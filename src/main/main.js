const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { TelegramClient } = require('./telegram');

let mainWindow;
let tgClient;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    frame: false,
    transparent: false,
    backgroundColor: '#0b0e14',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    icon: path.join(__dirname, '..', 'renderer', 'icon.png'),
  });

  mainWindow.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));

  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }
}

app.whenReady().then(createWindow);

app.on('window-all-closed', async () => {
  if (tgClient) {
    await tgClient.disconnect();
  }
  app.quit();
});

// Window controls
ipcMain.on('window:minimize', () => mainWindow?.minimize());
ipcMain.on('window:maximize', () => {
  if (mainWindow?.isMaximized()) {
    mainWindow.unmaximize();
  } else {
    mainWindow?.maximize();
  }
});
ipcMain.on('window:close', () => mainWindow?.close());

// Telegram API
ipcMain.handle('tg:connect', async (_, { apiId, apiHash }) => {
  try {
    tgClient = new TelegramClient(parseInt(apiId), apiHash);
    await tgClient.connect();
    return { ok: true };
  } catch (e) {
    return { ok: false, error: e.message };
  }
});

ipcMain.handle('tg:sendCode', async (_, { phone }) => {
  try {
    const result = await tgClient.sendCode(phone);
    return { ok: true, phoneCodeHash: result };
  } catch (e) {
    return { ok: false, error: e.message };
  }
});

ipcMain.handle('tg:signIn', async (_, { phone, code, phoneCodeHash, password }) => {
  try {
    const user = await tgClient.signIn(phone, code, phoneCodeHash, password);
    return { ok: true, user };
  } catch (e) {
    if (e.message.includes('SESSION_PASSWORD_NEEDED') || e.errorMessage === 'SESSION_PASSWORD_NEEDED') {
      return { ok: false, needPassword: true };
    }
    return { ok: false, error: e.message };
  }
});

ipcMain.handle('tg:getDialogs', async () => {
  try {
    const dialogs = await tgClient.getDialogs();
    return { ok: true, dialogs };
  } catch (e) {
    return { ok: false, error: e.message };
  }
});

ipcMain.handle('tg:getMessages', async (_, { chatId, limit, offsetId }) => {
  try {
    const messages = await tgClient.getMessages(chatId, limit, offsetId);
    return { ok: true, messages };
  } catch (e) {
    return { ok: false, error: e.message };
  }
});

ipcMain.handle('tg:exportMessages', async (_, { chatId, format, filePath }) => {
  try {
    const result = await tgClient.exportMessages(chatId, format, filePath);
    return { ok: true, count: result };
  } catch (e) {
    return { ok: false, error: e.message };
  }
});

ipcMain.handle('tg:getMe', async () => {
  try {
    const me = await tgClient.getMe();
    return { ok: true, user: me };
  } catch (e) {
    return { ok: false, error: e.message };
  }
});

ipcMain.handle('tg:disconnect', async () => {
  try {
    if (tgClient) await tgClient.disconnect();
    tgClient = null;
    return { ok: true };
  } catch (e) {
    return { ok: false, error: e.message };
  }
});
