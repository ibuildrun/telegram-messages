const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  // Window controls
  minimize: () => ipcRenderer.send('window:minimize'),
  maximize: () => ipcRenderer.send('window:maximize'),
  close: () => ipcRenderer.send('window:close'),

  // Telegram
  connect: (data) => ipcRenderer.invoke('tg:connect', data),
  sendCode: (data) => ipcRenderer.invoke('tg:sendCode', data),
  signIn: (data) => ipcRenderer.invoke('tg:signIn', data),
  getDialogs: () => ipcRenderer.invoke('tg:getDialogs'),
  getMessages: (data) => ipcRenderer.invoke('tg:getMessages', data),
  exportMessages: (data) => ipcRenderer.invoke('tg:exportMessages', data),
  getMe: () => ipcRenderer.invoke('tg:getMe'),
  disconnect: () => ipcRenderer.invoke('tg:disconnect'),
});
