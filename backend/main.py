from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

from agent.state import AgentState, Message
from agent.graph import get_agent
from memory.conversation_store import conversation_store
from websocket_manager import manager

app = FastAPI(title="Mulungushi University Intelligent Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    current_url: str = ""

class ChatResponse(BaseModel):
    session_id: str
    response: str
    error: Optional[str] = None

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)

@app.post("/api/chat")
async def chat(request: ChatRequest):
    print(f"\n📨 Received: {request.query}")
    
    session_id = request.session_id or str(uuid.uuid4())
    
    # Get conversation history
    messages_data = conversation_store.get_messages(session_id, limit=20)
    messages = [Message(**msg) for msg in messages_data] if messages_data else []
    
    # Initialize agent state
    initial_state: AgentState = {
        "session_id": session_id,
        "messages": messages,
        "current_query": request.query,
        "intent": None,
        "tool_calls": [],
        "action_results": [],
        "final_response": "",
        "is_logged_in": False,
        "pending_intent": None,
        "errors": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # Run agent
    agent = get_agent()
    final_state = await agent.ainvoke(initial_state)
    
    # Save conversation
    conversation_store.add_message(session_id, "user", request.query)
    conversation_store.add_message(session_id, "assistant", final_state["final_response"])
    
    return ChatResponse(
        session_id=session_id,
        response=final_state["final_response"],
        error=final_state["errors"][0] if final_state["errors"] else None
    )

@app.get("/api/health")
async def health():
    return {"status": "healthy", "sessions": len(conversation_store._storage)}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Mulungushi University Intelligent Agent...")
    uvicorn.run(app, host="0.0.0.0", port=8000)