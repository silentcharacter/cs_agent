from google.adk.agents import LlmAgent
from .escalation_agent import escalation_agent
from ..tools.order_tools import get_order_status

order_agent = LlmAgent(
    name="Order", 
    model="gemini-2.5-flash-lite",
    description="Handles order inquiries.",
    instruction="""
        You are a helpful assistant that handles order related inquiries (status, shipping, refunds, etc.).
        If asked about a specific order, use the get_order_status tool to get the order status.
        If you are not able to answer the question, recommend escalation to human support
        If the user wants to escalate, pass execution to 'escalation_agent'.
    """,
    tools=[get_order_status]
)

