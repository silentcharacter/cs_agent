import vertexai
from vertexai import agent_engines
import os

PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
deployed_region = os.environ["GOOGLE_CLOUD_LOCATION"]

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=deployed_region)

# Get the most recently deployed agent
agents_list = list(agent_engines.list())
if agents_list:
    remote_agent = agents_list[0]  # Get the first (most recent) agent
    client = agent_engines
    print(f"✅ Connected to deployed agent: {remote_agent.resource_name}")

    agent_engines.delete(resource_name=remote_agent.resource_name, force=True)
    print("✅ Agent successfully deleted")
else:
    print("❌ No agents found. Please deploy first.")


