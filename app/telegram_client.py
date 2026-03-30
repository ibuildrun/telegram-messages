"""Telegram client wrapper using Telethon."""
import asyncio
import os
from datetime import datetime
from typing import Optional, Callable

from telethon import TelegramClient
from telethon.tl.types import (
    User, Chat, Channel,
    MessageMediaPhoto, MessageMediaDocument,
    MessageMediaWebPage, MessageMediaGeo,
    PeerUser, PeerChat, PeerChannel,
)
from telethon.errors import SessionPasswordNeededError

from app.models import MessageData, ChatData, SenderInfo


class TgClient:
    """Async Telegram client wrapper."""

    def __init__(self):
        self.client: Optional[TelegramClient] = None
        self.api_id: Optional[int] = None
        self.api_hash: Optional[str] = None
        self._phone: Optional[str] = None
        self._phone_code_hash: Optional[str] = None

    async def connect(self, api_id: int, api_hash: str) -> bool:
        """Initialize and connect the client."""
        self.api_id = api_id
        self.api_hash = api_hash
        session_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tg_session")
        self.client = TelegramClient(session_path, api_id, api_hash)
        await self.client.connect()
        return await self.client.is_user_authorized()

    async def send_code(self, phone: str):
        """Send verification code to phone."""
        self._phone = phone
        result = await self.client.send_code_request(phone)
        self._phone_code_hash = result.phone_code_hash

    async def sign_in(self, code: str, password: Optional[str] = None) -> bool:
        """Sign in with code or 2FA password."""
        try:
            await self.client.sign_in(self._phone, code, phone_code_hash=self._phone_code_hash)
            return True
        except SessionPasswordNeededError:
            if password:
                await self.client.sign_in(password=password)
                return True
            raise

    async def get_dialogs(self) -> list[ChatData]:
        """Get all dialogs/chats."""
        dialogs = await self.client.get_dialogs()
        chats = []
        for d in dialogs:
            entity = d.entity
            if isinstance(entity, User):
                chat_type = "user"
                title = f"{entity.first_name or ''} {entity.last_name or ''}".strip()
                members = None
            elif isinstance(entity, Chat):
                chat_type = "group"
                title = entity.title
                members = entity.participants_count
            elif isinstance(entity, Channel):
                chat_type = "supergroup" if entity.megagroup else "channel"
                title = entity.title
                members = entity.participants_count
            else:
                continue

            last_msg = ""
            if d.message and d.message.text:
                last_msg = d.message.text[:100]

            chats.append(ChatData(
                id=d.id,
                title=title or "Unknown",
                chat_type=chat_type,
                members_count=members,
                unread_count=d.unread_count,
                last_message=last_msg,
                last_date=d.date,
            ))
        return chats

    async def get_chat_senders(self, chat_id: int, limit: int = 2000) -> list[SenderInfo]:
        """Get unique senders in a chat by scanning messages."""
        senders = {}
        async for msg in self.client.iter_messages(chat_id, limit=limit):
            if msg.sender:
                sid = msg.sender_id
                if sid not in senders:
                    name = self._get_sender_name(msg.sender)
                    senders[sid] = SenderInfo(id=sid, name=name, message_count=0)
                senders[sid].message_count += 1
        result = list(senders.values())
        result.sort(key=lambda s: s.message_count, reverse=True)
        return result

    async def get_messages(
        self,
        chat_id: int,
        sender_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        search: Optional[str] = None,
        limit: int = 0,
        progress_cb: Optional[Callable[[int], None]] = None,
    ) -> list[MessageData]:
        """Fetch messages from a chat with optional filters."""
        messages = []
        kwargs = {"limit": limit if limit > 0 else None}
        if search:
            kwargs["search"] = search
        if date_to:
            kwargs["offset_date"] = date_to

        count = 0
        async for msg in self.client.iter_messages(chat_id, **kwargs):
            if date_from and msg.date.replace(tzinfo=None) < date_from:
                break

            if sender_id and msg.sender_id != sender_id:
                continue

            sender_name = ""
            if msg.sender:
                sender_name = self._get_sender_name(msg.sender)

            media_type = None
            if msg.media:
                if isinstance(msg.media, MessageMediaPhoto):
                    media_type = "photo"
                elif isinstance(msg.media, MessageMediaDocument):
                    media_type = "document"
                elif isinstance(msg.media, MessageMediaWebPage):
                    media_type = "webpage"
                elif isinstance(msg.media, MessageMediaGeo):
                    media_type = "geo"
                else:
                    media_type = "other"

            messages.append(MessageData(
                id=msg.id,
                date=msg.date.replace(tzinfo=None),
                sender_id=msg.sender_id,
                sender_name=sender_name,
                text=msg.text or "",
                media_type=media_type,
                reply_to_id=msg.reply_to.reply_to_msg_id if msg.reply_to else None,
                views=msg.views,
                forwards=msg.forwards,
            ))

            count += 1
            if progress_cb and count % 100 == 0:
                progress_cb(count)

        if progress_cb:
            progress_cb(count)

        messages.reverse()
        return messages

    async def disconnect(self):
        """Disconnect the client."""
        if self.client:
            await self.client.disconnect()

    @staticmethod
    def _get_sender_name(sender) -> str:
        if isinstance(sender, User):
            parts = [sender.first_name or "", sender.last_name or ""]
            return " ".join(p for p in parts if p) or f"User#{sender.id}"
        elif isinstance(sender, (Chat, Channel)):
            return sender.title or f"Chat#{sender.id}"
        return f"Unknown#{getattr(sender, 'id', '?')}"
