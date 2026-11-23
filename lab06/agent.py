import os
from dotenv import load_dotenv

# Add references
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool
from openai.types.responses.response_input_param import McpApprovalResponse, ResponseInputParam

# Load environment variables from .env file
load_dotenv()
project_endpoint = os.getenv("PROJECT_ENDPOINT")
model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")

# Connect to the agents client
with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    # Initialize agent MCP tool
    mcp_tool = MCPTool(
        server_label="api-specs",
        server_url="https://learn.microsoft.com/api/mcp",
        require_approval="never",
    )

    # Create a new agent with the MCP tool
    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=PromptAgentDefinition(
            model=model_deployment,
            instructions="You are a helpful agent that can use MCP tools to assist users. Use the available MCP tools to answer questions. Answer in at most 5 short bullet points, then list the links to the pages you used.",
            tools=[mcp_tool],
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    # Create conversation thread
    conversation = openai_client.conversations.create()
    print(f"Created conversation (id: {conversation.id})")

    while 1:

        # Send initial request that will trigger the MCP tool
        question = input("Question:  ")
        response = openai_client.responses.create(
            conversation=conversation.id,
            input=question,
            extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        )

        # Show the tools that Foundry found on the MCP server
        for item in response.output:
            if item.type == "mcp_list_tools":
                tool_names = ", ".join(tool.name for tool in item.tools)
                print(f"[Foundry] Connected to the '{item.server_label}' MCP server. Its tools: {tool_names}")

        # Process any MCP approval requests that were generated
        # The agent may make several tool calls, each needing its own approval, so loop until none are left
        while True:
            input_list: ResponseInputParam = []
            for item in response.output:
                # Show each tool call that Foundry has made for us
                if item.type == "mcp_call":
                    print(f"[Foundry] Called {item.name} and got {len(item.output or '')} characters of documentation")
                # Ask the user before each new tool call
                if item.type == "mcp_approval_request" and item.server_label == "api-specs" and item.id:
                    print(f"\n[Foundry] The agent wants to call {item.name} with: {item.arguments}")
                    answer = input("[Your app] Allow this call? (y/n): ")
                    input_list.append(
                        McpApprovalResponse(
                            type="mcp_approval_response",
                            approve=answer.strip().lower() == "y",
                            approval_request_id=item.id,
                        )
                    )

            # No more approvals needed: the agent has produced its final response
            if not input_list:
                break

            # Send the answers back: Foundry runs the approved calls and the agent carries on
            response = openai_client.responses.create(
                input=input_list,
                previous_response_id=response.id,
                extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
            )

        print(f"\n[Agent] {response.output_text}")
    # Clean up resources by deleting the agent version
    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")
