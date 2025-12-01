from google.adk.agents import LlmAgent
from .escalation_agent import escalation_agent

"""
Billing Agent - Handles billing and payment inquiries

This agent is responsible for handling billing and payment inquiries.
It can answer questions about billing, payment, and subscription management.
It can also create support tickets for billing issues.
It can also escalate to human support if needed.
"""

billing_agent = LlmAgent(
    name="Billing", 
    model="gemini-2.5-flash-lite",
    description="Handles billing inquiries.",
    instruction="""
        You are a helpful assistant that handles billing inquiries. 
        If you are not able to answer the question, recommend escalation to human support.
        If the user wants to escalate, pass execution to 'escalation_agent'.
    """
)
