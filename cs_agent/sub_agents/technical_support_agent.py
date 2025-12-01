"""
Specialist Agent - Technical Expert with Parallel Information Gathering

Uses ParallelAgent pattern to simultaneously:
- Search internet for solutions  
- Search knowledge base for solutions  
- Find similar resolved tickets

Then synthesizes all results into a comprehensive diagnosis.

This agent is responsible for investigating technical issues.
It can use Google search, knowledge base, and similar tickets to find solutions.
It can also escalate to human support if needed.
"""

from google.adk.agents import Agent, LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools import google_search
from .escalation_agent import escalation_agent
from ..tools.kb_tools import search_knowledge_base
from ..tools.solutions import generate_solution_steps

from ..agent_utils import suppress_output_callback
from ..tools.ticket_system import search_similar_tickets

google_search_agent = LlmAgent(
    name="google_search_agent",
    model="gemini-2.5-flash-lite",
    description="Checks similar issues in Google.",
    instruction="""You are Google search agent. Your ONLY job is to check similar issues on the internet.

TASK:
1. Analyze the issue description from the conversation
2. Use 'google_search' with relevant search terms
3. Extract key information from top 5 found articles

OUTPUT FORMAT:
Summarize your findings in this format:
- Articles Found: [number]
- Most Relevant Article: [title and ID]
- Key Solution Steps: [brief summary of solution if found]
- Relevance: [high/medium/low]

Be concise. Just report facts, no solutions yet.""",
    tools=[google_search],
    output_key="google_search_result",
    after_agent_callback=suppress_output_callback,
)


kb_search_agent = Agent(
    name="kb_search_agent",
    model="gemini-2.5-flash-lite",
    description="Searches knowledge base for relevant articles and documentation.",
    instruction="""You are the Knowledge Base Searcher. Your ONLY job is to find relevant documentation.

TASK:
1. Analyze the issue description from the conversation
2. Use 'search_knowledge_base' with relevant search terms
3. Extract key information from found articles

OUTPUT FORMAT:
Summarize your findings in this format:
- Articles Found: [number]
- Most Relevant Article: [title and ID]
- Key Solution Steps: [brief summary of solution if found]
- Relevance: [high/medium/low]

Be concise. Just report what you found, no diagnosis yet.""",
    tools=[search_knowledge_base],
    output_key="kb_search_result",
    after_agent_callback=suppress_output_callback,
)


ticket_search_agent = LlmAgent(
    name="ticket_search_agent",
    model="gemini-2.5-flash-lite",
    description="Searches for similar previously resolved support tickets.",
    instruction="""
        You are the Ticket History Searcher. Your ONLY job is to find similar past issues.

        TASK:
        1. Analyze the current issue description
        2. Use 'search_similar_tickets' to find resolved tickets with similar problems
        3. Extract resolution information from matches

        OUTPUT FORMAT:
        Summarize your findings in this format:
        - Similar Tickets Found: [number]
        - Best Match: [ticket ID and brief description]
        - Resolution Used: [what fixed the issue in past tickets]
        - Confidence: [high/medium/low based on similarity]

        Be concise. Just report historical matches, no new solutions yet.
    """,
    tools=[search_similar_tickets],
    output_key="similar_tickets_result",
    after_agent_callback=suppress_output_callback,
)


parallel_info_gathering = ParallelAgent(
    name="parallel_info_gathering",
    description="Gathers information from multiple sources in parallel: google search, knowledge base, and ticket history.",
    sub_agents=[google_search_agent, kb_search_agent, ticket_search_agent]
)


    diagnosis_synthesizer = LlmAgent(
    name="diagnosis_synthesizer",
    model="gemini-2.5-flash-lite",
    description="Synthesizes information from parallel searches into a comprehensive diagnosis.",
    instruction="""
        You are the Diagnosis Synthesizer. Combine all gathered information into a solution.

        INPUT (from parallel agents via session state):
        - Information from Google search: {google_search_result}
        - Knowledge Base: {kb_search_result}
        - Similar Tickets: {similar_tickets_result}

        YOUR TASK:
        1. Analyze all three information sources
        2. Identify the most likely cause of the issue
        3. Generate a step-by-step solution using 'generate_solution_steps' if you identified an error type

        OUTPUT FORMAT:
        Provide a comprehensive response to the user:

        **Diagnosis:**
        [Explain what you found and the likely cause]

        **Solution:**
        [Step-by-step instructions to fix the issue]

        **If this doesn't work:**
        [Alternative approaches or escalation recommendation]

        GUIDELINES:
        - If KB has a direct solution, reference the article
        - If similar ticket was resolved, reference that ticket ID
        - Be empathetic and clear in your explanation
        - If no clear solution, recommend escalation to human support
        - If the user wants to escalate, pass execution to 'escalation_agent'.
    """,
    tools=[generate_solution_steps],
    output_key="diagnosis_result"
)


technical_support_agent = SequentialAgent(
    name="specialist_agent",
    description="Technical specialist that handles complex issues. Uses parallel information "
                "gathering for faster diagnosis, then synthesizes findings into solutions. "
                "Escalates to human support when automated solutions fail.",
    sub_agents=[parallel_info_gathering, diagnosis_synthesizer]
)