const tenantInput = document.querySelector('#tenant');
const apiInput = document.querySelector('#api');
const chatForm = document.querySelector('#chat-form');
const messageInput = document.querySelector('#message-input');
const messages = document.querySelector('#messages');
const resetButton = document.querySelector('#reset');
const sessionText = document.querySelector('#session');

const SESSION_KEY = 'vantage.sessionId';

function getSessionId() {
  let id = localStorage.getItem(SESSION_KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

function resetSession() {
  const id = crypto.randomUUID();
  localStorage.setItem(SESSION_KEY, id);
  sessionText.textContent = `Session: ${id}`;
  messages.innerHTML = '';
}

function addMessage(text, role) {
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

async function sendMessage(text) {
  const base = apiInput.value.replace(/\/$/, '');
  const payload = {
    tenant_id: Number(tenantInput.value),
    text,
    session_id: getSessionId(),
  };

  const res = await fetch(`${base}/api/chat`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error(`request failed with ${res.status}`);
  }
  const data = await res.json();
  return data.reply || `[${data.status}]`;
}

chatForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (!text) {
    return;
  }

  addMessage(text, 'user');
  messageInput.value = '';

  try {
    const reply = await sendMessage(text);
    addMessage(reply, 'bot');
  } catch (error) {
    addMessage(`Error: ${error.message}`, 'bot');
  }
});

resetButton.addEventListener('click', resetSession);
sessionText.textContent = `Session: ${getSessionId()}`;
