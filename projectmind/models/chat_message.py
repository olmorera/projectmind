# projectmind/models/chat_message.py
from pydantic import BaseModel
from typing import Literal

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str
