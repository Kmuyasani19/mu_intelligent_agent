// Background service worker
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'CHAT_QUERY') {
    handleChatQuery(message.query, message.sessionId, message.currentUrl)
      .then(sendResponse);
    return true;
  }
});

async function handleChatQuery(query, sessionId, currentUrl) {
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
    return { success: true, response: data.response, sessionId: data.session_id };
  } catch (error) {
    console.error('API Error:', error);
    return { success: false, error: error.message };
  }
}