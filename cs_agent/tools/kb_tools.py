"""
Knowledge Base Tools

Provides access to support documentation, FAQs, and help articles.
Uses mock data for MVP - can be replaced with real KB integration.

Uses ToolContext to:
- Record KB searches in session state
- Track which articles have been shown
"""

from typing import Dict
from google.adk.tools.tool_context import ToolContext


# Mock knowledge base data
KNOWLEDGE_BASE = {
    "articles": [
        {
            "id": "KB001",
            "title": "How to Reset Your Password",
            "category": "password_reset",
            "content": """To reset your password:
1. Go to the login page and click 'Forgot Password'
2. Enter your email address
3. Check your inbox for a reset link (check spam folder too)
4. Click the link and create a new password
5. Password must be at least 8 characters with one number and one special character

If you don't receive the email within 5 minutes, contact support.""",
            "keywords": ["password", "reset", "forgot", "login", "access"]
        },
        {
            "id": "KB002", 
            "title": "Webhook Configuration Guide",
            "category": "integration",
            "content": """Setting up webhooks:
1. Navigate to Settings > Integrations > Webhooks
2. Click 'Add Webhook Endpoint'
3. Enter your endpoint URL (must be HTTPS)
4. Select the events you want to receive
5. Copy the webhook secret for signature verification

Common issues:
- Signature mismatch: Regenerate your webhook secret and update your code
- Events not received: Check your endpoint returns 200 OK within 30 seconds
- SSL errors: Ensure your certificate is valid and not self-signed""",
            "keywords": ["webhook", "integration", "api", "events", "endpoint", "signature"]
        },
        {
            "id": "KB003",
            "title": "API Authentication Guide", 
            "category": "integration",
            "content": """API Authentication:
1. Generate an API key from Settings > API Keys
2. Include the key in the Authorization header: 'Bearer YOUR_API_KEY'
3. API keys are environment-specific (test/production)

Rate limits:
- Standard plan: 100 requests/minute
- Pro plan: 1000 requests/minute
- Enterprise: Custom limits

If you receive 401 errors, verify your API key is correct and active.""",
            "keywords": ["api", "authentication", "auth", "key", "401", "bearer", "token"]
        },
        {
            "id": "KB004",
            "title": "Billing and Subscription FAQ",
            "category": "billing",
            "content": """Billing Information:
- Invoices are generated on the 1st of each month
- Payment methods: Credit card, ACH, Wire transfer (Enterprise only)
- Upgrade/downgrade takes effect immediately, prorated billing applies

Common questions:
- View invoices: Settings > Billing > Invoice History
- Update payment method: Settings > Billing > Payment Methods
- Cancel subscription: Settings > Billing > Manage Plan > Cancel""",
            "keywords": ["billing", "invoice", "payment", "subscription", "cancel", "upgrade"]
        },
        {
            "id": "KB005",
            "title": "Troubleshooting 500 Errors",
            "category": "bug_report",
            "content": """If you're experiencing 500 Internal Server Errors:

1. Check our status page for ongoing incidents
2. Retry the request after a few seconds (may be temporary)
3. If persistent, note:
   - The exact endpoint being called
   - Request body/parameters
   - Time of occurrence
   - Any error message returned

Common causes:
- Large payload sizes (max 10MB)
- Invalid JSON format
- Missing required fields
- Rate limit exceeded (returns 429, not 500)

If the issue persists, contact support with the details above.""",
            "keywords": ["500", "error", "server", "bug", "crash", "internal"]
        }
    ]
}

