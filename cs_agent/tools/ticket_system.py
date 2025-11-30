"""
Ticket System Tools

Handles creation, assignment, and searching of support tickets.
Uses mock data for MVP - can be replaced with real ticketing system.

Uses ToolContext to:
- Store ticket ID when created
- Record escalation in session state
- Track similar tickets found
- Build escalation context from session history
"""

from typing import Dict, List, Optional
from datetime import datetime
from google.adk.tools.tool_context import ToolContext
import random
from ..session.state_helpers import record_similar_tickets

# Mock ticket database
TICKET_DATABASE = {
    "TICKET-789": {
        "id": "TICKET-789",
        "title": "Cannot connect to API",
        "category": "integration",
        "priority": "high",
        "status": "resolved",
        "assigned_team": "integration_team",
        "created_at": "2024-12-20T10:00:00Z",
        "resolved_at": "2024-12-20T14:30:00Z",
        "description": "User unable to authenticate with API using provided key",
        "resolution": "API key was for test environment, provided production key"
    },
    "TICKET-456": {
        "id": "TICKET-456",
        "title": "Webhook events not received",
        "category": "integration",
        "priority": "high",
        "status": "resolved",
        "assigned_team": "integration_team",
        "created_at": "2024-11-15T08:00:00Z",
        "resolved_at": "2024-11-15T12:00:00Z",
        "description": "Customer's webhook endpoint stopped receiving events after API v2 update",
        "resolution": "Webhook secret was regenerated during API update. Customer needed to update their verification code with new secret."
    },
    "TICKET-234": {
        "id": "TICKET-234",
        "title": "Billing discrepancy",
        "category": "billing",
        "priority": "medium",
        "status": "resolved",
        "assigned_team": "finance_team",
        "created_at": "2024-10-05T14:00:00Z",
        "resolved_at": "2024-10-06T09:00:00Z",
        "description": "Customer charged twice for the same month",
        "resolution": "Duplicate charge refunded, billing system bug fixed"
    },
    "TICKET-567": {
        "id": "TICKET-567",
        "title": "Performance degradation on dashboard",
        "category": "performance",
        "priority": "medium",
        "status": "resolved",
        "assigned_team": "infrastructure_team",
        "created_at": "2024-11-20T16:00:00Z",
        "resolved_at": "2024-11-21T10:00:00Z",
        "description": "Dashboard loading very slowly, 10+ seconds per page",
        "resolution": "Database index added, caching layer implemented"
    }
}

# Team assignments
TEAM_ASSIGNMENTS = {
    "password_reset": "account_team",
    "billing": "finance_team",
    "order": "order_fullfillment_team",
    "bug_report": "engineering_team",
    "feature_question": "product_team",
    "performance": "infrastructure_team",
    "security": "security_team",
    "unknown": "general_support"
}

# Response time SLAs (in hours)
RESPONSE_SLAS = {
    "critical": 1,
    "high": 4,
    "medium": 8,
    "low": 24
}


def _generate_ticket_id() -> str:
    """Generate a unique ticket ID."""
    number = random.randint(1000, 9999)
    return f"TICKET-{number}"


