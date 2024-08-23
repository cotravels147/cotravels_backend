from pydantic import BaseModel

class SessionRequest(BaseModel):
    user_id: str
    token: str