# FAQ quick answers
FAQ_DATABASE = {
    "password reset": "You can reset your password at the login page by clicking 'Forgot Password' and following the email instructions.",
    "api rate limit": "Rate limits are: Standard (100/min), Pro (1000/min), Enterprise (custom). Check headers for X-RateLimit-Remaining.",
    "webhook timeout": "Webhooks timeout after 30 seconds. Ensure your endpoint responds with 200 OK quickly. Process heavy operations asynchronously.",
    "billing cycle": "Billing occurs on the 1st of each month. Changes are prorated.",
    "cancel subscription": "Go to Settings > Billing > Manage Plan > Cancel. You'll retain access until the end of your billing period.",
    "api key": "Generate API keys at Settings > API Keys. Keep them secure and never share in public repositories.",
    "supported browsers": "We support the latest versions of Chrome, Firefox, Safari, and Edge.",
    "data export": "Export your data from Settings > Account > Export Data. Processing may take up to 24 hours for large accounts."
}


def search_knowledge_base(query: str, tool_context: ToolContext, max_results: int = 3) -> Dict:
    """
    Searches the knowledge base for articles matching the query.
    Records the search in session state for tracking.
    
    Args:
        query: Search query string (e.g., "webhook signature error")
        tool_context: ToolContext for session state access
        max_results: Maximum number of articles to return (default 3)
    
    Returns:
        dict: Contains 'status', 'articles' list with matching articles,
              and 'total_found' count. Each article has id, title, category,
              and content fields.
    """
    print(f"--- Tool: search_knowledge_base called with query: '{query}' ---")
    
    # Record search in state
    from ..session.state_helpers import record_kb_search
    record_kb_search(tool_context, query)
    
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    scored_articles = []
    
    for article in KNOWLEDGE_BASE["articles"]:
        score = 0
        
        # Check title match
        if query_lower in article["title"].lower():
            score += 10
            
        # Check keyword matches
        for keyword in article["keywords"]:
            if keyword in query_lower or keyword in query_words:
                score += 5
                
        # Check content match
        if query_lower in article["content"].lower():
            score += 3
            
        # Check individual word matches
        for word in query_words:
            if len(word) > 3:  # Skip short words
                if word in article["content"].lower():
                    score += 1
                if word in article["title"].lower():
                    score += 2
        
        if score > 0:
            scored_articles.append((score, article))
    
    # Sort by score and take top results
    scored_articles.sort(key=lambda x: x[0], reverse=True)
    results = [
        {
            "id": article["id"],
            "title": article["title"],
            "category": article["category"],
            "content": article["content"],
            "relevance_score": score
        }
        for score, article in scored_articles[:max_results]
    ]
    
    print(f"--- Tool: Found {len(results)} relevant articles ---")
    
    return {
        "status": "success",
        "articles": results,
        "total_found": len(results)
    }


def get_faq_answer(question: str, tool_context: ToolContext) -> Dict:
    """
    Gets a quick answer from the FAQ database for common questions.
    
    Args:
        question: The question to look up (e.g., "how to reset password")
        tool_context: ToolContext for session state access
    
    Returns:
        dict: Contains 'status' and either 'answer' if found or 
              'message' if no FAQ match exists.
    """
    print(f"--- Tool: get_faq_answer called with question: '{question}' ---")
    
    question_lower = question.lower()
    
    # Direct match
    for topic, answer in FAQ_DATABASE.items():
        if topic in question_lower:
            print(f"--- Tool: Found FAQ match for topic: '{topic}' ---")
            return {
                "status": "found",
                "topic": topic,
                "answer": answer
            }
    
    # Fuzzy match - check if multiple words match
    question_words = set(question_lower.split())
    best_match = None
    best_score = 0
    
    for topic, answer in FAQ_DATABASE.items():
        topic_words = set(topic.split())
        overlap = len(question_words.intersection(topic_words))
        if overlap > best_score:
            best_score = overlap
            best_match = (topic, answer)
    
    if best_match and best_score >= 1:
        print(f"--- Tool: Found fuzzy FAQ match for topic: '{best_match[0]}' ---")
        return {
            "status": "found",
            "topic": best_match[0],
            "answer": best_match[1]
        }
    
    print("--- Tool: No FAQ match found ---")
    return {
        "status": "not_found",
        "message": "No FAQ entry found for this question. Try searching the knowledge base for more detailed articles."
    }