def create_ticket(
    summary: str,
    category: str,
    priority: str,
    description: str,
    tool_context: ToolContext,
    attempted_solutions: Optional[List[str]] = None,
    user_id: Optional[str] = None
) -> Dict:
    """
    Creates a new support ticket for human agent review.
    Records the escalation in session state.
    
    Args:
        summary: Brief summary of the issue (e.g., "Webhook signature verification failing")
        category: Issue category (e.g., "integration", "billing", "bug_report")
        priority: Priority level ("low", "medium", "high", "critical")
        description: Detailed description including context and error messages
        tool_context: ToolContext for session state access
        attempted_solutions: Optional list of solutions already tried
        user_id: Optional user identifier
    
    Returns:
        dict: Contains:
            - status: 'success' or 'error'
            - ticket_id: The created ticket ID
            - assigned_team: Team assigned to handle the ticket
            - estimated_response: Expected response time based on priority
    """
    print("--- Tool: create_ticket called ---")
    print(f"--- Tool: Creating ticket - Category: {category}, Priority: {priority} ---")
    
    # Import state helpers
    from ..session.state_helpers import set_escalation_requested, get_attempted_solutions as get_solutions
    
    ticket_id = _generate_ticket_id()
    
    # Ensure ticket ID is unique
    while ticket_id in TICKET_DATABASE:
        ticket_id = _generate_ticket_id()
    
    # Determine assigned team
    assigned_team = TEAM_ASSIGNMENTS.get(category, "general_support")
    
    # Get response SLA
    response_hours = RESPONSE_SLAS.get(priority, 24)
    
    # Get attempted solutions from state if not provided
    if not attempted_solutions:
        state_solutions = get_solutions(tool_context)
        attempted_solutions = [s.get("solution", "") for s in state_solutions]
    
    # Get user_id from state if not provided
    if not user_id:
        user_id = tool_context.state.get("user_id")
    
    # Create the ticket
    ticket = {
        "id": ticket_id,
        "title": summary,
        "category": category,
        "priority": priority,
        "status": "open",
        "assigned_team": assigned_team,
        "created_at": datetime.now().isoformat(),
        "description": description,
        "attempted_solutions": attempted_solutions or [],
        "user_id": user_id,
        "frustration_level": tool_context.state.get("user_frustration_level", "normal"),
        "turn_count": tool_context.state.get("turn_count", 0)
    }
    
    # Store in mock database
    TICKET_DATABASE[ticket_id] = ticket
    
    # Record escalation in session state
    set_escalation_requested(tool_context, ticket_id)
    
    result = {
        "status": "success",
        "ticket_id": ticket_id,
        "assigned_team": assigned_team,
        "estimated_response": f"{response_hours} hour(s)",
        "priority": priority,
        "message": f"Ticket {ticket_id} created successfully and assigned to {assigned_team}. "
                   f"Expected response within {response_hours} hour(s)."
    }
    
    print(f"--- Tool: Created ticket {ticket_id}, assigned to {assigned_team} ---")
    print(f"--- State: Escalation recorded with ticket {ticket_id} ---")
    return result


def assign_to_team(category: str, priority: str, tool_context: ToolContext) -> Dict:
    """
    Determines which team should handle a ticket based on category and priority.
    
    Args:
        category: Issue category (e.g., "integration", "billing")
        priority: Priority level (e.g., "high", "critical")
        tool_context: ToolContext for session state access
    
    Returns:
        dict: Contains:
            - status: 'success'
            - team: Assigned team name
            - response_sla: Expected response time
            - escalation_path: Next level of escalation if needed
    """
    print(f"--- Tool: assign_to_team called for category: {category}, priority: {priority} ---")
    
    team = TEAM_ASSIGNMENTS.get(category, "general_support")
    response_hours = RESPONSE_SLAS.get(priority, 24)
    
    # Define escalation paths
    escalation_paths = {
        "account_team": "customer_success_manager",
        "finance_team": "finance_director",
        "engineering_team": "engineering_lead",
        "product_team": "product_manager",
        "integration_team": "technical_architect",
        "infrastructure_team": "sre_lead",
        "security_team": "security_officer",
        "general_support": "support_manager"
    }
    
    result = {
        "status": "success",
        "team": team,
        "team_description": f"The {team.replace('_', ' ').title()} handles {category} issues",
        "response_sla": f"{response_hours} hours",
        "escalation_path": escalation_paths.get(team, "support_manager")
    }
    
    # Add urgency note for critical/high priority
    if priority in ["critical", "high"]:
        result["urgency_note"] = f"This is a {priority} priority issue - team will be notified immediately"
    
    print(f"--- Tool: Assigned to {team} with {response_hours}h SLA ---")
    return result


