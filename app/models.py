"""Data models for the application."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class MessageData:
    """Represents a single Telegram message."""
    id: int
    date: datetime
    sender_id: Optional[int]
    sender_name: str
    text: str
    media_type: Optional[str] = None
    reply_to_id: Optional[int] = None
    views: Optional[int] = None
    forwards: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "sender_id": self.sender_id,
            "sender_name": self.sender_name,
            "text": self.text,
            "media_type": self.media_type,
            "reply_to_id": self.reply_to_id,
            "views": self.views,
            "forwards": self.forwards,
        }


@dataclass
class ChatData:
    """Represents a Telegram chat/dialog."""
    id: int
    title: str
    chat_type: str  # "user", "group", "supergroup", "channel"
    members_count: Optional[int] = None
    unread_count: int = 0
    last_message: Optional[str] = None
    last_date: Optional[datetime] = None


@dataclass
class SenderInfo:
    """Represents a message sender in a chat."""
    id: int
    name: str
    message_count: int = 0
