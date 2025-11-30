"""
Session State Management

Defines the structure and helpers for managing conversation state
across the multi-agent support system.

State is accessed via ToolContext in tools and persists across turns.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum


class ConversationStatus(str, Enum):
    """Status of the support conversation."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    AWAITING_USER = "awaiting_user"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class IssuePriority(str, Enum):
    """Priority levels for issues."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AttemptedSolution:
    """Record of a solution attempt."""
    solution: str
    timestamp: str
    agent: str
    result: str  # "helpful", "not_helpful", "partially_helpful"
    user_feedback: Optional[str] = None


@dataclass
class IssueContext:
    """Structured information about the user's issue."""
    category: Optional[str] = None
    priority: Optional[str] = None
    confidence: float = 0.0
    description_summary: Optional[str] = None
    error_type: Optional[str] = None
    affected_service: Optional[str] = None
    keywords: List[str] = field(default_factory=list)


@dataclass 
class SessionState:
    """
    Complete session state structure.
    
    This represents all the stateful information tracked during
    a support conversation.
    """
    # Conversation metadata
    conversation_id: str = ""
    user_id: str = ""
    started_at: str = ""
    last_activity: str = ""
    
    # Conversation status
    status: str = ConversationStatus.NEW.value
    current_agent: str = "orchestrator"
    turn_count: int = 0
    
    # Issue tracking
    issue: Optional[Dict] = None
    
    # Solution tracking
    attempted_solutions: List[Dict] = field(default_factory=list)
    solution_attempts_count: int = 0
    
    # Escalation tracking
    escalation_count: int = 0
    escalation_requested: bool = False
    ticket_id: Optional[str] = None
    
    # Agent-specific state
    triage_complete: bool = False
    specialist_engaged: bool = False
    clarifying_questions_asked: int = 0
    
    # Context from tools
    last_kb_search: Optional[str] = None
    last_similar_tickets: List[str] = field(default_factory=list)
    system_status_checked: bool = False
    user_context_loaded: bool = False
    
    # User preferences/context
    user_name: Optional[str] = None
    user_plan: Optional[str] = None
    user_frustration_level: str = "normal"  # normal, frustrated, angry
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for session storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SessionState':
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# Initial state template
INITIAL_STATE = {
    "conversation_id": "",
    "user_id": "",
    "started_at": "",
    "last_activity": "",
    "status": "new",
    "current_agent": "orchestrator",
    "turn_count": 0,
    "issue": None,
    "attempted_solutions": [],
    "solution_attempts_count": 0,
    "escalation_count": 0,
    "escalation_requested": False,
    "ticket_id": None,
    "triage_complete": False,
    "specialist_engaged": False,
    "clarifying_questions_asked": 0,
    "last_kb_search": None,
    "last_similar_tickets": [],
    "system_status_checked": False,
    "user_context_loaded": False,
    "user_name": None,
    "user_plan": None,
    "user_frustration_level": "normal"
}


def get_initial_state(user_id: str = "", conversation_id: str = "") -> Dict:
    """
    Get a fresh initial state dictionary.
    
    Args:
        user_id: User identifier
        conversation_id: Conversation/session identifier
    
    Returns:
        Dictionary with initial state values
    """
    state = INITIAL_STATE.copy()
    state["user_id"] = user_id
    state["conversation_id"] = conversation_id
    state["started_at"] = datetime.now().isoformat()
    state["last_activity"] = datetime.now().isoformat()
    return state
