import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool

# Connect to your Foundry project
load_dotenv()
project_client = AIProjectClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential(),
)

# The Foundry IQ knowledge base, which the agent reaches through MCP
knowledge_tool = MCPTool(
    server_label="knowledge-base",
    server_url=os.getenv("KB_MCP_URL"),
    require_approval="always",
    allowed_tools=["knowledge_base_retrieve"],
    project_connection_id=os.getenv("KB_CONNECTION"),
)

# Create the agent
agent = project_client.agents.create_version(
    agent_name=os.getenv("AGENT_NAME"),
    definition=PromptAgentDefinition(
        model=os.getenv("MODEL_DEPLOYMENT_NAME"),
        instructions="""You are a helpful AI assistant for Contoso, specializing in outdoor camping and hiking products.
You must ALWAYS search the knowledge base to answer questions about our products or product catalog.
Provide detailed, accurate information and always cite your sources.
If you don't find relevant information in the knowledge base, say so clearly.""",
        tools=[knowledge_tool],
    ),
)
print(f"Created {agent.name}, version {agent.version}")
