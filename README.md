# TG Saver

Save your Telegram messages before you lose access to chats.

![Electron](https://img.shields.io/badge/Electron-33-47848f?logo=electron)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)

## Why?

If you're a member of a Telegram group, you could be removed at any time — and all your message history, leads, and important data would be lost. This tool lets you backup everything before that happens.

## Features

- **Connect to Telegram** via official API (secure, no bots needed)
- **Browse all your chats** — groups, channels, private chats
- **Search chats** — find the right conversation fast
- **View messages** — scroll through chat history
- **Export in 3 formats:**
  - **JSON** — structured data
  - **CSV** — spreadsheet compatible
  - **TXT** — plain text
- **Modern dark UI** — premium dark theme, smooth animations

## Quick Start

### Run from Source

```bash
git clone https://github.com/ibuildrun/telegram-messages.git
cd telegram-messages
npm install
npm start
```

### Get Telegram API Credentials

1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Go to **"API development tools"**
4. Create an application — you'll get `API_ID` and `API_HASH`
5. Enter these in the app

## How to Use

### Step 1 — Get API Credentials
Go to [my.telegram.org](https://my.telegram.org), log in, create an app under "API development tools". Copy the **API ID** (number) and **API Hash** (string).

### Step 2 — Connect
Launch TG Saver, paste your API ID and API Hash, click **CONNECT**.

### Step 3 — Authenticate
Enter your phone number (with country code, e.g. `+79991234567`). You'll receive a code in Telegram — enter it. If you have 2FA enabled, you'll also need your password.

### Step 4 — Browse Chats
After login, you'll see all your chats. Use the search bar to filter. Click any chat to open it.

### Step 5 — View Messages
Messages load automatically (50 at a time). Click **LOAD MORE** to fetch older messages.

### Step 6 — Export
Click **EXPORT** in the top-right corner. Choose format (JSON, CSV, or TXT). Messages are saved to the `exports/` folder.

## Tech Stack

- **Electron** — cross-platform desktop app
- **GramJS** — Telegram MTProto API client for JavaScript
- **Vanilla JS + CSS** — no framework bloat

## Security

- Your credentials are stored **locally only** in a session file
- No data is sent to any third-party servers
- The app uses Telegram's official MTProto protocol
- Session file location: `%APPDATA%/.telegram-message-saver/session.txt`
- Delete the session file to log out

## License

MIT
