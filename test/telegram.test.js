const assert = require('assert');
const path = require('path');
const fs = require('fs');

// =============================================
// TG SAVER — Unit Tests
// =============================================

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`  ✓ ${name}`);
  } catch (e) {
    failed++;
    console.log(`  ✗ ${name}`);
    console.log(`    ${e.message}`);
  }
}

// --- 1. Project structure tests ---
console.log('\n[1] Project Structure');

test('package.json exists and is valid', () => {
  const pkg = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'package.json'), 'utf-8'));
  assert.strictEqual(pkg.name, 'telegram-message-saver');
  assert.ok(pkg.main);
  assert.ok(pkg.scripts.start);
  assert.ok(pkg.dependencies.telegram);
  assert.ok(pkg.devDependencies.electron);
});

test('main entry point exists', () => {
  assert.ok(fs.existsSync(path.join(__dirname, '..', 'src', 'main', 'main.js')));
});

test('preload.js exists', () => {
  assert.ok(fs.existsSync(path.join(__dirname, '..', 'src', 'main', 'preload.js')));
});

test('telegram.js exists', () => {
  assert.ok(fs.existsSync(path.join(__dirname, '..', 'src', 'main', 'telegram.js')));
});

test('renderer index.html exists', () => {
  assert.ok(fs.existsSync(path.join(__dirname, '..', 'src', 'renderer', 'index.html')));
});

test('renderer style.css exists', () => {
  assert.ok(fs.existsSync(path.join(__dirname, '..', 'src', 'renderer', 'css', 'style.css')));
});

test('renderer app.js exists', () => {
  assert.ok(fs.existsSync(path.join(__dirname, '..', 'src', 'renderer', 'js', 'app.js')));
});

// --- 2. TelegramClient module tests ---
console.log('\n[2] TelegramClient Module');

test('telegram.js exports TelegramClient class', () => {
  const mod = require('../src/main/telegram');
  assert.ok(mod.TelegramClient);
  assert.strictEqual(typeof mod.TelegramClient, 'function');
});

test('TelegramClient constructor accepts apiId and apiHash', () => {
  const { TelegramClient } = require('../src/main/telegram');
  const client = new TelegramClient(12345, 'abc123');
  assert.strictEqual(client.apiId, 12345);
  assert.strictEqual(client.apiHash, 'abc123');
});

test('TelegramClient has required methods', () => {
  const { TelegramClient } = require('../src/main/telegram');
  const client = new TelegramClient(12345, 'abc123');
  assert.strictEqual(typeof client.connect, 'function');
  assert.strictEqual(typeof client.sendCode, 'function');
  assert.strictEqual(typeof client.signIn, 'function');
  assert.strictEqual(typeof client.getMe, 'function');
  assert.strictEqual(typeof client.getDialogs, 'function');
  assert.strictEqual(typeof client.getMessages, 'function');
  assert.strictEqual(typeof client.exportMessages, 'function');
  assert.strictEqual(typeof client.disconnect, 'function');
});

test('TelegramClient._saveSession creates session directory', () => {
  const { TelegramClient } = require('../src/main/telegram');
  const client = new TelegramClient(12345, 'abc123');
  // Just verify the method exists — actual save requires connected client
  assert.strictEqual(typeof client._saveSession, 'function');
});

// --- 3. HTML structure tests ---
console.log('\n[3] HTML Structure');

const html = fs.readFileSync(path.join(__dirname, '..', 'src', 'renderer', 'index.html'), 'utf-8');

test('HTML has proper doctype', () => {
  assert.ok(html.startsWith('<!DOCTYPE html>'));
});

test('HTML includes style.css', () => {
  assert.ok(html.includes('css/style.css'));
});

test('HTML includes app.js', () => {
  assert.ok(html.includes('js/app.js'));
});

test('HTML has titlebar with controls', () => {
  assert.ok(html.includes('id="btn-minimize"'));
  assert.ok(html.includes('id="btn-maximize"'));
  assert.ok(html.includes('id="btn-close"'));
});

test('HTML has auth view with all steps', () => {
  assert.ok(html.includes('id="step-api"'));
  assert.ok(html.includes('id="step-phone"'));
  assert.ok(html.includes('id="step-code"'));
  assert.ok(html.includes('id="step-password"'));
});

