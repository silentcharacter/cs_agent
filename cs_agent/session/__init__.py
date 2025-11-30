"""
Session management package for Tech Support Escalation System

Provides state schema and helper functions for managing
conversation state across the multi-agent system.
"""

from .state_schema import (
    SessionState,
    IssueContext,
    AttemptedSolution,
    ConversationStatus,
    IssuePriority,
    INITIAL_STATE,
    get_initial_state
)

from .state_helpers import (
    # Reading helpers
    get_state_value,
    get_issue_context,
    get_attempted_solutions,
    get_conversation_status,
    get_current_agent,
    get_turn_count,
    get_escalation_count,
    is_user_frustrated,
    get_user_info,
    get_state_summary,
    
    # Writing helpers
    update_state,
    set_issue_context,
    add_attempted_solution,
    update_solution_result,
    set_conversation_status,
    set_current_agent,
    increment_turn_count,
    increment_clarifying_questions,
    set_escalation_requested,
    set_user_info,
    detect_frustration,
    mark_triage_complete,
    mark_specialist_engaged,
    record_kb_search,
    record_similar_tickets,
    mark_system_status_checked,
    
    # Decision helpers
    should_escalate,
    get_escalation_context
)

__all__ = [
    # Schema
    "SessionState",
    "IssueContext", 
    "AttemptedSolution",
    "ConversationStatus",
    "IssuePriority",
    "INITIAL_STATE",
    "get_initial_state",
    
    # Reading
    "get_state_value",
    "get_issue_context",
    "get_attempted_solutions",
    "get_conversation_status",
    "get_current_agent",
    "get_turn_count",
    "get_escalation_count",
    "is_user_frustrated",
    "get_user_info",
    "get_state_summary",
    
    # Writing
    "update_state",
    "set_issue_context",
    "add_attempted_solution",
    "update_solution_result",
    "set_conversation_status",
    "set_current_agent",
    "increment_turn_count",
    "increment_clarifying_questions",
    "set_escalation_requested",
    "set_user_info",
    "detect_frustration",
    "mark_triage_complete",
    "mark_specialist_engaged",
    "record_kb_search",
    "record_similar_tickets",
    "mark_system_status_checked",
    
    # Decisions
    "should_escalate",
    "get_escalation_context"
]
