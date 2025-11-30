from typing import List, Dict, Optional
from google.adk.tools.tool_context import ToolContext


# Mock Database
orders_db = {
    "101": {"status": "Delivered", "item": "Smart Speaker"},
    "102": {"status": "In Transit", "item": "Pixel Buds Pro"},
    "103": {"status": "Processing", "item": "Phone Case"}
}

def get_order_status(order_id: str):
    """
    Retrieves the status of an order given its ID.
    Args:
        order_id: The order number (e.g., '101').
    """
    order = orders_db.get(order_id)
    if order:
        return f"Order {order_id} ({order['item']}): Status - {order['status']}."
    else:
        return f"Order ID {order_id} not found."
