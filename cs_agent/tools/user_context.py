"""
User Context Tool

Retrieves information about the user's account and history.
Uses mock data for MVP - can be replaced with real user database.

Uses ToolContext to:
- Store user information in session state
- Track that user context has been loaded
"""

from typing import Dict, Optional
from google.adk.tools.tool_context import ToolContext
from ..session.state_helpers import set_user_info

# Mock user database
MOCK_USERS = {
    "user_123": {
        "name": "John Smith",
        "email": "john.smith@example.com",
        "plan": "Pro",
        "account_status": "active",
        "created_at": "2024-01-15",
        "recent_tickets": ["TICKET-456", "TICKET-234"],
        "api_key_count": 2,
        "webhook_count": 3,
        "last_login": "2025-01-10"
    },
    "user_456": {
        "name": "Jane Doe",
        "email": "jane.doe@company.com",
        "plan": "Enterprise",
        "account_status": "active",
        "created_at": "2023-06-20",
        "recent_tickets": [],
        "api_key_count": 5,
        "webhook_count": 10,
        "last_login": "2025-01-12"
    },
    "demo_user": {
        "name": "Jack Sparrow",
        "email": "demo@example.com",
        "plan": "Standard",
        "account_status": "active",
        "created_at": "2024-11-01",
        "recent_tickets": ["TICKET-789"],
        "api_key_count": 1,
        "webhook_count": 1,
        "last_login": "2025-01-12"
    }
}

# Default user for when ID is not provided
DEFAULT_USER_ID = "demo_user"


def get_user_context(tool_context: ToolContext, user_id: Optional[str] = None) -> Dict:
    """
    Retrieves context information about the user including their account details,
    plan type, and recent support history. Stores the info in session state.
    
    Args:
        tool_context: ToolContext for session state access
        user_id: Optional user identifier. If not provided, uses the current
                session user or default demo user.
    
    Returns:
        dict: Contains:
            - status: 'success' or 'error'
            - user: Dict with user details (name, email, plan, etc.)
            - support_context: Recent tickets and account age
    """
    print(f"--- Tool: get_user_context called for user_id: {user_id or 'default'} ---")
    
    # Use default if no ID provided
    lookup_id = user_id or DEFAULT_USER_ID
    
    if lookup_id in MOCK_USERS:
        user = MOCK_USERS[lookup_id]

        # Store user info in session state
        set_user_info(
            tool_context=tool_context,
            user_name=user["name"],
            user_plan=user["plan"],
            user_id=lookup_id,
            recent_tickets=user["recent_tickets"],
        )
        
        result = {
            "status": "success",
            "user": {
                "name": user["name"],
                "email": user["email"],
                "plan": user["plan"],
                "account_status": user["account_status"]
            },
            "support_context": {
                "recent_tickets": user["recent_tickets"],
                "ticket_count": len(user["recent_tickets"])
            }
        }
        
        print(f"--- Tool: Found user {user['name']} on {user['plan']} plan ---")
        return result
    
    else:
        print(f"--- Tool: User {lookup_id} not found ---")
        return {
            "status": "error",
            "error_message": f"User '{lookup_id}' not found in the system",
            "suggestion": "Please verify the user ID or proceed without user context"
        }
