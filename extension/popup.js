const messagesContainer = document.getElementById('messages');
const input = document.getElementById('input');
const sendBtn = document.getElementById('send');
const statusContainer = document.getElementById('statusMessages');

let sessionId = null;
let ws = null;
let currentSessionId = null;

// Storage keys
const STORAGE_KEYS = {
    SESSION_ID: 'sessionId',
    CHAT_HISTORY: 'chatHistory',
    LAST_SESSION: 'lastSession'
};

// Maximum messages to store (prevents storage overflow)
const MAX_STORED_MESSAGES = 100;

// Load saved session
chrome.storage.local.get([STORAGE_KEYS.SESSION_ID, STORAGE_KEYS.CHAT_HISTORY], (result) => {
    if (result[STORAGE_KEYS.SESSION_ID]) {
        sessionId = result[STORAGE_KEYS.SESSION_ID];
        connectWebSocket(sessionId);
    }
    
    // Load previous chat history
    if (result[STORAGE_KEYS.CHAT_HISTORY] && result[STORAGE_KEYS.CHAT_HISTORY].length > 0) {
        loadChatHistory(result[STORAGE_KEYS.CHAT_HISTORY]);
    }
});

// Save message to storage
async function saveMessageToStorage(message, sender, timestamp = null) {
    return new Promise((resolve) => {
        chrome.storage.local.get([STORAGE_KEYS.CHAT_HISTORY], (result) => {
            let history = result[STORAGE_KEYS.CHAT_HISTORY] || [];
            
            const messageObj = {
                id: Date.now() + Math.random(),
                text: message,
                sender: sender,
                timestamp: timestamp || new Date().toLocaleTimeString(),
                date: new Date().toISOString()
            };
            
            history.push(messageObj);
            
            // Keep only last MAX_STORED_MESSAGES
            if (history.length > MAX_STORED_MESSAGES) {
                history = history.slice(-MAX_STORED_MESSAGES);
            }
            
            chrome.storage.local.set({ [STORAGE_KEYS.CHAT_HISTORY]: history }, () => {
                resolve();
            });
        });
    });
}

// Clear chat history
function clearChatHistory() {
    return new Promise((resolve) => {
        chrome.storage.local.set({ [STORAGE_KEYS.CHAT_HISTORY]: [] }, () => {
            resolve();
        });
    });
}

// Load chat history into UI
function loadChatHistory(history) {
    if (!history || history.length === 0) return;
    
    // Clear existing messages (except welcome message)
    while (messagesContainer.children.length > 0) {
        messagesContainer.removeChild(messagesContainer.firstChild);
    }
    
    // Load messages from storage
    history.forEach(msg => {
        addMessageToUI(msg.text, msg.sender, msg.timestamp);
    });
    
    // Add welcome message if history is empty
    if (history.length === 0) {
        addWelcomeMessage();
    }
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Add message to UI without saving (used when loading history)
function addMessageToUI(text, sender, timeString = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    
    // Clean the text
    let cleanText = text;
    if (sender === 'assistant') {
        cleanText = text.replace(/[^\x20-\x7E\n\r\t]/g, '');
    }
    bubble.textContent = cleanText;
    
    const timeSpan = document.createElement('div');
    timeSpan.className = 'message-time';
    timeSpan.textContent = timeString || new Date().toLocaleTimeString();
    
    messageDiv.appendChild(bubble);
    messageDiv.appendChild(timeSpan);
    
    messagesContainer.appendChild(messageDiv);
}

// Add welcome message
function addWelcomeMessage() {
    const welcomeMsg = "👋 Hi! I'm your Mulungushi University assistant. Ask me about schools, fees, programs, or anything about the university, I'm here to help";
    addMessageToUI(welcomeMsg, 'assistant', 'Just now');
    // Save welcome message to storage
    saveMessageToStorage(welcomeMsg, 'assistant', 'Just now');
}

function addStatusMessage(text, type = 'info') {
    const statusDiv = document.createElement('div');
    statusDiv.className = `status-message ${type === 'error' ? 'error' : (type === 'success' ? 'success' : '')}`;
    
    const time = new Date().toLocaleTimeString();
    statusDiv.textContent = `[${time}] ${text}`;
    
    statusContainer.appendChild(statusDiv);
    statusDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Auto-remove old messages
    while (statusContainer.children.length > 10) {
        statusContainer.removeChild(statusContainer.firstChild);
    }
}

function connectWebSocket(sessionId) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
    }
    
    ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);
    
    ws.onopen = () => {
        console.log('WebSocket connected');
        addStatusMessage('🔌 Real-time connection established', 'success');
    };
    
    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            addStatusMessage(data.message, data.type === 'error' ? 'error' : (data.type === 'success' ? 'success' : 'info'));
        } catch (e) {
            console.error('Error parsing WebSocket message:', e);
        }
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        addStatusMessage('⚠️ Real-time connection lost', 'error');
    };
    
    ws.onclose = () => {
        console.log('WebSocket disconnected');
    };
}

