import os
import time
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    FileSearchTool,
    CodeInterpreterTool,
    AutoCodeInterpreterToolParam,
)

# Connect to your Foundry project
load_dotenv()
project_client = AIProjectClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential(),
)
openai_client = project_client.get_openai_client()

# Upload the IT policy and index it in a vector store, for file search
with open("IT_Policy.txt", "rb") as f:
    policy_file = openai_client.files.create(file=f, purpose="assistants")
vector_store = openai_client.vector_stores.create(
    name="it-policy",
    file_ids=[policy_file.id],
)
while vector_store.status == "in_progress":
    print("Indexing the policy...")
    time.sleep(2)
    vector_store = openai_client.vector_stores.retrieve(vector_store_id=vector_store.id)
print(f"Vector store {vector_store.id}: {vector_store.status}")

# Upload the performance data, for code interpreter
with open("system_performance.csv", "rb") as f:
    data_file = openai_client.files.create(file=f, purpose="assistants")
print(f"Uploaded {data_file.filename}") 

# Create the agent: a model, instructions and two built-in tools
agent = project_client.agents.create_version(
    agent_name=os.getenv("AGENT_NAME"),
    definition=PromptAgentDefinition(
        model=os.getenv("MODEL_DEPLOYMENT_NAME"),
        instructions="""You are an IT Support Agent for Contoso Corporation.
You help employees with technical issues and IT policy questions.

Guidelines:
- Always be professional and helpful
- Use the IT policy documentation to answer questions accurately
- If you don't know the answer, admit it and suggest contacting IT support directly
- When creating tickets, collect all necessary information before proceeding""",
        tools=[
            FileSearchTool(vector_store_ids=[vector_store.id]),
            CodeInterpreterTool(container=AutoCodeInterpreterToolParam(file_ids=[data_file.id])),
        ],
    ),
)
print(f"Created {agent.name}, version {agent.version}")
