from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Classroom settings: the Azure OpenAI endpoint is on your card
azure_openai_endpoint = "https://qes-ai103.openai.azure.com/openai/v1/"
model_deployment = "gpt-5.2"

# Sign in with your az login session: no key needed
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://ai.azure.com/.default"
)
client = OpenAI(base_url=azure_openai_endpoint, api_key=token_provider)

# Send instructions and a question to the model using the Responses API
response = client.responses.create(
    model=model_deployment,
    instructions="You are an AI assistant that can provide information and advice about AI software development.",
    input="Describe three key considerations for working with Large Language Models for AI application development.",
)
print(response.output_text)