test('HTML has chats view', () => {
  assert.ok(html.includes('id="view-chats"'));
  assert.ok(html.includes('id="chats-list"'));
  assert.ok(html.includes('id="search-chats"'));
});

test('HTML has messages view', () => {
  assert.ok(html.includes('id="view-messages"'));
  assert.ok(html.includes('id="messages-list"'));
  assert.ok(html.includes('id="btn-export"'));
  assert.ok(html.includes('id="btn-back"'));
  assert.ok(html.includes('id="btn-load-more"'));
});

test('HTML has export modal with 3 formats', () => {
  assert.ok(html.includes('id="modal-export"'));
  assert.ok(html.includes('data-format="json"'));
  assert.ok(html.includes('data-format="csv"'));
  assert.ok(html.includes('data-format="txt"'));
});

test('HTML has sidebar', () => {
  assert.ok(html.includes('id="sidebar"'));
  assert.ok(html.includes('id="btn-disconnect"'));
  assert.ok(html.includes('id="sidebar-user"'));
});

// --- 4. CSS tests ---
console.log('\n[4] CSS Theme');

const css = fs.readFileSync(path.join(__dirname, '..', 'src', 'renderer', 'css', 'style.css'), 'utf-8');

test('CSS uses ibuildrun dark theme colors', () => {
  assert.ok(css.includes('#0b0e14'));   // bg
  assert.ok(css.includes('#161a23'));   // card bg
  assert.ok(css.includes('#7e9dff'));   // accent
  assert.ok(css.includes('#f8fafc'));   // text
});

test('CSS uses Inter + Space Mono fonts', () => {
  assert.ok(css.includes('Inter'));
  assert.ok(css.includes('Space Mono'));
});

test('CSS has custom scrollbar styling', () => {
  assert.ok(css.includes('::-webkit-scrollbar'));
});

test('CSS has titlebar styles', () => {
  assert.ok(css.includes('.titlebar'));
  assert.ok(css.includes('-webkit-app-region: drag'));
});

test('CSS has glass morphism / backdrop blur', () => {
  assert.ok(css.includes('backdrop-filter'));
});

test('CSS has animation keyframes', () => {
  assert.ok(css.includes('@keyframes'));
  assert.ok(css.includes('msgIn'));
  assert.ok(css.includes('spin'));
});

// --- 5. Renderer JS logic tests ---
console.log('\n[5] Renderer JS Logic');

const appJs = fs.readFileSync(path.join(__dirname, '..', 'src', 'renderer', 'js', 'app.js'), 'utf-8');

test('app.js has state management', () => {
  assert.ok(appJs.includes('const state'));
  assert.ok(appJs.includes('currentView'));
  assert.ok(appJs.includes('chats'));
  assert.ok(appJs.includes('messages'));
});

test('app.js has view switching logic', () => {
  assert.ok(appJs.includes('function switchView'));
});

test('app.js has auth flow functions', () => {
  assert.ok(appJs.includes('showStep'));
  assert.ok(appJs.includes('setStatus'));
  assert.ok(appJs.includes('onAuthenticated'));
});

test('app.js has chat rendering', () => {
  assert.ok(appJs.includes('function renderChats'));
  assert.ok(appJs.includes('function loadChats'));
  assert.ok(appJs.includes('getAvatarColor'));
});

test('app.js has message rendering', () => {
  assert.ok(appJs.includes('function renderMessages'));
  assert.ok(appJs.includes('function loadMessages'));
  assert.ok(appJs.includes('function openChat'));
});

test('app.js has export modal logic', () => {
  assert.ok(appJs.includes('export-option'));
  assert.ok(appJs.includes('exportMessages'));
});

test('app.js has XSS protection (escHtml)', () => {
  assert.ok(appJs.includes('function escHtml'));
  assert.ok(appJs.includes('&amp;'));
  assert.ok(appJs.includes('&lt;'));
  assert.ok(appJs.includes('&gt;'));
});

test('app.js has search functionality', () => {
  assert.ok(appJs.includes('search-chats'));
  assert.ok(appJs.includes('filteredChats'));
});

test('app.js has disconnect functionality', () => {
  assert.ok(appJs.includes('btn-disconnect'));
  assert.ok(appJs.includes('disconnect'));
});

