"""Main application window."""
import customtkinter as ctk

from app.ui.theme import *
from app.ui.auth_frame import AuthFrame
from app.ui.chats_frame import ChatsFrame
from app.ui.messages_frame import MessagesFrame
from app.ui.export_frame import ExportDialog
from app.telegram_client import TgClient

import asyncio
import threading


class App(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Telegram Message Saver")
        self.geometry("1100x750")
        self.minsize(900, 600)
        self.configure(fg_color=BG_DARK)

        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Telegram client
        self.tg_client = TgClient()

        # Frames container
        self.container = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        self.container.pack(fill="both", expand=True)

        # Navigation sidebar
        self.sidebar = ctk.CTkFrame(self.container, fg_color=BG_SIDEBAR, width=SIDEBAR_WIDTH, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()
        self.sidebar.pack_forget()  # Hidden until authenticated

        # Main content area
        self.content = ctk.CTkFrame(self.container, fg_color=BG_DARK, corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)

        # Create frames
        self.auth_frame = AuthFrame(self.content, on_connected=self._on_authenticated)
        self.auth_frame.set_client(self.tg_client)

        self.chats_frame = ChatsFrame(self.content, on_chat_selected=self._on_chat_selected)
        self.messages_frame = MessagesFrame(
            self.content, self.tg_client,
            on_back=self._show_chats,
            on_export=self._show_export,
        )

        # Show auth first
        self._current_frame = None
        self._show_frame(self.auth_frame)

        # Cleanup on close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_sidebar(self):
        # Brand
        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=15, pady=(20, 25))

        ctk.CTkLabel(
            brand, text="TG Saver",
            font=(FONT_FAMILY, 18, "bold"), text_color=ACCENT,
        ).pack(anchor="w")
        ctk.CTkLabel(
            brand, text="Message Backup Tool",
            font=FONT_SMALL, text_color=TEXT_MUTED,
        ).pack(anchor="w")

        # Separator
        ctk.CTkFrame(self.sidebar, fg_color=BORDER, height=1).pack(fill="x", padx=15, pady=(0, 15))

        # Nav buttons
        self.nav_chats_btn = ctk.CTkButton(
            self.sidebar, text="  Chats", height=42,
            fg_color="transparent", hover_color=BG_CARD,
            text_color=TEXT_PRIMARY, font=FONT_BODY,
            anchor="w", corner_radius=8,
            command=self._show_chats,
        )
        self.nav_chats_btn.pack(fill="x", padx=10, pady=2)

        # Spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="both", expand=True)

        # Bottom info
        ctk.CTkFrame(self.sidebar, fg_color=BORDER, height=1).pack(fill="x", padx=15, pady=(15, 10))

        self.user_label = ctk.CTkLabel(
            self.sidebar, text="Not connected",
            font=FONT_SMALL, text_color=TEXT_MUTED,
        )
        self.user_label.pack(padx=15, pady=(0, 5))

        ctk.CTkButton(
            self.sidebar, text="Disconnect", height=32,
            fg_color=BG_CARD, hover_color=ERROR,
            text_color=TEXT_SECONDARY, font=FONT_SMALL,
            corner_radius=6, command=self._on_disconnect,
        ).pack(fill="x", padx=15, pady=(0, 20))

    def _show_frame(self, frame):
        if self._current_frame:
            self._current_frame.pack_forget()
        self._current_frame = frame
        frame.pack(fill="both", expand=True)

    def _on_authenticated(self):
        """Called when user successfully logs in."""
        self.sidebar.pack(side="left", fill="y", before=self.content)
        self._show_chats()
        self._load_chats()

        # Update user label
        def get_me():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                me = loop.run_until_complete(self.tg_client.client.get_me())
                name = f"{me.first_name or ''} {me.last_name or ''}".strip()
                self.after(0, lambda: self.user_label.configure(text=f"Logged in as {name}", text_color=SUCCESS))
            except:
                pass
            finally:
                loop.close()
        threading.Thread(target=get_me, daemon=True).start()

    def _load_chats(self):
        """Load chats list in background."""
        def fetch():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                chats = loop.run_until_complete(self.tg_client.get_dialogs())
                self.after(0, lambda: self.chats_frame.set_chats(chats))
            except Exception as e:
                print(f"Error loading chats: {e}")
            finally:
                loop.close()
        threading.Thread(target=fetch, daemon=True).start()

    def _show_chats(self):
        self._show_frame(self.chats_frame)
        self.nav_chats_btn.configure(fg_color=ACCENT_DIM)

    def _on_chat_selected(self, chat):
        self.nav_chats_btn.configure(fg_color="transparent")
        self._show_frame(self.messages_frame)
        self.messages_frame.load_chat(chat)

    def _show_export(self, messages, chat_title):
        ExportDialog(self, messages, chat_title)

    def _on_disconnect(self):
        def dc():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.tg_client.disconnect())
            except:
                pass
            finally:
                loop.close()
            self.after(0, self._reset_to_auth)
        threading.Thread(target=dc, daemon=True).start()

    def _reset_to_auth(self):
        self.sidebar.pack_forget()
        self.tg_client = TgClient()
        self.auth_frame.set_client(self.tg_client)
        self.auth_frame._state = "init"
        self._show_frame(self.auth_frame)

    def _on_close(self):
        def cleanup():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.tg_client.disconnect())
            except:
                pass
            finally:
                loop.close()
            self.after(0, self.destroy)
        threading.Thread(target=cleanup, daemon=True).start()
