/* ============================================
   TG SAVER — Renderer logic
   ============================================ */

// --- State ---
const state = {
  currentView: 'auth',
  phone: '',
  phoneCodeHash: '',
  chats: [],
  filteredChats: [],
  currentChat: null,
  messages: [],
  lastMsgId: 0,
};

// --- DOM refs ---
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// Window controls
$('#btn-minimize').onclick = () => window.api.minimize();
$('#btn-maximize').onclick = () => window.api.maximize();
$('#btn-close').onclick = () => window.api.close();

// --- Auth flow ---
const showStep = (stepId) => {
  $$('.auth-step').forEach(s => s.classList.remove('active'));
  $(`#step-${stepId}`).classList.add('active');
  clearStatus();
};

const setStatus = (type, text) => {
  const el = $('#auth-status');
  el.className = `auth-status ${type}`;
  el.innerHTML = type === 'loading' ? `<div class="spinner"></div><span>${text}</span>` : text;
};

const clearStatus = () => {
  const el = $('#auth-status');
  el.className = 'auth-status';
  el.style.display = 'none';
};

// Open external links
$('#link-telegram-api')?.addEventListener('click', (e) => {
  e.preventDefault();
  require('electron')?.shell?.openExternal?.('https://my.telegram.org') ||
    window.open('https://my.telegram.org', '_blank');
});

// Step 1: Connect
$('#btn-connect').onclick = async () => {
  const apiId = $('#input-api-id').value.trim();
  const apiHash = $('#input-api-hash').value.trim();
  if (!apiId || !apiHash) return setStatus('error', 'Please fill in both fields');

  setStatus('loading', 'Connecting to Telegram...');
  const res = await window.api.connect({ apiId, apiHash });
  if (res.ok) {
    setStatus('success', 'Connected! Enter your phone number.');
    setTimeout(() => showStep('phone'), 600);
  } else {
    setStatus('error', res.error || 'Connection failed');
  }
};

// Step 2: Send code
$('#btn-send-code').onclick = async () => {
  state.phone = $('#input-phone').value.trim();
  if (!state.phone) return setStatus('error', 'Enter your phone number');

  setStatus('loading', 'Sending verification code...');
  const res = await window.api.sendCode({ phone: state.phone });
  if (res.ok) {
    state.phoneCodeHash = res.phoneCodeHash;
    setStatus('success', 'Code sent! Check your Telegram app.');
    setTimeout(() => showStep('code'), 600);
  } else {
    setStatus('error', res.error || 'Failed to send code');
  }
};

// Step 3: Verify code
$('#btn-verify').onclick = async () => {
  const code = $('#input-code').value.trim();
  if (!code) return setStatus('error', 'Enter the verification code');

  setStatus('loading', 'Verifying...');
  const res = await window.api.signIn({
    phone: state.phone,
    code,
    phoneCodeHash: state.phoneCodeHash,
  });

  if (res.ok) {
    onAuthenticated(res.user);
  } else if (res.needPassword) {
    setStatus('success', '2FA enabled. Enter your password.');
    setTimeout(() => showStep('password'), 600);
  } else {
    setStatus('error', res.error || 'Verification failed');
  }
};

// Step 4: 2FA password
$('#btn-password').onclick = async () => {
  const password = $('#input-password').value;
  if (!password) return setStatus('error', 'Enter your password');

  setStatus('loading', 'Checking password...');
  const res = await window.api.signIn({
    phone: state.phone,
    code: $('#input-code').value.trim(),
    phoneCodeHash: state.phoneCodeHash,
    password,
  });

  if (res.ok) {
    onAuthenticated(res.user);
  } else {
    setStatus('error', res.error || 'Invalid password');
  }
};

// Enter key support on inputs
$$('.auth-step .input').forEach(input => {
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const step = input.closest('.auth-step');
      step.querySelector('.btn-primary')?.click();
    }
  });
});

