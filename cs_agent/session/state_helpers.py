"""
State Helper Functions

Utility functions for reading and updating session state from tools.
These work with ToolContext to provide a clean API for state management.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from google.adk.tools.tool_context import ToolContext


# ============================================================================
# State Reading Helpers
# ============================================================================

def get_state_value(tool_context: ToolContext, key: str, default: Any = None) -> Any:
    """
    Safely get a value from session state.
    
    Args:
        tool_context: The ToolContext provided to the tool
        key: State key to retrieve
        default: Default value if key doesn't exist
    
    Returns:
        The state value or default
    """
    return tool_context.state.get(key, default)


def get_issue_context(tool_context: ToolContext) -> Optional[Dict]:
    """Get the current issue context from state."""
    return get_state_value(tool_context, "issue", None)


def get_attempted_solutions(tool_context: ToolContext) -> List[Dict]:
    """Get list of attempted solutions."""
    return get_state_value(tool_context, "attempted_solutions", [])


def get_conversation_status(tool_context: ToolContext) -> str:
    """Get current conversation status."""
    return get_state_value(tool_context, "status", "new")


def get_current_agent(tool_context: ToolContext) -> str:
    """Get the currently active agent."""
    return get_state_value(tool_context, "current_agent", "orchestrator")


def get_turn_count(tool_context: ToolContext) -> int:
    """Get the number of conversation turns."""
    return get_state_value(tool_context, "turn_count", 0)


def get_escalation_count(tool_context: ToolContext) -> int:
    """Get number of times escalation has been attempted."""
    return get_state_value(tool_context, "escalation_count", 0)


def is_user_frustrated(tool_context: ToolContext) -> bool:
    """Check if user has shown signs of frustration."""
    level = get_state_value(tool_context, "user_frustration_level", "normal")
    return level in ["frustrated", "angry"]


def get_user_info(tool_context: ToolContext) -> Dict:
    """Get stored user information."""
    return {
        "user_id": get_state_value(tool_context, "user_id"),
        "user_name": get_state_value(tool_context, "user_name"),
        "user_plan": get_state_value(tool_context, "user_plan")
    }


# ============================================================================
# State Writing Helpers
# ============================================================================

def update_state(tool_context: ToolContext, updates: Dict) -> None:
    """
    Update multiple state values at once.
    
    Args:
        tool_context: The ToolContext provided to the tool
        updates: Dictionary of key-value pairs to update
    """
    for key, value in updates.items():
        tool_context.state[key] = value
    
    # Always update last_activity timestamp
    tool_context.state["last_activity"] = datetime.now().isoformat()


def set_issue_context(
    tool_context: ToolContext,
    category: str,
    priority: str,
    confidence: float,
    description_summary: str,
    error_type: Optional[str] = None,
    keywords: Optional[List[str]] = None
) -> None:
    """
    Set or update the issue context in state.
    
    Args:
        tool_context: The ToolContext
        category: Issue category (e.g., "integration", "billing")
        priority: Priority level
        confidence: Classification confidence (0-1)
        description_summary: Brief summary of the issue
        error_type: Type of error if identified
        keywords: Relevant keywords found
    """
    issue = {
        "category": category,
        "priority": priority,
        "confidence": confidence,
        "description_summary": description_summary,
        "error_type": error_type,
        "keywords": keywords or [],
        "classified_at": datetime.now().isoformat()
    }
    tool_context.state["issue"] = issue
    tool_context.state["last_activity"] = datetime.now().isoformat()
    
    print(f"--- State: Issue context set - {category} ({priority}) ---")


def add_attempted_solution(
    tool_context: ToolContext,
    solution: str,
    agent: str,
    result: str = "pending",
    user_feedback: Optional[str] = None
) -> None:
    """
    Record an attempted solution in state.
    
    Args:
        tool_context: The ToolContext
        solution: Description of the solution attempted
        agent: Which agent provided the solution
        result: Outcome - "helpful", "not_helpful", "partially_helpful", "pending"
        user_feedback: Any feedback from user
    """
    solutions = tool_context.state.get("attempted_solutions", [])
    
    attempt = {
        "solution": solution,
        "agent": agent,
        "result": result,
        "user_feedback": user_feedback,
        "timestamp": datetime.now().isoformat()
    }
    
    solutions.append(attempt)
    tool_context.state["attempted_solutions"] = solutions
    tool_context.state["solution_attempts_count"] = len(solutions)
    tool_context.state["last_activity"] = datetime.now().isoformat()
    
    print(f"--- State: Added solution attempt #{len(solutions)} by {agent} ---")


def update_solution_result(
    tool_context: ToolContext,
    result: str,
    user_feedback: Optional[str] = None
) -> None:
    """
    Update the result of the most recent solution attempt.
    
    Args:
        tool_context: The ToolContext
        result: Outcome - "helpful", "not_helpful", "partially_helpful"
        user_feedback: Optional user feedback
    """
    solutions = tool_context.state.get("attempted_solutions", [])
    
    if solutions:
        solutions[-1]["result"] = result
        if user_feedback:
            solutions[-1]["user_feedback"] = user_feedback
        tool_context.state["attempted_solutions"] = solutions
        tool_context.state["last_activity"] = datetime.now().isoformat()
        
        print(f"--- State: Updated last solution result to '{result}' ---")


def set_conversation_status(tool_context: ToolContext, status: str) -> None:
    """
    Update conversation status.
    
    Args:
        tool_context: The ToolContext
        status: New status - "new", "in_progress", "awaiting_user", "resolved", "escalated"
    """
    tool_context.state["status"] = status
    tool_context.state["last_activity"] = datetime.now().isoformat()
    print(f"--- State: Conversation status → {status} ---")


def set_current_agent(tool_context: ToolContext, agent: str) -> None:
    """
    Record which agent is currently handling the conversation.
    
    Args:
        tool_context: The ToolContext
        agent: Agent name - "orchestrator", "triage", "specialist", "escalation"
    """
    tool_context.state["current_agent"] = agent
    tool_context.state["last_activity"] = datetime.now().isoformat()
    print(f"--- State: Current agent → {agent} ---")


def increment_turn_count(tool_context: ToolContext) -> int:
    """Increment and return the turn count."""
    count = tool_context.state.get("turn_count", 0) + 1
    tool_context.state["turn_count"] = count
    return count


def increment_clarifying_questions(tool_context: ToolContext) -> int:
    """Increment and return clarifying questions count."""
    count = tool_context.state.get("clarifying_questions_asked", 0) + 1
    tool_context.state["clarifying_questions_asked"] = count
    return count


def set_escalation_requested(tool_context: ToolContext, ticket_id: Optional[str] = None) -> None:
    """
    Mark that escalation has been requested/completed.
    
    Args:
        tool_context: The ToolContext
        ticket_id: The created ticket ID if available
    """
    tool_context.state["escalation_requested"] = True
    tool_context.state["escalation_count"] = tool_context.state.get("escalation_count", 0) + 1
    tool_context.state["status"] = "escalated"
    
    if ticket_id:
        tool_context.state["ticket_id"] = ticket_id
    
    tool_context.state["last_activity"] = datetime.now().isoformat()
    print(f"--- State: Escalation recorded (ticket: {ticket_id}) ---")


def set_user_info(
    tool_context: ToolContext,
    user_name: Optional[str] = None,
    user_plan: Optional[str] = None,
    user_id: Optional[str] = None,
    recent_tickets: Optional[List[str]] = None,
) -> None:
    """
    Store user information in state.
    
    Args:
        tool_context: The ToolContext
        user_name: User's name
        user_plan: User's subscription plan
        user_id: User identifier
    """
    if user_name:
        tool_context.state["user_name"] = user_name
    if user_plan:
        tool_context.state["user_plan"] = user_plan
    if user_id:
        tool_context.state["user_id"] = user_id
    if recent_tickets:
        tool_context.state["recent_tickets"] = recent_tickets
        
    tool_context.state["user_context_loaded"] = True
    tool_context.state["last_activity"] = datetime.now().isoformat()
    
    print(f"--- State: User info stored - {user_name} ({user_plan}) ---")


def detect_frustration(tool_context: ToolContext, user_message: str) -> str:
    """
    Detect user frustration level from message content.
    Updates state and returns the detected level.
    
    Args:
        tool_context: The ToolContext
        user_message: The user's message
    
    Returns:
        Frustration level: "normal", "frustrated", "angry"
    """
    message_lower = user_message.lower()
    
    # Angry indicators
    angry_words = ["ridiculous", "unacceptable", "terrible", "worst", "lawsuit", 
                   "refund", "cancel", "angry", "furious", "outraged"]
    
    # Frustrated indicators
    frustrated_words = ["frustrated", "annoying", "still not working", "tried everything",
                       "waste of time", "useless", "doesn't help", "hours", "days",
                       "again", "still", "keeps happening"]
    
    level = "normal"
    
    if any(word in message_lower for word in angry_words):
        level = "angry"
    elif any(word in message_lower for word in frustrated_words):
        level = "frustrated"
    
    # Check for caps (shouting)
    caps_ratio = sum(1 for c in user_message if c.isupper()) / max(len(user_message), 1)
    if caps_ratio > 0.5 and len(user_message) > 10:
        level = "angry"
    
    tool_context.state["user_frustration_level"] = level
    
    if level != "normal":
        print(f"--- State: User frustration detected - {level} ---")
    
    return level


def mark_triage_complete(tool_context: ToolContext) -> None:
    """Mark that triage phase is complete."""
    tool_context.state["triage_complete"] = True
    print("--- State: Triage marked complete ---")


def mark_specialist_engaged(tool_context: ToolContext) -> None:
    """Mark that specialist has been engaged."""
    tool_context.state["specialist_engaged"] = True
    print("--- State: Specialist engaged ---")


def record_kb_search(tool_context: ToolContext, query: str) -> None:
    """Record a knowledge base search."""
    tool_context.state["last_kb_search"] = query
    tool_context.state["last_activity"] = datetime.now().isoformat()


def record_similar_tickets(tool_context: ToolContext, ticket_ids: List[str]) -> None:
    """Record found similar tickets."""
    tool_context.state["last_similar_tickets"] = ticket_ids


def mark_system_status_checked(tool_context: ToolContext) -> None:
    """Mark that system status has been checked."""
    tool_context.state["system_status_checked"] = True


# ============================================================================
# State Summary Helpers
# ============================================================================

def get_state_summary(tool_context: ToolContext) -> Dict:
    """
    Get a summary of the current state for logging/debugging.
    
    Returns:
        Dictionary with key state information
    """
    return {
        "status": get_conversation_status(tool_context),
        "current_agent": get_current_agent(tool_context),
        "turn_count": get_turn_count(tool_context),
        "issue_category": (get_issue_context(tool_context) or {}).get("category"),
        "solutions_tried": len(get_attempted_solutions(tool_context)),
        "escalation_count": get_escalation_count(tool_context),
        "user_frustrated": is_user_frustrated(tool_context),
        "ticket_id": get_state_value(tool_context, "ticket_id")
    }


def should_escalate(tool_context: ToolContext, max_attempts: int = 2) -> bool:
    """
    Determine if the conversation should be escalated to human support.
    
    Args:
        tool_context: The ToolContext
        max_attempts: Maximum solution attempts before escalation
    
    Returns:
        True if escalation is recommended
    """
    # Check solution attempt count
    solutions = get_attempted_solutions(tool_context)
    failed_attempts = sum(1 for s in solutions if s.get("result") == "not_helpful")
    
    if failed_attempts >= max_attempts:
        return True
    
    # Check if user requested escalation
    if get_state_value(tool_context, "escalation_requested", False):
        return True
    
    # Check frustration level
    if get_state_value(tool_context, "user_frustration_level") == "angry":
        return True
    
    return False


def get_escalation_context(tool_context: ToolContext) -> Dict:
    """
    Gather all context needed for escalation ticket.
    
    Returns:
        Dictionary with full escalation context
    """
    issue = get_issue_context(tool_context) or {}
    solutions = get_attempted_solutions(tool_context)
    
    return {
        "issue_summary": issue.get("description_summary", "No summary available"),
        "category": issue.get("category", "unknown"),
        "priority": issue.get("priority", "medium"),
        "error_type": issue.get("error_type"),
        "attempted_solutions": [
            {
                "solution": s["solution"],
                "result": s["result"],
                "agent": s["agent"]
            }
            for s in solutions
        ],
        "turn_count": get_turn_count(tool_context),
        "user_info": get_user_info(tool_context),
        "frustration_level": get_state_value(tool_context, "user_frustration_level", "normal")
    }
