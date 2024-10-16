from pydantic import BaseModel

class FriendRequestCreate(BaseModel):
    receiver_id: int

class PrivacySettingsUpdate(BaseModel):
    friends_list_privacy: str
    friend_requests_privacy: str