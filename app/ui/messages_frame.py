"""Messages viewer frame with sender filtering and export."""
import customtkinter as ctk
import threading
import asyncio
from datetime import datetime
from typing import Optional

from app.ui.theme import *
from app.models import ChatData, MessageData, SenderInfo


class MessageBubble(ctk.CTkFrame):
    """Single message display."""

    def __init__(self, master, msg: MessageData):
        super().__init__(master, fg_color=BG_CARD, corner_radius=10)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=10)

        # Header row
        header = ctk.CTkFrame(inner, fg_color="transparent")
        header.pack(fill="x")

        ctk.CTkLabel(
            header, text=msg.sender_name,
            font=(FONT_FAMILY, 12, "bold"), text_color=ACCENT, anchor="w",
        ).pack(side="left")

        ctk.CTkLabel(
            header, text=msg.date.strftime("%Y-%m-%d %H:%M"),
            font=FONT_SMALL, text_color=TEXT_MUTED, anchor="e",
        ).pack(side="right")

        # Text
        if msg.text:
            text_label = ctk.CTkLabel(
                inner, text=msg.text, font=FONT_BODY,
                text_color=TEXT_PRIMARY, anchor="w", justify="left",
                wraplength=600,
            )
            text_label.pack(fill="x", pady=(4, 0))

        # Media indicator
        if msg.media_type:
            ctk.CTkLabel(
                inner, text=f"[{msg.media_type}]",
                font=FONT_SMALL, text_color=WARNING, anchor="w",
            ).pack(fill="x", pady=(2, 0))


