# Telegram Message Saver

Save your Telegram chat messages before you lose access. Built for anyone who needs to backup important conversations, leads, or data from Telegram groups and chats.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows-blue?logo=windows)

## Why?

If you're an assistant or team member in a Telegram group, you could be removed at any time — and all your message history, leads, and important data would be lost. This tool lets you download and backup everything before that happens.

## Features

- **Connect to Telegram** via official API (secure, no bots needed)
- **Browse all your chats** — groups, supergroups, channels, private chats
- **Filter by sender** — find messages from a specific person
- **Search messages** — full-text search through chat history
- **Export in 5 formats:**
  - **JSON** — structured data for developers
  - **CSV** — open in Excel or Google Sheets
  - **Excel (.xlsx)** — formatted spreadsheet with sender statistics
  - **HTML** — beautiful dark-themed web report
  - **PDF** — printable document
- **Export all formats at once** with a single click
- **Modern dark UI** — clean, fast, and easy to use

## Quick Start

### Download (Windows)

1. Go to [Releases](../../releases)
2. Download `TelegramMessageSaver.exe`
3. Run it — no installation needed

### Run from Source

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/telegram-message-saver.git
cd telegram-message-saver

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

### Get Telegram API Credentials

1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Go to "API development tools"
4. Create an application — you'll get `api_id` and `api_hash`
5. Enter these in the app

## How to Use

1. **Launch the app** and enter your API credentials
2. **Enter your phone number** and verify with the code Telegram sends you
3. **Browse your chats** — use search and filters to find the right one
4. **Open a chat** — all messages load automatically
5. **Filter by sender** — select a specific person from the dropdown
6. **Export** — click Export, choose format, pick a folder, done!

## Building from Source

```bash
# Install build tools
pip install pyinstaller

# Build .exe
python build.py
```

The executable will be in `dist/TelegramMessageSaver.exe`.

## Tech Stack

- **Python 3.10+**
- **CustomTkinter** — modern dark-themed UI
- **Telethon** — Telegram MTProto API client
- **openpyxl** — Excel export
- **fpdf2** — PDF export
- **Jinja2** — HTML template rendering

## Security

- Your credentials are stored **locally only** in a session file
- No data is sent to any third-party servers
- The app uses Telegram's official MTProto protocol
- You can delete the session file at any time to log out

## License

MIT License — do whatever you want with it.
