"""Telegram Message Saver - Desktop Application.

Save your Telegram messages before you lose access to chats.
"""
import sys
import os

# Ensure the app package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ui.app import App


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
