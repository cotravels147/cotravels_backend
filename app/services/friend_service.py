from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import or_, and_
from app.models.user import User
from app.models.friend_request import FriendRequest, FriendRequestStatus
from app.models.friend import Friend
from app.models.notification import Notification, NotificationType
from app.services.notification_service import create_notification
from typing import List
from datetime import datetime

async def send_friend_request(db: Session, sender_id: int, receiver_id: int):
    if sender_id == receiver_id:
        raise HTTPException(status_code=400, detail="You cannot send a friend request to yourself")

    sender = db.query(User).filter(User.id == sender_id).first()
    receiver = db.query(User).filter(User.id == receiver_id).first()

    if not receiver:
        raise HTTPException(status_code=404, detail="User not found")

    if receiver.privacy_friend_requests == 'none':
        raise HTTPException(status_code=400, detail="This user is not accepting friend requests")

    if receiver.privacy_friend_requests == 'friends_of_friends':
        common_friends = set(sender.friends).intersection(set(receiver.friends))
        if not common_friends:
            raise HTTPException(status_code=400, detail="You can only send friend requests to friends of friends")

    if receiver in sender.blocked_users or sender in receiver.blocked_users:
        raise HTTPException(status_code=400, detail="Cannot send friend request to blocked user")

    existing_request = db.query(FriendRequest).filter(
        or_(
            and_(FriendRequest.sender_id == sender_id, FriendRequest.receiver_id == receiver_id),
            and_(FriendRequest.sender_id == receiver_id, FriendRequest.receiver_id == sender_id)
        )
    ).first()

    if existing_request:
        raise HTTPException(status_code=400, detail="A friend request already exists between these users")

    existing_friendship = db.query(Friend).filter(
        or_(
            and_(Friend.user_id == sender_id, Friend.friend_id == receiver_id),
            and_(Friend.user_id == receiver_id, Friend.friend_id == sender_id)
        )
    ).first()

    if existing_friendship:
        raise HTTPException(status_code=400, detail="You are already friends with this user")

    new_request = FriendRequest(sender_id=sender_id, receiver_id=receiver_id)
    db.add(new_request)

    # Create notification for receiver
    create_notification(db, receiver_id, NotificationType.friend_request, f"{sender.username} sent you a friend request")
    db.commit()
    return {"message": "Friend request sent successfully"}

async def accept_friend_request(db: Session, current_user_id: int, request_id: int):
    friend_request = db.query(FriendRequest).filter(FriendRequest.id == request_id, FriendRequest.receiver_id == current_user_id).first()
    if not friend_request:
        raise HTTPException(status_code=404, detail="Friend request not found")

    if friend_request.status != FriendRequestStatus.pending:
        raise HTTPException(status_code=400, detail="This friend request has already been processed")

    friend_request.status = FriendRequestStatus.accepted
    
    new_friendship1 = Friend(user_id=current_user_id, friend_id=friend_request.sender_id)
    new_friendship2 = Friend(user_id=friend_request.sender_id, friend_id=current_user_id)
    db.add(new_friendship1)
    db.add(new_friendship2)

    # create notification on sender's profile that request is accepted
    create_notification(db, friend_request.sender_id, NotificationType.friend_accept, f"{friend_request.receiver.username} accepted your friend request")

    db.commit()
    return {"message": "Friend request accepted"}

async def reject_friend_request(db: Session, current_user_id: int, request_id: int):
    friend_request = db.query(FriendRequest).filter(FriendRequest.id == request_id, FriendRequest.receiver_id == current_user_id).first()
    if not friend_request:
        raise HTTPException(status_code=404, detail="Friend request not found")

    if friend_request.status != FriendRequestStatus.pending:
        raise HTTPException(status_code=400, detail="This friend request has already been processed")

    friend_request.status = FriendRequestStatus.rejected
    db.commit()
    return {"message": "Friend request rejected"}
 
async def get_friends_list(db: Session, user_id: int, current_user_id: int) -> List[dict]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.privacy_friends_list == 'private' and user_id != current_user_id:
        raise HTTPException(status_code=403, detail="You don't have permission to view this user's friends list")

    if user.privacy_friends_list == 'friends' and user_id != current_user_id:
        friendship = db.query(Friend).filter(
            or_(
                and_(Friend.user_id == current_user_id, Friend.friend_id == user_id),
                and_(Friend.user_id == user_id, Friend.friend_id == current_user_id)
            )
        ).first()
        if not friendship:
            raise HTTPException(status_code=403, detail="You don't have permission to view this user's friends list")

    friends = db.query(User).join(Friend, Friend.friend_id == User.id).filter(Friend.user_id == user_id).all()
    return [{"id": friend.id, "username": friend.username, "name": friend.name} for friend in friends]