function addMessage(text, sender, metadata = null) {
    // Add to UI
    addMessageToUI(text, sender);
    
    // Save to storage
    saveMessageToStorage(text, sender);
}

function showTypingIndicator() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant';
    loadingDiv.id = 'typing-indicator';
    
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';
    
    loadingDiv.appendChild(indicator);
    messagesContainer.appendChild(loadingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
}

async function sendMessage() {
    const query = input.value.trim();
    if (!query) return;
    
    addMessage(query, 'user');
    input.value = '';
    
    addStatusMessage(`📝 Processing: "${query.substring(0, 50)}..."`, 'info');
    showTypingIndicator();
    
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        addStatusMessage(`🔍 Searching...`, 'info');
        
        const response = await fetch('http://localhost:8000/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                session_id: sessionId,
                current_url: tab?.url || ''
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.session_id) {
            if (!sessionId || sessionId !== data.session_id) {
                sessionId = data.session_id;
                connectWebSocket(sessionId);
                chrome.storage.local.set({ [STORAGE_KEYS.SESSION_ID]: sessionId });
            }
        }
        
        addStatusMessage(`✅ Response received`, 'success');
        hideTypingIndicator();
        
        // Display and save response
        addMessage(data.response || 'No response received', 'assistant');
        
    } catch (error) {
        console.error('Error:', error);
        addStatusMessage(`❌ Error: ${error.message}`, 'error');
        hideTypingIndicator();
        const errorMsg = `Sorry, I encountered an error: ${error.message}. Make sure the backend is running.`;
        addMessage(errorMsg, 'assistant');
    }
}

// Clear chat button - add this to your popup.html
function addClearChatButton() {
    const header = document.querySelector('.header');
    if (header && !document.getElementById('clearChatBtn')) {
        const clearBtn = document.createElement('button');
        clearBtn.id = 'clearChatBtn';
        clearBtn.innerHTML = '🗑️ Clear';
        clearBtn.style.cssText = `
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 11px;
            margin-top: 8px;
        `;
        clearBtn.onclick = async () => {
            if (confirm('Clear all chat history?')) {
                await clearChatHistory();
                // Clear UI
                while (messagesContainer.children.length > 0) {
                    messagesContainer.removeChild(messagesContainer.firstChild);
                }
                addWelcomeMessage();
                addStatusMessage('Chat history cleared', 'success');
            }
        };
        header.appendChild(clearBtn);
    }
}

// Event listeners
sendBtn.addEventListener('click', sendMessage);
input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

input.focus();

// Add clear button to UI
setTimeout(addClearChatButton, 100);

// Periodic connection check
setInterval(async () => {
    try {
        const response = await fetch('http://localhost:8000/api/health');
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            if (response.ok) {
                statusElement.innerHTML = '🟢 Connected';
                statusElement.style.background = '#4CAF50';
                statusElement.style.color = 'white';
            } else {
                statusElement.innerHTML = '🟡 Connecting...';
                statusElement.style.background = '#ffc107';
                statusElement.style.color = '#333';
            }
        }
    } catch {
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            statusElement.innerHTML = '🔴 Disconnected';
            statusElement.style.background = '#dc3545';
            statusElement.style.color = 'white';
        }
    }
}, 5000);