import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

STORAGE_FILE = Path("./conversations.json")

class ConversationStore:
    """Persistent conversation storage"""
    
    def __init__(self):
        self._storage: Dict[str, List[Dict]] = {}
        self._load()
    
    def _load(self):
        if STORAGE_FILE.exists():
            try:
                with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                    self._storage = json.load(f)
                print(f"📁 Loaded {len(self._storage)} conversation histories")
            except Exception as e:
                print(f"Error loading conversations: {e}")
    
    def _save(self):
        try:
            with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._storage, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Error saving conversations: {e}")
    
    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self._storage:
            self._storage[session_id] = []
        self._storage[session_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        # Keep only last 50 messages
        if len(self._storage[session_id]) > 50:
            self._storage[session_id] = self._storage[session_id][-50:]
        self._save()
    
    def get_messages(self, session_id: str, limit: int = 20) -> List[Dict]:
        messages = self._storage.get(session_id, [])
        return messages[-limit:]
    
    def get_first_user_message(self, session_id: str) -> Optional[str]:
        messages = self._storage.get(session_id, [])
        for msg in messages:
            if msg.get('role') == 'user':
                return msg.get('content')
        return None
    
    def get_recent_context(self, session_id: str, limit: int = 3) -> str:
        messages = self._storage.get(session_id, [])
        recent = messages[-limit:] if messages else []
        context = ""
        for msg in recent:
            role = "User" if msg.get('role') == 'user' else "Assistant"
            context += f"{role}: {msg.get('content', '')}\n"
        return context

# Singleton
conversation_store = ConversationStore()