from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient('mongodb://localhost:27017')
db = client.your_database_name
messages_collection = db.messages

class Message:
    @staticmethod
    async def create_message(chat_id, chat_type, sender_id, content, sent_at, edited_at=None):
        message = {
            "chat_id": chat_id,
            "chat_type": chat_type,
            "sender_id": sender_id,
            "content": content,
            "sent_at": sent_at,
            "edited_at": edited_at
        }
        result = await messages_collection.insert_one(message)
        return result.inserted_id