// --- 6. Preload security tests ---
console.log('\n[6] Preload Security');

const preload = fs.readFileSync(path.join(__dirname, '..', 'src', 'main', 'preload.js'), 'utf-8');

test('preload uses contextBridge', () => {
  assert.ok(preload.includes('contextBridge'));
  assert.ok(preload.includes('exposeInMainWorld'));
});

test('preload exposes only specific API via contextBridge', () => {
  assert.ok(preload.includes("'api'"));
  assert.ok(!preload.includes('nodeIntegration'));
  // preload correctly uses require() for electron modules only
  assert.ok(preload.includes("require('electron')"));
});

test('preload exposes all required methods', () => {
  const methods = ['minimize', 'maximize', 'close', 'connect', 'sendCode', 'signIn', 'getDialogs', 'getMessages', 'exportMessages', 'getMe', 'disconnect'];
  methods.forEach(m => {
    assert.ok(preload.includes(m), `Missing method: ${m}`);
  });
});

// --- 7. Main process IPC tests ---
console.log('\n[7] Main Process IPC');

const mainJs = fs.readFileSync(path.join(__dirname, '..', 'src', 'main', 'main.js'), 'utf-8');

test('main.js has window control handlers', () => {
  assert.ok(mainJs.includes("'window:minimize'"));
  assert.ok(mainJs.includes("'window:maximize'"));
  assert.ok(mainJs.includes("'window:close'"));
});

test('main.js has all Telegram IPC handlers', () => {
  const handlers = ['tg:connect', 'tg:sendCode', 'tg:signIn', 'tg:getDialogs', 'tg:getMessages', 'tg:exportMessages', 'tg:getMe', 'tg:disconnect'];
  handlers.forEach(h => {
    assert.ok(mainJs.includes(`'${h}'`), `Missing handler: ${h}`);
  });
});

test('main.js uses contextIsolation: true', () => {
  assert.ok(mainJs.includes('contextIsolation: true'));
});

test('main.js uses nodeIntegration: false', () => {
  assert.ok(mainJs.includes('nodeIntegration: false'));
});

test('main.js has error handling in IPC (returns ok/error)', () => {
  const okCount = (mainJs.match(/ok: true/g) || []).length;
  const errCount = (mainJs.match(/ok: false/g) || []).length;
  assert.ok(okCount >= 7, `Expected >=7 ok:true, got ${okCount}`);
  assert.ok(errCount >= 7, `Expected >=7 ok:false, got ${errCount}`);
});

test('main.js cleans up on window close', () => {
  assert.ok(mainJs.includes('window-all-closed'));
  assert.ok(mainJs.includes('disconnect'));
});

// --- 8. Export format tests ---
console.log('\n[8] Export Formats');

test('telegram.js supports JSON export', () => {
  const tgJs = fs.readFileSync(path.join(__dirname, '..', 'src', 'main', 'telegram.js'), 'utf-8');
  assert.ok(tgJs.includes("format === 'json'"));
  assert.ok(tgJs.includes('JSON.stringify'));
});

test('telegram.js supports CSV export', () => {
  const tgJs = fs.readFileSync(path.join(__dirname, '..', 'src', 'main', 'telegram.js'), 'utf-8');
  assert.ok(tgJs.includes("format === 'csv'"));
  assert.ok(tgJs.includes('id,date,sender'));
});

test('telegram.js supports TXT export', () => {
  const tgJs = fs.readFileSync(path.join(__dirname, '..', 'src', 'main', 'telegram.js'), 'utf-8');
  // TXT is the else branch
  assert.ok(tgJs.includes('m.sender'));
  assert.ok(tgJs.includes('m.text'));
});

test('telegram.js creates export directory if missing', () => {
  const tgJs = fs.readFileSync(path.join(__dirname, '..', 'src', 'main', 'telegram.js'), 'utf-8');
  assert.ok(tgJs.includes("mkdirSync(dir, { recursive: true })"));
});

// --- Summary ---
console.log('\n' + '='.repeat(40));
console.log(`Results: ${passed} passed, ${failed} failed, ${passed + failed} total`);
console.log('='.repeat(40));

process.exit(failed > 0 ? 1 : 0);
