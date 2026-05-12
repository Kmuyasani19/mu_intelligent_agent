from fastapi import WebSocket
from typing import List, Dict
from datetime import datetime

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        print(f"🔌 WebSocket connected for session: {session_id}")
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        print(f"🔌 WebSocket disconnected for session: {session_id}")
    
    async def send_status(self, session_id: str, message: str, status_type: str = "info"):
        """Send status update to specific session"""
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json({
                        "session_id": session_id,
                        "message": message,
                        "type": status_type,
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    print(f"Error sending WebSocket message: {e}")
    
    async def broadcast(self, message: str, status_type: str = "info"):
        """Send to all connected sessions"""
        for session_id in self.active_connections:
            await self.send_status(session_id, message, status_type)

# Global instance
manager = ConnectionManager()