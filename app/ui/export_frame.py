"""Export dialog for choosing format and saving messages."""
import customtkinter as ctk
import os
import threading
from tkinter import filedialog
from datetime import datetime

from app.ui.theme import *
from app.models import MessageData
from app.exporter import Exporter


class ExportDialog(ctk.CTkToplevel):
    """Export dialog window."""

    def __init__(self, master, messages: list[MessageData], chat_title: str):
        super().__init__(master)
        self.messages = messages
        self.chat_title = chat_title

        self.title("Export Messages")
        self.geometry("480x520")
        self.configure(fg_color=BG_DARK)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - 480) // 2
        y = master.winfo_y() + (master.winfo_height() - 520) // 2
        self.geometry(f"+{x}+{y}")

        self._build_ui()

    def _build_ui(self):
        # Header
        ctk.CTkLabel(
            self, text="Export Messages",
            font=FONT_TITLE, text_color=TEXT_PRIMARY,
        ).pack(pady=(25, 5))

        ctk.CTkLabel(
            self, text=f"{len(self.messages)} messages from {self.chat_title}",
            font=FONT_BODY, text_color=TEXT_SECONDARY,
        ).pack(pady=(0, 20))

        # Format selection
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=CORNER_RADIUS)
        card.pack(fill="x", padx=25, pady=(0, 15))

        ctk.CTkLabel(
            card, text="Choose Format", font=FONT_SUBHEADING, text_color=TEXT_PRIMARY,
        ).pack(padx=20, pady=(15, 10), anchor="w")

        self.format_var = ctk.StringVar(value="json")

        formats = [
            ("JSON", "json", "Structured data, good for developers"),
            ("CSV", "csv", "Open in Excel, Google Sheets"),
            ("Excel", "xlsx", "Formatted spreadsheet with stats"),
            ("HTML", "html", "Beautiful web page report"),
            ("PDF", "pdf", "Printable document"),
            ("All Formats", "all", "Export in every format at once"),
        ]

        for name, value, desc in formats:
            frame = ctk.CTkFrame(card, fg_color="transparent")
            frame.pack(fill="x", padx=20, pady=2)

            rb = ctk.CTkRadioButton(
                frame, text=name, variable=self.format_var, value=value,
                fg_color=ACCENT, hover_color=ACCENT_HOVER,
                border_color=BORDER, text_color=TEXT_PRIMARY,
                font=FONT_BODY,
            )
            rb.pack(side="left")

            ctk.CTkLabel(
                frame, text=f"  — {desc}",
                font=FONT_SMALL, text_color=TEXT_MUTED,
            ).pack(side="left")

        # Spacer
        ctk.CTkFrame(card, fg_color="transparent", height=10).pack()

        # Status
        self.status_label = ctk.CTkLabel(
            self, text="", font=FONT_BODY, text_color=TEXT_SECONDARY,
        )
        self.status_label.pack(pady=(5, 5))

        # Progress
        self.progress = ctk.CTkProgressBar(self, fg_color=BG_CARD, progress_color=SUCCESS, height=4, width=350)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=25, pady=(5, 25))

        ctk.CTkButton(
            btn_frame, text="Cancel", width=120, height=40,
            fg_color=BG_CARD, hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY, font=FONT_BODY, corner_radius=8,
            command=self.destroy,
        ).pack(side="left")

        self.export_btn = ctk.CTkButton(
            btn_frame, text="Export", width=120, height=40,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            font=FONT_SUBHEADING, corner_radius=8,
            command=self._do_export,
        )
        self.export_btn.pack(side="right")

    def _do_export(self):
        fmt = self.format_var.get()

        # Ask for directory
        export_dir = filedialog.askdirectory(
            title="Choose export folder",
            initialdir=os.path.expanduser("~/Desktop"),
        )
        if not export_dir:
            return

        self.export_btn.configure(state="disabled")
        self.progress.pack(pady=(0, 5))
        self.progress.set(0)

        def run_export():
            try:
                exporter = Exporter(self.messages, self.chat_title)
                safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in self.chat_title)[:50]
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                base = os.path.join(export_dir, f"{safe_title}_{ts}")

                formats_to_export = []
                if fmt == "all":
                    formats_to_export = ["json", "csv", "xlsx", "html", "pdf"]
                else:
                    formats_to_export = [fmt]

                total = len(formats_to_export)
                exported_files = []

                for i, f in enumerate(formats_to_export):
                    self.after(0, lambda t=f: self.status_label.configure(text=f"Exporting {t.upper()}...", text_color=WARNING))
                    self.after(0, lambda v=(i / total): self.progress.set(v))

                    path = f"{base}.{f}"
                    if f == "json":
                        exporter.to_json(path)
                    elif f == "csv":
                        exporter.to_csv(path)
                    elif f == "xlsx":
                        exporter.to_excel(path)
                    elif f == "html":
                        exporter.to_html(path)
                    elif f == "pdf":
                        exporter.to_pdf(path)
                    exported_files.append(path)

                self.after(0, lambda: self.progress.set(1.0))
                self.after(0, lambda: self.status_label.configure(
                    text=f"Exported {len(exported_files)} file(s) to {export_dir}",
                    text_color=SUCCESS,
                ))
                self.after(0, lambda: self.export_btn.configure(text="Done!", state="normal", command=self.destroy))

                # Open folder
                os.startfile(export_dir)

            except Exception as e:
                self.after(0, lambda: self.status_label.configure(text=f"Error: {e}", text_color=ERROR))
                self.after(0, lambda: self.export_btn.configure(state="normal"))

        threading.Thread(target=run_export, daemon=True).start()