// --- Authenticated ---
async function onAuthenticated(user) {
  setStatus('success', `Welcome, ${user?.firstName || 'User'}!`);

  const name = user ? `${user.firstName || ''} ${user.lastName || ''}`.trim() : '';
  $('#sidebar-user').textContent = name || 'Connected';

  setTimeout(() => {
    switchView('chats');
    $('#sidebar').classList.remove('hidden');
    loadChats();
  }, 800);
}

// --- View switching ---
function switchView(viewName) {
  $$('.view').forEach(v => v.classList.remove('active'));
  $(`#view-${viewName}`).classList.add('active');
  $$('.nav-btn').forEach(b => b.classList.remove('active'));
  $(`.nav-btn[data-view="${viewName}"]`)?.classList.add('active');
  state.currentView = viewName;
}

$('#nav-chats').onclick = () => {
  switchView('chats');
};

// --- Chats ---
const AVATAR_COLORS = [
  '#7e9dff', '#ff7eb3', '#7effdb', '#ffd97e', '#ff7e7e',
  '#c47eff', '#7ec8ff', '#a8ff7e', '#ff9d7e', '#7efff1',
];

function getAvatarColor(title) {
  let hash = 0;
  for (let i = 0; i < title.length; i++) hash = title.charCodeAt(i) + ((hash << 5) - hash);
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length];
}

