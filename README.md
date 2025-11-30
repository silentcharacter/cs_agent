# Customer Support Agent

This project implements an AI-powered customer service agent for E-Commerce Company. 
The agent is designed to provide excellent customer service, assist customers with orders and billings issues, troubleshoot technical problems, create support tickets and check their status.

## Overview


## Agent Details


### Agent Architecture

![Customer Service Agent Workflow](architecture_diagram.png)


The agent is built using a multi-modal architecture, combining text and video inputs to provide a rich and interactive experience. It mocks interactions with various tools and services, including a product catalog, inventory management, order processing, and appointment scheduling systems. The agent also utilizes a session management system to maintain context across interactions and personalize the customer experience.

It is important to notice that this agent is not integrated to an actual backend and the behaviour is based on mocked tools. 


### Key Features

- **Personalized Customer Assistance:**
  - Greets returning customers by name and acknowledges their purchase history.
  - Maintains a friendly, empathetic, and helpful tone.
- **Order Tracking:**
- **Evaluation:**
  - The agent can be evaluated using a set of test cases.
  - The evaluation is based on the agent's ability to use the tools and to respond to the user's requests.

#### Agent State - Default customer information

The agent's session state is preloaded with sample customer data, simulating a real conversation. Ideally, this state should be loaded from a CRM system at the start of the conversation, using the user's information. This assumes that either the agent authenticates the user or the user is already logged in. 

#### Tools

The agent has access to the following tools:

- `send_call_companion_link(phone_number: str) -> str`: Sends a link for video connection.


## Setup and Installations

### Prerequisites

- Python 3.10+
- uv (for dependency management)
- Google ADK SDK (installed via uv)
- Google Cloud Project (for Vertex AI Gemini integration)

### Installation
1.  **Prerequisites:**

    For the Agent Engine deployment steps, you will need
    a Google Cloud Project. Once you have created your project,
    [install the Google Cloud SDK](https://cloud.google.com/sdk/docs/install).
    Then run the following command to authenticate with your project:
    ```bash
    gcloud auth login
    ```
    You also need to enable certain APIs. Run the following command to enable
    the required APIs:
    ```bash
    gcloud services enable aiplatform.googleapis.com
    ```

    Install uv for dependency management:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

1.  Clone the repository:

    ```bash
    git clone https://github.com/...
    cd ...
    ```


2.  Install dependencies:

    ```bash
    uv sync
    ```

3.  Set up Google Cloud credentials:

    - Ensure you have a Google Cloud project.
    - Make sure you have the Vertex AI API enabled in your project.
    - Set the `GOOGLE_GENAI_USE_VERTEXAI`, `GOOGLE_CLOUD_PROJECT`, and `GOOGLE_CLOUD_LOCATION` environment variables. You can set them in your `.env` file (modify and rename .env_sample file to .env) or directly in your shell. Alternatively you can edit [customer_service/config.py](./customer_service/config.py)

    ```bash
    export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_NAME_HERE
    export GOOGLE_GENAI_USE_VERTEXAI=1
    export GOOGLE_CLOUD_LOCATION=us-central1
    ```
 
 Enable Google Cloud APIs¶
For this tutorial, you'll need to enable the following APIs in the Google Cloud Console.

Vertex AI API
Cloud Storage API
Cloud Logging API
Cloud Monitoring API
Cloud Trace API
Telemetry API
You can use this link to open the Google Cloud Console and follow the steps there to enable these APIs: https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com,storage.googleapis.com,logging.googleapis.com,monitoring.googleapis.com,cloudtrace.googleapis.com,telemetry.googleapis.com 


## Running the Agent

You can run the agent using the ADK commant in your terminal.
from the root project directory:

1.  Run agent in CLI:

    ```bash
    adk run customer_service
    ```

2.  Run agent with ADK Web UI:
    ```bash
    adk web
    ```
    Select the customer_service from the dropdown



## Evaluating the Agent

Evaluation tests assess the overall performance and capabilities of the agent in a holistic manner.

**Steps:**

1.  **Run Evaluation Tests:**

    ```bash
    uv sync --dev
    uv run pytest eval
    ```

    - This command executes all test files within the `eval` directory.

## Unit Tests

Unit tests focus on testing individual units or components of the code in isolation.

**Steps:**

1.  **Run Unit Tests:**

    ```bash
    uv run pytest tests/unit
    ```

    - This command executes all test files within the `tests/unit` directory.



## Deployment on Google Agent Engine

In order to inherit all dependencies of your agent you can build the wheel file of the agent and run the deployment.

1.  **Build Customer Service Agent WHL file**

    ```bash
    uv build --wheel --out-dir deployment
    ```

1.  **Deploy the agent to agents engine**
    It is important to run deploy.py from within deployment folder so paths are correct

    ```bash
    cd deployment
    uv run python deploy.py
    ```

### Testing deployment

This code snippet is an example of how to test the deployed agent.

```python
import vertexai
from customer_service.config import Config
from vertexai.preview.reasoning_engines import AdkApp


configs = Config()

vertexai.init(
    project="<GOOGLE_CLOUD_LOCATION_PROJECT_ID>",
    location="<GOOGLE_CLOUD_LOCATION>"
)

# get the agent based on resource id
agent_engine = vertexai.agent_engines.get('DEPLOYMENT_RESOURCE_NAME') # looks like this projects/PROJECT_ID/locations/LOCATION/reasoningEngines/REASONING_ENGINE_ID

for event in remote_agent.stream_query(
    user_id=USER_ID,
    session_id=session["id"],
    message="Hello!",
):
    print(event)

```

### Alternative: Using Agent Starter Pack

You can also use the [Agent Starter Pack](https://goo.gle/agent-starter-pack) to create a production-ready version of this agent with additional deployment options:

```bash
# Create and activate a virtual environment
python -m venv .venv && source .venv/bin/activate # On Windows: .venv\Scripts\activate

# Install the starter pack and create your project
pip install --upgrade agent-starter-pack
agent-starter-pack create my-customer-service -a adk@customer-service
```

<details>
<summary>⚡️ Alternative: Using uv</summary>

If you have [`uv`](https://github.com/astral-sh/uv) installed, you can create and set up your project with a single command:
```bash
uvx agent-starter-pack create my-customer-service -a adk@customer-service
```
This command handles creating the project without needing to pre-install the package into a virtual environment.

</details>

The starter pack will prompt you to select deployment options and provides additional production-ready features including automated CI/CD deployment scripts.



Cleanup

export GOOGLE_CLOUD_PROJECT = <>
export GOOGLE_CLOUD_LOCATION = <>
 uv run python deployment/cleanup.py