"""Chats list frame."""
import customtkinter as ctk
from app.ui.theme import *
from app.models import ChatData


CHAT_TYPE_ICONS = {
    "user": "\U0001F464",
    "group": "\U0001F465",
    "supergroup": "\U0001F30D",
    "channel": "\U0001F4E2",
}

CHAT_TYPE_COLORS = {
    "user": "#4fc3f7",
    "group": "#81c784",
    "supergroup": "#7c8cf8",
    "channel": "#ffb74d",
}


class ChatCard(ctk.CTkFrame):
    """Single chat card widget."""

    def __init__(self, master, chat: ChatData, on_click):
        super().__init__(master, fg_color=BG_CARD, corner_radius=CORNER_RADIUS, height=72)
        self.pack_propagate(False)
        self.chat = chat
        self.on_click = on_click
        self._build()

        self.bind("<Button-1>", lambda e: self.on_click(self.chat))
        for child in self.winfo_children():
            child.bind("<Button-1>", lambda e: self.on_click(self.chat))
            for grandchild in child.winfo_children():
                grandchild.bind("<Button-1>", lambda e: self.on_click(self.chat))

        self.bind("<Enter>", lambda e: self.configure(fg_color=BG_CARD_HOVER))
        self.bind("<Leave>", lambda e: self.configure(fg_color=BG_CARD))

    def _build(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=12)

        # Type badge
        type_color = CHAT_TYPE_COLORS.get(self.chat.chat_type, ACCENT)
        badge = ctk.CTkFrame(row, fg_color=type_color, width=40, height=40, corner_radius=20)
        badge.pack(side="left", padx=(0, 12))
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text=self.chat.chat_type[0].upper(), font=(FONT_FAMILY, 16, "bold"), text_color="#fff").place(relx=0.5, rely=0.5, anchor="center")

        # Info
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)

        title_text = self.chat.title
        if len(title_text) > 35:
            title_text = title_text[:35] + "..."
        ctk.CTkLabel(info, text=title_text, font=FONT_SUBHEADING, text_color=TEXT_PRIMARY, anchor="w").pack(fill="x")

        meta_parts = [self.chat.chat_type]
        if self.chat.members_count:
            meta_parts.append(f"{self.chat.members_count} members")
        ctk.CTkLabel(info, text=" · ".join(meta_parts), font=FONT_SMALL, text_color=TEXT_MUTED, anchor="w").pack(fill="x")

        # Unread badge
        if self.chat.unread_count > 0:
            unread = ctk.CTkFrame(row, fg_color=ACCENT, width=28, height=28, corner_radius=14)
            unread.pack(side="right")
            unread.pack_propagate(False)
            ctk.CTkLabel(unread, text=str(self.chat.unread_count), font=FONT_SMALL, text_color="#fff").place(relx=0.5, rely=0.5, anchor="center")


class ChatsFrame(ctk.CTkFrame):
    """Shows list of all Telegram chats."""

    def __init__(self, master, on_chat_selected):
        super().__init__(master, fg_color=BG_DARK, corner_radius=0)
        self.on_chat_selected = on_chat_selected
        self.all_chats: list[ChatData] = []
        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.pack(fill="x", padx=20, pady=(20, 10))
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="Your Chats", font=FONT_TITLE, text_color=TEXT_PRIMARY).pack(side="left")

        self.chat_count_label = ctk.CTkLabel(header, text="", font=FONT_BODY, text_color=TEXT_SECONDARY)
        self.chat_count_label.pack(side="right")

        # Search
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.search_entry = ctk.CTkEntry(
            search_frame, height=40, fg_color=BG_INPUT,
            border_color=BORDER, text_color=TEXT_PRIMARY,
            placeholder_text="Search chats...", corner_radius=8,
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self._filter_chats())

        # Type filter
        self.type_var = ctk.StringVar(value="All")
        self.type_menu = ctk.CTkSegmentedButton(
            search_frame, values=["All", "Groups", "Users", "Channels"],
            variable=self.type_var, command=lambda v: self._filter_chats(),
            fg_color=BG_INPUT, selected_color=ACCENT,
            selected_hover_color=ACCENT_HOVER, unselected_color=BG_CARD,
            text_color=TEXT_PRIMARY,
        )
        self.type_menu.pack(side="right")

        # Status
        self.status = ctk.CTkLabel(self, text="Loading chats...", font=FONT_BODY, text_color=TEXT_SECONDARY)
        self.status.pack(pady=10)

        # Scrollable list
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def set_chats(self, chats: list[ChatData]):
        self.all_chats = chats
        self.status.pack_forget()
        self.chat_count_label.configure(text=f"{len(chats)} chats")
        self._render_chats(chats)

    def _filter_chats(self):
        query = self.search_entry.get().strip().lower()
        type_filter = self.type_var.get()

        filtered = self.all_chats
        if query:
            filtered = [c for c in filtered if query in c.title.lower()]
        if type_filter == "Groups":
            filtered = [c for c in filtered if c.chat_type in ("group", "supergroup")]
        elif type_filter == "Users":
            filtered = [c for c in filtered if c.chat_type == "user"]
        elif type_filter == "Channels":
            filtered = [c for c in filtered if c.chat_type == "channel"]

        self._render_chats(filtered)

    def _render_chats(self, chats: list[ChatData]):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        if not chats:
            ctk.CTkLabel(self.scroll, text="No chats found", font=FONT_BODY, text_color=TEXT_MUTED).pack(pady=40)
            return

        for chat in chats:
            card = ChatCard(self.scroll, chat, self.on_chat_selected)
            card.pack(fill="x", pady=3)
