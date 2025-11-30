from google.adk.agents.callback_context import CallbackContext
from google.genai.types import Content
from google.adk.agents.invocation_context import InvocationContext


def suppress_output_callback(callback_context: CallbackContext) -> Content:
    """Suppresses the output of the agent by returning an empty Content object."""
    return Content()

    # checking that the customer profile is loaded as state.
def before_agent(callback_context: InvocationContext):
    # In a production agent, this is set as part of the
    # session creation for the agent. 
    if "customer_profile" not in callback_context.state:
        callback_context.state["customer_profile"] = Customer.get_customer(
            "123"
        ).to_json()

    # logger.info(callback_context.state["customer_profile"])