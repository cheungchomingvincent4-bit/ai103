from openai import OpenAI
from azure.identity import get_bearer_token_provider, DefaultAzureCredential

azure_openai_endpoint = "https://qes-ai103.openai.azure.com/openai/v1/"
token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default")
client = OpenAI(base_url=azure_openai_endpoint, api_key=token_provider, max_retries=5)

while 1:
    prompt = input(">>> ")
    stream = client.responses.create(
        model="gpt-6-luna",
        instructions="you are a penguin",
        input=prompt,
        stream=True
    )
    print()

    for chunk in stream:
        if chunk.type == "response.output_text.delta":
            print(chunk.delta, end="")
    print("\n")