async def get_friend_suggestions(db: Session, user_id: int) -> List[dict]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    friends_ids = [friend.friend_id for friend in user.friends]
    blocked_ids = [blocked.id for blocked in user.blocked_users]

    # Get friends of friends
    friends_of_friends = db.query(User).join(Friend, User.id == Friend.friend_id).filter(
        Friend.user_id.in_(friends_ids),
        User.id.notin_([user_id] + friends_ids + blocked_ids)
    ).distinct()

    # Get users with similar travel preferences
    similar_travelers = db.query(User).filter(
        User.id.notin_([user_id] + friends_ids + blocked_ids),
        User.travel_preferences.overlap(user.travel_preferences)
    )

    # Combine and sort suggestions
    suggestions = list(set(list(friends_of_friends) + list(similar_travelers)))
    suggestions.sort(key=lambda x: (x in friends_of_friends, len(set(x.travel_preferences) & set(user.travel_preferences))), reverse=True)

    return [{"id": suggestion.id, "username": suggestion.username, "name": suggestion.name} for suggestion in suggestions[:10]]

async def remove_friend(db: Session, current_user_id: int, friend_id: int):
    friendship1 = db.query(Friend).filter(
        (Friend.user_id == current_user_id) & (Friend.friend_id == friend_id)
    ).first()
    friendship2 = db.query(Friend).filter(
        (Friend.user_id == friend_id) & (Friend.friend_id == current_user_id)
    ).first()

    if not friendship1 or not friendship2:
        raise HTTPException(status_code=404, detail="Friend connection not found")

    db.delete(friendship1)
    db.delete(friendship2)
    db.commit()
    return {"message": "Friend removed successfully"}

async def block_user(db: Session, current_user_id: int, user_id_to_block: int):
    if current_user_id == user_id_to_block:
        raise HTTPException(status_code=400, detail="You cannot block yourself")

    user = db.query(User).filter(User.id == current_user_id).first()
    user_to_block = db.query(User).filter(User.id == user_id_to_block).first()

    if not user_to_block:
        raise HTTPException(status_code=404, detail="User not found")

    if user_to_block in user.blocked_users:
        raise HTTPException(status_code=400, detail="User is already blocked")

    user.blocked_users.append(user_to_block)

    # Remove any existing friend connection
    friendship1 = db.query(Friend).filter(
        (Friend.user_id == current_user_id) & (Friend.friend_id == user_id_to_block)
    ).first()
    friendship2 = db.query(Friend).filter(
        (Friend.user_id == user_id_to_block) & (Friend.friend_id == current_user_id)
    ).first()

    if friendship1:
        db.delete(friendship1)
    if friendship2:
        db.delete(friendship2)

    # Remove any existing friend requests
    db.query(FriendRequest).filter(
        or_(
            and_(FriendRequest.sender_id == current_user_id, FriendRequest.receiver_id == user_id_to_block),
            and_(FriendRequest.sender_id == user_id_to_block, FriendRequest.receiver_id == current_user_id)
        )
    ).delete()

    db.commit()
    return {"message": "User blocked successfully"}

async def unblock_user(db: Session, current_user_id: int, user_id_to_unblock: int):
    user = db.query(User).filter(User.id == current_user_id).first()
    user_to_unblock = db.query(User).filter(User.id == user_id_to_unblock).first()

    if not user_to_unblock:
        raise HTTPException(status_code=404, detail="User not found")

    if user_to_unblock not in user.blocked_users:
        raise HTTPException(status_code=400, detail="User is not blocked")

    user.blocked_users.remove(user_to_unblock)
    db.commit()
    return {"message": "User unblocked successfully"}

async def update_privacy_settings(db: Session, user_id: int, friends_list_privacy: str, friend_requests_privacy: str):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if friends_list_privacy not in ['public', 'friends', 'private']:
        raise HTTPException(status_code=400, detail="Invalid friends list privacy setting")

    if friend_requests_privacy not in ['everyone', 'friends_of_friends', 'none']:
        raise HTTPException(status_code=400, detail="Invalid friend requests privacy setting")

    user.privacy_friends_list = friends_list_privacy
    user.privacy_friend_requests = friend_requests_privacy
    db.commit()
    return {"message": "Privacy settings updated successfully"}