function formatDate(timestamp) {
  if (!timestamp) return '';
  const d = new Date(timestamp * 1000);
  const now = new Date();
  const diff = now - d;

  if (diff < 86400000) {
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
  if (diff < 604800000) {
    return d.toLocaleDateString([], { weekday: 'short' });
  }
  return d.toLocaleDateString([], { day: 'numeric', month: 'short' });
}

async function loadChats() {
  $('#chats-list').innerHTML = '<div class="loading"><div class="spinner"></div>&nbsp;&nbsp;Loading chats...</div>';

  const res = await window.api.getDialogs();
  if (!res.ok) {
    $('#chats-list').innerHTML = `<div class="empty-state"><p>Failed to load chats</p><p style="font-size:12px">${res.error}</p></div>`;
    return;
  }

  state.chats = res.dialogs;
  state.filteredChats = [...state.chats];
  renderChats();
}

function renderChats() {
  const list = $('#chats-list');

  if (!state.filteredChats.length) {
    list.innerHTML = '<div class="empty-state"><p>No chats found</p></div>';
    return;
  }

  list.innerHTML = state.filteredChats.map(chat => {
    const color = getAvatarColor(chat.title);
    const initial = (chat.title[0] || '?').toUpperCase();
    const typeClass = chat.isChannel ? 'channel' : chat.isGroup ? 'group' : 'user';
    const typeLabel = chat.isChannel ? 'Channel' : chat.isGroup ? 'Group' : 'User';

    return `
      <div class="chat-item" data-id="${chat.id}">
        <div class="chat-avatar" style="background:${color}">${initial}</div>
        <div class="chat-info">
          <div class="chat-name">${escHtml(chat.title)}</div>
          <div class="chat-last-msg">${escHtml(truncate(chat.message, 60))}</div>
        </div>
        <div class="chat-meta">
          <div class="chat-date">${formatDate(chat.date)}</div>
          ${chat.unreadCount ? `<div class="chat-badge">${chat.unreadCount}</div>` : ''}
          <div class="chat-type ${typeClass}">${typeLabel}</div>
        </div>
      </div>
    `;
  }).join('');

  // Click handlers
  list.querySelectorAll('.chat-item').forEach(item => {
    item.onclick = () => {
      const chat = state.chats.find(c => c.id === item.dataset.id);
      if (chat) openChat(chat);
    };
  });
}

// Search
$('#search-chats').oninput = (e) => {
  const q = e.target.value.toLowerCase();
  state.filteredChats = q
    ? state.chats.filter(c => c.title.toLowerCase().includes(q))
    : [...state.chats];
  renderChats();
};

// --- Messages ---
async function openChat(chat) {
  state.currentChat = chat;
  state.messages = [];
  state.lastMsgId = 0;

  $('#messages-title').textContent = chat.title;
  $('#messages-count').textContent = '';
  $('#messages-list').innerHTML = '<div class="loading"><div class="spinner"></div>&nbsp;&nbsp;Loading messages...</div>';
  $('#btn-load-more').classList.add('hidden');

  switchView('messages');
  await loadMessages();
}

async function loadMessages(loadMore = false) {
  const res = await window.api.getMessages({
    chatId: state.currentChat.id,
    limit: 50,
    offsetId: loadMore ? state.lastMsgId : 0,
  });

  if (!res.ok) {
    if (!loadMore) {
      $('#messages-list').innerHTML = `<div class="empty-state"><p>Failed to load messages</p></div>`;
    }
    return;
  }

  if (!loadMore) {
    state.messages = res.messages;
  } else {
    state.messages.push(...res.messages);
  }

  if (res.messages.length > 0) {
    state.lastMsgId = res.messages[res.messages.length - 1].id;
  }

  renderMessages();

  if (res.messages.length >= 50) {
    $('#btn-load-more').classList.remove('hidden');
  } else {
    $('#btn-load-more').classList.add('hidden');
  }

  $('#messages-count').textContent = `${state.messages.length} messages`;
}

function renderMessages() {
  const list = $('#messages-list');
  // Show oldest first
  const msgs = [...state.messages].reverse();

  list.innerHTML = msgs.map(m => {
    const cls = m.isOutgoing ? 'outgoing' : 'incoming';
    const time = m.date ? new Date(m.date * 1000).toLocaleString([], {
      hour: '2-digit', minute: '2-digit', day: 'numeric', month: 'short'
    }) : '';

    return `
      <div class="message-item ${cls}">
        ${!m.isOutgoing ? `<div class="message-sender">${escHtml(m.senderName)}</div>` : ''}
        ${m.text ? `<div class="message-text">${escHtml(m.text)}</div>` : ''}
        ${m.media ? `<div class="message-media">[${m.media}]</div>` : ''}
        <div class="message-time">${time}</div>
      </div>
    `;
  }).join('');

  // Scroll to bottom
  list.scrollTop = list.scrollHeight;
}

$('#btn-back').onclick = () => switchView('chats');
$('#btn-load-more').onclick = () => loadMessages(true);

// --- Export ---
$('#btn-export').onclick = () => {
  if (!state.currentChat) return;
  $('#export-chat-name').textContent = state.currentChat.title;
  $('#modal-export').classList.remove('hidden');
  $('#export-status').classList.add('hidden');
  $('#export-status').className = 'export-status hidden';
};

$('#btn-modal-close').onclick = () => $('#modal-export').classList.add('hidden');
$('.modal-overlay')?.addEventListener('click', () => $('#modal-export').classList.add('hidden'));

$$('.export-option').forEach(btn => {
  btn.onclick = async () => {
    const format = btn.dataset.format;
    const chatTitle = state.currentChat.title.replace(/[^a-zA-Zа-яА-Я0-9_-]/g, '_');
    const filePath = `exports/${chatTitle}_${Date.now()}.${format}`;

    const statusEl = $('#export-status');
    statusEl.className = 'export-status';
    statusEl.innerHTML = '<div class="spinner"></div><span>Exporting all messages...</span>';

    const res = await window.api.exportMessages({
      chatId: state.currentChat.id,
      format,
      filePath,
    });

    if (res.ok) {
      statusEl.className = 'export-status done';
      statusEl.innerHTML = `✓ Exported ${res.count} messages to ${filePath}`;
    } else {
      statusEl.className = 'export-status error';
      statusEl.innerHTML = `✗ Export failed: ${res.error}`;
      statusEl.style.background = 'rgba(255,107,107,0.1)';
      statusEl.style.color = 'var(--danger)';
    }
  };
});

// --- Disconnect ---
$('#btn-disconnect').onclick = async () => {
  await window.api.disconnect();
  $('#sidebar').classList.add('hidden');
  switchView('auth');
  showStep('api');
  // Clear inputs
  $$('.auth-step .input').forEach(i => i.value = '');
  clearStatus();
};

// --- Helpers ---
function escHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function truncate(str, len) {
  if (!str) return '';
  return str.length > len ? str.slice(0, len) + '…' : str;
}
