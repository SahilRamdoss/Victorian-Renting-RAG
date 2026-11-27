from pydantic import BaseModel

class UserQuery(BaseModel):
    query: str

class ChatbotResponse(BaseModel):
    response: str
    sources: set[str]