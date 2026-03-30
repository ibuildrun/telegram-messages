"""Authentication frame for Telegram login."""
import customtkinter as ctk
from app.ui.theme import *


class AuthFrame(ctk.CTkFrame):
    """Handles Telegram API authentication."""

    def __init__(self, master, on_connected):
        super().__init__(master, fg_color=BG_DARK, corner_radius=0)
        self.on_connected = on_connected
        self.tg_client = None
        self._build_ui()

    def set_client(self, client):
        self.tg_client = client

    def _build_ui(self):
        # Center container
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Logo / Title
        ctk.CTkLabel(
            center, text="Telegram Message Saver",
            font=(FONT_FAMILY, 28, "bold"), text_color=ACCENT,
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            center, text="Save your important messages before it's too late",
            font=FONT_BODY, text_color=TEXT_SECONDARY,
        ).pack(pady=(0, 30))

        # Card
        card = ctk.CTkFrame(center, fg_color=BG_CARD, corner_radius=16, width=420)
        card.pack(padx=20)
        card.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=30, pady=30, fill="both", expand=True)

        ctk.CTkLabel(
            inner, text="Connect to Telegram",
            font=FONT_HEADING, text_color=TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 5))

        ctk.CTkLabel(
            inner, text="Get API credentials at my.telegram.org",
            font=FONT_SMALL, text_color=TEXT_SECONDARY,
        ).pack(anchor="w", pady=(0, 20))

        # API ID
        ctk.CTkLabel(inner, text="API ID", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(anchor="w")
        self.api_id_entry = ctk.CTkEntry(
            inner, height=INPUT_HEIGHT, fg_color=BG_INPUT,
            border_color=BORDER, text_color=TEXT_PRIMARY,
            placeholder_text="Enter your API ID", corner_radius=8,
        )
        self.api_id_entry.pack(fill="x", pady=(4, 12))

        # API Hash
        ctk.CTkLabel(inner, text="API Hash", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(anchor="w")
        self.api_hash_entry = ctk.CTkEntry(
            inner, height=INPUT_HEIGHT, fg_color=BG_INPUT,
            border_color=BORDER, text_color=TEXT_PRIMARY,
            placeholder_text="Enter your API Hash", corner_radius=8,
        )
        self.api_hash_entry.pack(fill="x", pady=(4, 12))

        # Phone
        ctk.CTkLabel(inner, text="Phone Number", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(anchor="w")
        self.phone_entry = ctk.CTkEntry(
            inner, height=INPUT_HEIGHT, fg_color=BG_INPUT,
            border_color=BORDER, text_color=TEXT_PRIMARY,
            placeholder_text="+7 999 123 4567", corner_radius=8,
        )
        self.phone_entry.pack(fill="x", pady=(4, 12))

        # Code entry (hidden initially)
        self.code_frame = ctk.CTkFrame(inner, fg_color="transparent")
        ctk.CTkLabel(self.code_frame, text="Verification Code", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(anchor="w")
        self.code_entry = ctk.CTkEntry(
            self.code_frame, height=INPUT_HEIGHT, fg_color=BG_INPUT,
            border_color=BORDER, text_color=TEXT_PRIMARY,
            placeholder_text="Code from Telegram", corner_radius=8,
        )
        self.code_entry.pack(fill="x", pady=(4, 12))

        # 2FA password (hidden initially)
        self.password_frame = ctk.CTkFrame(inner, fg_color="transparent")
        ctk.CTkLabel(self.password_frame, text="2FA Password", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(anchor="w")
        self.password_entry = ctk.CTkEntry(
            self.password_frame, height=INPUT_HEIGHT, fg_color=BG_INPUT,
            border_color=BORDER, text_color=TEXT_PRIMARY,
            placeholder_text="Your 2FA password", show="*", corner_radius=8,
        )
        self.password_entry.pack(fill="x", pady=(4, 12))

        # Status
        self.status_label = ctk.CTkLabel(
            inner, text="", font=FONT_SMALL, text_color=TEXT_SECONDARY,
        )
        self.status_label.pack(pady=(0, 10))

        # Connect button
        self.connect_btn = ctk.CTkButton(
            inner, text="Connect", height=BUTTON_HEIGHT,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            font=FONT_SUBHEADING, corner_radius=8,
            command=self._on_connect,
        )
        self.connect_btn.pack(fill="x", pady=(5, 0))

        self._state = "init"  # init -> code_sent -> need_2fa -> done

    def _set_status(self, text, color=TEXT_SECONDARY):
        self.status_label.configure(text=text, text_color=color)

    def _on_connect(self):
        import asyncio
        import threading

        if self._state == "init":
            api_id = self.api_id_entry.get().strip()
            api_hash = self.api_hash_entry.get().strip()
            phone = self.phone_entry.get().strip()

            if not api_id or not api_hash or not phone:
                self._set_status("Please fill in all fields", ERROR)
                return

            try:
                api_id = int(api_id)
            except ValueError:
                self._set_status("API ID must be a number", ERROR)
                return

            self._set_status("Connecting...", WARNING)
            self.connect_btn.configure(state="disabled")

            def do_connect():
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    authorized = loop.run_until_complete(self.tg_client.connect(api_id, api_hash))
                    if authorized:
                        self.after(0, self._auth_success)
                    else:
                        loop.run_until_complete(self.tg_client.send_code(phone))
                        self.after(0, self._show_code_entry)
                except Exception as e:
                    self.after(0, lambda: self._set_status(f"Error: {e}", ERROR))
                    self.after(0, lambda: self.connect_btn.configure(state="normal"))
                finally:
                    loop.close()

            threading.Thread(target=do_connect, daemon=True).start()

        elif self._state == "code_sent":
            code = self.code_entry.get().strip()
            if not code:
                self._set_status("Enter the code", ERROR)
                return

            self._set_status("Verifying...", WARNING)
            self.connect_btn.configure(state="disabled")

            def do_signin():
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.tg_client.sign_in(code))
                    self.after(0, self._auth_success)
                except Exception as e:
                    if "2FA" in str(type(e).__name__) or "password" in str(e).lower() or "SessionPasswordNeeded" in str(type(e).__name__):
                        self.after(0, self._show_2fa_entry)
                    else:
                        self.after(0, lambda: self._set_status(f"Error: {e}", ERROR))
                        self.after(0, lambda: self.connect_btn.configure(state="normal"))
                finally:
                    loop.close()

            threading.Thread(target=do_signin, daemon=True).start()

        elif self._state == "need_2fa":
            password = self.password_entry.get().strip()
            if not password:
                self._set_status("Enter your 2FA password", ERROR)
                return

            self._set_status("Verifying 2FA...", WARNING)
            self.connect_btn.configure(state="disabled")

            def do_2fa():
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.tg_client.sign_in("", password=password))
                    self.after(0, self._auth_success)
                except Exception as e:
                    self.after(0, lambda: self._set_status(f"Error: {e}", ERROR))
                    self.after(0, lambda: self.connect_btn.configure(state="normal"))
                finally:
                    loop.close()

            threading.Thread(target=do_2fa, daemon=True).start()

    def _show_code_entry(self):
        self._state = "code_sent"
        self.code_frame.pack(fill="x", before=self.status_label)
        self.connect_btn.configure(text="Verify Code", state="normal")
        self._set_status("Code sent to your Telegram", SUCCESS)

    def _show_2fa_entry(self):
        self._state = "need_2fa"
        self.password_frame.pack(fill="x", before=self.status_label)
        self.connect_btn.configure(text="Verify 2FA", state="normal")
        self._set_status("2FA password required", WARNING)

    def _auth_success(self):
        self._state = "done"
        self._set_status("Connected!", SUCCESS)
        self.on_connected()
