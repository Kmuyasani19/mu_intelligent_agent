from typing import TypedDict, List, Dict, Any, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field

# -------------------- Message Models --------------------
class Message(BaseModel):
    """Individual message in conversation"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

# -------------------- Intent Models --------------------
class Intent(BaseModel):
    """LLM-classified intent"""
    type: Literal[
        "student_data",      # Personal info (grades, balance, courses)
        "navigation",        # Navigate portal pages
        "public_info",       # University information (programs, fees)
        "memory_query",      # Ask about conversation history
        "general_chat",      # Greetings, small talk, off-topic
        "unknown"            # Couldn't determine
    ]
    confidence: float = Field(ge=0.0, le=1.0)
    entities: Dict[str, Any] = Field(default_factory=dict)
    requires_login: bool = False

# -------------------- Action Models --------------------
class ToolCall(BaseModel):
    """A tool the agent can execute"""
    tool_name: str
    arguments: Dict[str, Any]
    reasoning: str

# -------------------- Agent State --------------------
class AgentState(TypedDict):
    """Main state for the LangGraph agent"""
    # Conversation
    session_id: str
    messages: List[Message]
    
    # Current query
    current_query: str
    
    # LLM decisions
    intent: Optional[Intent]
    tool_calls: List[ToolCall]
    
    # Results
    action_results: List[Dict[str, Any]]
    final_response: str
    
    # Portal session
    is_logged_in: bool
    pending_intent: Optional[Intent]
    
    # Metadata
    errors: List[str]
    timestamp: str