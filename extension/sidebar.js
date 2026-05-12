// Get DOM elements
const messagesContainer = document.getElementById('messages');
const inputElement = document.getElementById('input');
const sendButton = document.getElementById('send');

let sessionId = null;

// Load existing session
chrome.storage.local.get(['sessionId'], (result) => {
  if (result.sessionId) {
    sessionId = result.sessionId;
  }
});

// Send message function
async function sendMessage() {
  const query = inputElement.value.trim();
  if (!query) return;
  
  // Add user message to UI
  addMessage(query, 'user');
  inputElement.value = '';
  
  // Show loading indicator
  const loadingId = addLoadingMessage();
  
  // Get current tab URL
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const currentUrl = tab?.url || '';
  
  try {
    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query,
        session_id: sessionId,
        current_url: currentUrl
      })
    });
    
    const data = await response.json();
    
    // Save session ID
    if (data.session_id) {
      sessionId = data.session_id;
      chrome.storage.local.set({ sessionId: sessionId });
    }
    
    // Remove loading message
    removeLoadingMessage(loadingId);
    
    // Add assistant response
    addMessage(data.response, 'assistant');
    
  } catch (error) {
    removeLoadingMessage(loadingId);
    addMessage('⚠️ Error connecting to AI assistant. Make sure the backend is running.', 'assistant');
    console.error('Error:', error);
  }
}

function addMessage(text, sender) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${sender === 'user' ? 'user-message' : 'assistant-message'}`;
  messageDiv.textContent = text;
  messagesContainer.appendChild(messageDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
  return messageDiv;
}

function addLoadingMessage() {
  const id = 'loading-' + Date.now();
  const loadingDiv = document.createElement('div');
  loadingDiv.id = id;
  loadingDiv.className = 'loading';
  loadingDiv.textContent = '🤔 Thinking...';
  messagesContainer.appendChild(loadingDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
  return id;
}

function removeLoadingMessage(id) {
  const element = document.getElementById(id);
  if (element) element.remove();
}

// Event listeners
sendButton.addEventListener('click', sendMessage);
inputElement.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') sendMessage();
});

// Auto-focus input
inputElement.focus();

// Add welcome message
addMessage('👋 Hi! I\'m your Mulungushi University assistant. Ask me about your grades, fee balance, or enrolled courses!', 'assistant');