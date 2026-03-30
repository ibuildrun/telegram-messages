const { TelegramClient: GramClient } = require('telegram');
const { StringSession } = require('telegram/sessions');
const { Api } = require('telegram/tl');
const fs = require('fs');
const path = require('path');

const SESSION_PATH = path.join(
  process.env.APPDATA || process.env.HOME,
  '.telegram-message-saver',
  'session.txt'
);

class TelegramClient {
  constructor(apiId, apiHash) {
    this.apiId = apiId;
    this.apiHash = apiHash;

    // Try to restore session
    let sessionStr = '';
    try {
      if (fs.existsSync(SESSION_PATH)) {
        sessionStr = fs.readFileSync(SESSION_PATH, 'utf-8').trim();
      }
    } catch {}

    this.session = new StringSession(sessionStr);
    this.client = new GramClient(this.session, this.apiId, this.apiHash, {
      connectionRetries: 3,
    });
  }

  async connect() {
    await this.client.connect();
  }

  _saveSession() {
    const dir = path.dirname(SESSION_PATH);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(SESSION_PATH, this.client.session.save());
  }

  async sendCode(phone) {
    const result = await this.client.sendCode(
      { apiId: this.apiId, apiHash: this.apiHash },
      phone
    );
    return result.phoneCodeHash;
  }

  async signIn(phone, code, phoneCodeHash, password) {
    try {
      await this.client.invoke(
        new Api.auth.SignIn({
          phoneNumber: phone,
          phoneCodeHash,
          phoneCode: code,
        })
      );
    } catch (e) {
      if (e.errorMessage === 'SESSION_PASSWORD_NEEDED') {
        if (!password) throw e;
        await this.client.invoke(
          new Api.auth.CheckPassword({
            password: await this.client.invoke(new Api.account.GetPassword())
              .then(pwd => require('telegram/Password').computeCheck(pwd, password)),
          })
        );
      } else {
        throw e;
      }
    }

    this._saveSession();
    const me = await this.client.getMe();
    return {
      id: me.id.toString(),
      firstName: me.firstName,
      lastName: me.lastName,
      username: me.username,
      phone: me.phone,
    };
  }

  async getMe() {
    const me = await this.client.getMe();
    return {
      id: me.id.toString(),
      firstName: me.firstName,
      lastName: me.lastName,
      username: me.username,
      phone: me.phone,
    };
  }

  async getDialogs() {
    const dialogs = await this.client.getDialogs({ limit: 100 });
    return dialogs.map(d => ({
      id: d.id.toString(),
      title: d.title || d.name || 'Unknown',
      unreadCount: d.unreadCount,
      date: d.date,
      isGroup: d.isGroup,
      isChannel: d.isChannel,
      isUser: d.isUser,
      message: d.message?.message || '',
    }));
  }

  async getMessages(chatId, limit = 50, offsetId = 0) {
    const entity = await this.client.getEntity(chatId);
    const messages = await this.client.getMessages(entity, {
      limit,
      offsetId: offsetId || undefined,
    });

    return messages.map(m => ({
      id: m.id,
      text: m.message || '',
      date: m.date,
      senderId: m.senderId?.toString() || '',
      senderName: m._sender
        ? `${m._sender.firstName || ''} ${m._sender.lastName || ''}`.trim() || m._sender.username || 'Unknown'
        : 'Unknown',
      isOutgoing: m.out,
      media: m.media ? m.media.className : null,
      replyToMsgId: m.replyTo?.replyToMsgId || null,
    }));
  }

  async exportMessages(chatId, format, filePath) {
    const entity = await this.client.getEntity(chatId);
    let allMessages = [];
    let offsetId = 0;

    // Fetch all messages
    while (true) {
      const batch = await this.client.getMessages(entity, {
        limit: 100,
        offsetId: offsetId || undefined,
      });
      if (!batch.length) break;

      allMessages.push(...batch.map(m => ({
        id: m.id,
        text: m.message || '',
        date: new Date(m.date * 1000).toISOString(),
        sender: m._sender
          ? `${m._sender.firstName || ''} ${m._sender.lastName || ''}`.trim() || m._sender.username || 'Unknown'
          : 'Unknown',
        isOutgoing: m.out,
      })));

      offsetId = batch[batch.length - 1].id;
      if (batch.length < 100) break;
    }

    // Write file
    const dir = path.dirname(filePath);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

    if (format === 'json') {
      fs.writeFileSync(filePath, JSON.stringify(allMessages, null, 2), 'utf-8');
    } else if (format === 'csv') {
      const header = 'id,date,sender,is_outgoing,text\n';
      const rows = allMessages.map(m =>
        `${m.id},"${m.date}","${(m.sender || '').replace(/"/g, '""')}",${m.isOutgoing},"${(m.text || '').replace(/"/g, '""').replace(/\n/g, '\\n')}"`
      ).join('\n');
      fs.writeFileSync(filePath, header + rows, 'utf-8');
    } else {
      const lines = allMessages.map(m =>
        `[${m.date}] ${m.sender}: ${m.text}`
      ).join('\n');
      fs.writeFileSync(filePath, lines, 'utf-8');
    }

    return allMessages.length;
  }

  async disconnect() {
    try {
      await this.client.disconnect();
    } catch {}
  }
}

module.exports = { TelegramClient };