def search_similar_tickets(description: str, tool_context: ToolContext, category: Optional[str] = None, limit: int = 3) -> Dict:
    """
    Searches for previously resolved tickets similar to the current issue.
    Records found tickets in session state.
    
    Args:
        description: Description of the current issue
        tool_context: ToolContext for session state access
        category: Optional category filter
        limit: Maximum number of results to return (default 3)
    
    Returns:
        dict: Contains:
            - status: 'success'
            - similar_tickets: List of similar resolved tickets with their resolutions
            - total_found: Number of matches found
    """
    print("--- Tool: search_similar_tickets called ---")
    print(f"--- Tool: Searching for issues similar to: '{description[:100]}...' ---")
    
    description_lower = description.lower()
    keywords = set(description_lower.split())
    
    scored_tickets = []
    
    for ticket_id, ticket in TICKET_DATABASE.items():
        # Only include resolved tickets
        if ticket["status"] != "resolved":
            continue
        
        # Filter by category if specified
        if category and ticket["category"] != category:
            continue
        
        score = 0
        
        # Check title match
        title_lower = ticket["title"].lower()
        for word in keywords:
            if len(word) > 3 and word in title_lower:
                score += 3
        
        # Check description match
        desc_lower = ticket.get("description", "").lower()
        for word in keywords:
            if len(word) > 3 and word in desc_lower:
                score += 1
        
        # Boost for same category
        if category and ticket["category"] == category:
            score += 2
        
        if score > 0:
            scored_tickets.append((score, ticket))
    
    # Sort by score and limit results
    scored_tickets.sort(key=lambda x: x[0], reverse=True)
    top_tickets = scored_tickets[:limit]
    
    similar_tickets = []
    for score, ticket in top_tickets:
        similar_tickets.append({
            "ticket_id": ticket["id"],
            "title": ticket["title"],
            "category": ticket["category"],
            "description": ticket.get("description", ""),
            "resolution": ticket.get("resolution", "No resolution recorded"),
            "relevance_score": score
        })
    
    result = {
        "status": "success",
        "similar_tickets": similar_tickets,
        "total_found": len(similar_tickets)
    }
    
    if similar_tickets:
        result["message"] = f"Found {len(similar_tickets)} similar resolved ticket(s) that may help"
        # Record in state
        ticket_ids = [t["ticket_id"] for t in similar_tickets]
        record_similar_tickets(tool_context, ticket_ids)
    else:
        result["message"] = "No similar resolved tickets found. This may be a new issue type."
    
    print(f"--- Tool: Found {len(similar_tickets)} similar tickets ---")
    return result


def get_ticket_status(ticket_id: str, tool_context: ToolContext) -> Dict:
    """
    Gets the current status of a support ticket.
    
    Args:
        ticket_id: The ticket ID to look up (e.g., "TICKET-789")
        tool_context: ToolContext for session state access
    
    Returns:
        dict: Contains:
            - status: 'success' or 'error'
            - ticket: Ticket details if found
    """
    print(f"--- Tool: get_ticket_status called for: {ticket_id} ---")
    
    if ticket_id in TICKET_DATABASE:
        ticket = TICKET_DATABASE[ticket_id]
        result = {
            "status": "success",
            "ticket": {
                "id": ticket["id"],
                "title": ticket["title"],
                "status": ticket["status"],
                "priority": ticket["priority"],
                "assigned_team": ticket["assigned_team"],
                "created_at": ticket["created_at"]
            }
        }
        
        if ticket["status"] == "resolved":
            result["ticket"]["resolved_at"] = ticket.get("resolved_at")
            result["ticket"]["resolution"] = ticket.get("resolution")
        
        print(f"--- Tool: Ticket {ticket_id} status: {ticket['status']} ---")
    else:
        result = {
            "status": "error",
            "error_message": f"Ticket '{ticket_id}' not found"
        }
        print(f"--- Tool: Ticket {ticket_id} not found ---")
    
    return result