class MessagesFrame(ctk.CTkFrame):
    """Shows messages for a selected chat with filtering and export."""

    def __init__(self, master, tg_client, on_back, on_export):
        super().__init__(master, fg_color=BG_DARK, corner_radius=0)
        self.tg_client = tg_client
        self.on_back = on_back
        self.on_export = on_export
        self.current_chat: Optional[ChatData] = None
        self.all_messages: list[MessageData] = []
        self.senders: list[SenderInfo] = []
        self._build_ui()

    def _build_ui(self):
        # Top bar
        top = ctk.CTkFrame(self, fg_color=BG_CARD, height=60, corner_radius=0)
        top.pack(fill="x")
        top.pack_propagate(False)

        self.back_btn = ctk.CTkButton(
            top, text="< Back", width=80, height=35,
            fg_color="transparent", hover_color=BG_CARD_HOVER,
            text_color=ACCENT, font=FONT_BODY, corner_radius=8,
            command=self.on_back,
        )
        self.back_btn.pack(side="left", padx=10)

        self.title_label = ctk.CTkLabel(top, text="", font=FONT_HEADING, text_color=TEXT_PRIMARY)
        self.title_label.pack(side="left", padx=10)

        self.msg_count_label = ctk.CTkLabel(top, text="", font=FONT_BODY, text_color=TEXT_SECONDARY)
        self.msg_count_label.pack(side="left", padx=5)

        # Export button
        self.export_btn = ctk.CTkButton(
            top, text="Export", width=100, height=35,
            fg_color=SUCCESS, hover_color="#66bb6a",
            font=FONT_SUBHEADING, corner_radius=8,
            command=self._do_export,
        )
        self.export_btn.pack(side="right", padx=10)

        # Filters bar
        filters = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, height=50)
        filters.pack(fill="x", padx=0, pady=0)
        filters.pack_propagate(False)

        filter_inner = ctk.CTkFrame(filters, fg_color="transparent")
        filter_inner.pack(fill="x", padx=15, pady=8)

        ctk.CTkLabel(filter_inner, text="Sender:", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(side="left", padx=(0, 5))
        self.sender_var = ctk.StringVar(value="All senders")
        self.sender_menu = ctk.CTkOptionMenu(
            filter_inner, variable=self.sender_var,
            values=["All senders"], width=250,
            fg_color=BG_INPUT, button_color=ACCENT,
            button_hover_color=ACCENT_HOVER,
            dropdown_fg_color=BG_CARD,
            text_color=TEXT_PRIMARY,
            command=self._on_sender_filter,
        )
        self.sender_menu.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(filter_inner, text="Search:", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(side="left", padx=(0, 5))
        self.search_entry = ctk.CTkEntry(
            filter_inner, width=200, height=32, fg_color=BG_INPUT,
            border_color=BORDER, text_color=TEXT_PRIMARY,
            placeholder_text="Filter messages...", corner_radius=6,
        )
        self.search_entry.pack(side="left", padx=(0, 15))
        self.search_entry.bind("<KeyRelease>", lambda e: self._apply_filters())

        # Loading indicator
        self.loading_label = ctk.CTkLabel(self, text="", font=FONT_BODY, text_color=WARNING)
        self.loading_label.pack(pady=5)

        # Progress bar
        self.progress = ctk.CTkProgressBar(self, fg_color=BG_CARD, progress_color=ACCENT, height=3, width=400)
        self.progress.set(0)

        # Messages scroll area
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=15, pady=(5, 15))

    def load_chat(self, chat: ChatData):
        """Load messages for a chat."""
        self.current_chat = chat
        self.title_label.configure(text=chat.title)
        self.msg_count_label.configure(text="")
        self.loading_label.configure(text="Loading messages...")
        self.progress.pack(pady=(0, 5))
        self.progress.set(0)

        # Clear messages
        for w in self.scroll.winfo_children():
            w.destroy()

        def fetch():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # Get senders first
                senders = loop.run_until_complete(self.tg_client.get_chat_senders(chat.id, limit=3000))
                self.senders = senders

                sender_names = ["All senders"] + [f"{s.name} ({s.message_count})" for s in senders]
                self.after(0, lambda: self.sender_menu.configure(values=sender_names))
                self.after(0, lambda: self.sender_var.set("All senders"))

                # Get all messages
                def progress_cb(count):
                    self.after(0, lambda c=count: self.loading_label.configure(text=f"Loading... {c} messages"))

                messages = loop.run_until_complete(
                    self.tg_client.get_messages(chat.id, progress_cb=progress_cb)
                )
                self.all_messages = messages
                self.after(0, lambda: self._display_messages(messages))
                self.after(0, lambda: self.loading_label.configure(text=""))
                self.after(0, lambda: self.progress.pack_forget())
                self.after(0, lambda: self.msg_count_label.configure(text=f"{len(messages)} messages"))
            except Exception as e:
                self.after(0, lambda: self.loading_label.configure(text=f"Error: {e}"))
            finally:
                loop.close()

        threading.Thread(target=fetch, daemon=True).start()

    def _on_sender_filter(self, value):
        self._apply_filters()

    def _apply_filters(self):
        sender_val = self.sender_var.get()
        search = self.search_entry.get().strip().lower()

        filtered = self.all_messages

        # Filter by sender
        if sender_val != "All senders":
            sender_name = sender_val.rsplit(" (", 1)[0]
            filtered = [m for m in filtered if m.sender_name == sender_name]

        # Filter by search
        if search:
            filtered = [m for m in filtered if search in (m.text or "").lower()]

        self._display_messages(filtered)
        self.msg_count_label.configure(text=f"{len(filtered)} messages")

    def _display_messages(self, messages: list[MessageData]):
        for w in self.scroll.winfo_children():
            w.destroy()

        if not messages:
            ctk.CTkLabel(self.scroll, text="No messages found", font=FONT_BODY, text_color=TEXT_MUTED).pack(pady=40)
            return

        # Show max 500 in UI to prevent lag, all are exported
        display = messages[-500:] if len(messages) > 500 else messages
        if len(messages) > 500:
            ctk.CTkLabel(
                self.scroll,
                text=f"Showing last 500 of {len(messages)} messages. All messages will be included in export.",
                font=FONT_SMALL, text_color=WARNING,
            ).pack(pady=(0, 10))

        for msg in display:
            bubble = MessageBubble(self.scroll, msg)
            bubble.pack(fill="x", pady=2)

    def _do_export(self):
        """Trigger export with current filters applied."""
        sender_val = self.sender_var.get()
        search = self.search_entry.get().strip().lower()

        messages = self.all_messages
        if sender_val != "All senders":
            sender_name = sender_val.rsplit(" (", 1)[0]
            messages = [m for m in messages if m.sender_name == sender_name]
        if search:
            messages = [m for m in messages if search in (m.text or "").lower()]

        self.on_export(messages, self.current_chat.title if self.current_chat else "Chat")

    def get_filtered_messages(self) -> list[MessageData]:
        """Return currently filtered messages."""
        sender_val = self.sender_var.get()
        search = self.search_entry.get().strip().lower()
        messages = self.all_messages
        if sender_val != "All senders":
            sender_name = sender_val.rsplit(" (", 1)[0]
            messages = [m for m in messages if m.sender_name == sender_name]
        if search:
            messages = [m for m in messages if search in (m.text or "").lower()]
        return messages
