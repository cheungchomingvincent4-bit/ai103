# Lab 01 · Prepare for an AI development project (no-portal version)
*AI-103 · Lesson 1 · about 45 minutes · adapted from Microsoft Learn `mslearn-ai-studio` exercise 01 for our classroom*
In this lab you work the way developers do: from the command line, in Python and in VS Code. You'll sign in to Azure, look at our class's Microsoft Foundry resource, call the **gpt-5.2** model from a Python script, and chat with it in VS Code.
> **Why no portal?** Microsoft Foundry also has websites (the Foundry portal and the Azure portal). They ask every user to set up the Microsoft Authenticator app, so in class we use the command line and VS Code instead. They reach the same resource and the same models. Your teacher's videos show the portal if you want to explore it at home.
## Before you start
> **Copy every command from this sheet** rather than typing it or copying it from the slides. A dash typed by hand or pasted through a chat app can turn into a look-alike character that `az` doesn't accept.
You need:
- **Your card:** your username (for example `qes7@unastudy.onmicrosoft.com`), your first password, and your project name (for example `qes7`).
- **On your PC:** Visual Studio Code, Python **3.13** (not 3.14), Git and the Azure CLI. Check them with `code --version`, `python --version`, `git --version` and `az version`.
### Missing Git or the Azure CLI?
If asked for an administrator password, put your hand up.
| | Windows (VS Code terminal) | macOS (Terminal) |
|---|---|---|
| **Git** | `winget install --id Git.Git -e --source winget` | `xcode-select --install`, then choose **Install** |
| **Azure CLI** | `winget install --exact --id Microsoft.AzureCLI` | `brew update && brew install azure-cli` (needs Homebrew) |
On Windows, close VS Code completely and open it again after installing, then check again with `git --version` and `az version` (2.80 or later).
Already done for you, so **don't** do them: creating a project, deploying a model, and cleaning up. Your project is ready, and the models are shared by the whole class.
## 1. Sign in with the Azure CLI
1. Open **Visual Studio Code**, then open a terminal: **Terminal → New Terminal**.
1. Sign in:
    ```
    az login --tenant unastudy.onmicrosoft.com
    ```
    A browser window opens. Sign in with your **qes username** and password. If another account is already shown, choose **Use another account**. If you're asked to choose a new password, do it and remember it.
    > **Important:** if a page asks you to set up **Microsoft Authenticator**, close it and put your hand up.
1. Back in the terminal, if you're asked to choose a subscription, press **Enter** to accept **Una External Azure CSP Subscription**.
1. Check that you're signed in as yourself:
    ```
    az account show --query "{user:user.name, subscription:name}" -o table
    ```
    You should see your qes username.
## 2. Explore the Foundry resource
These commands only **read** information. Creating or deleting things needs permissions you don't have, and you don't need them.
1. Look at our class's Foundry resource:
    ```
    az cognitiveservices account show -g QES-AI103 -n qes-ai103 --query "{name:name, kind:kind, region:location, endpoint:properties.endpoint}" -o table
    ```
    `AIServices` is the kind of Azure resource that a Foundry resource is. Note its region and its endpoint.
1. List the models deployed on the resource:
    ```
    az cognitiveservices account deployment list -g QES-AI103 -n qes-ai103 --query "[].{deployment:name, model:properties.model.name, version:properties.model.version, sku:sku.name, capacity:sku.capacity}" -o table
    ```
    Answer these questions:
    - How many model deployments are there?
    - What deployment type (`sku`) do they use?
    - What is the capacity of **gpt-5.2**? It's measured in thousands of tokens per minute.
1. List the projects on the resource:
    ```
    az cognitiveservices account project list -g QES-AI103 -n qes-ai103 --query "[].name" -o tsv
    ```
    Find your own project. You'll see your classmates' projects too: work only in yours.
## 3. Chat with gpt-5.2 from Python
1. In the terminal, make a folder for this lab and move into it:
    ```
    mkdir lab01
    cd lab01
    ```
1. Create a Python virtual environment and turn it on.
    **Windows (PowerShell):**
    ```
    py -3.13 -m venv .venv
    .venv\Scripts\Activate.ps1
    ```
    > If PowerShell says running scripts is disabled, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and try again. It only affects this terminal window.
    **macOS:**
    ```
    python3.13 -m venv .venv
    source .venv/bin/activate
    ```
    Your prompt should now start with `(.venv)`.
1. Install the OpenAI SDK and the Azure Identity library:
    ```
    pip install openai azure-identity
    ```
1. In VS Code, open the **lab01** folder (**File → Open Folder**), create a file named **hello_foundry.py**, and add this code:
    ```python
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
    ```
1. Save the file and run it:
    ```
    python hello_foundry.py
    ```
    After a few seconds, the model's answer appears.
    | If you see | What to do |
    |---|---|
    | `DefaultAzureCredential failed` | Run `az login --tenant unastudy.onmicrosoft.com` again |
    | `PermissionDenied` or `401` | Wait a few minutes and try again; if it persists, tell your teacher |
    | `429` or `Too Many Requests` | The whole class is sharing the model: wait a few seconds and run it again |
    | `DeploymentNotFound` | Check the spelling of `model_deployment` |
1. Compare the endpoint in your script with the resource endpoint from part 2. They're different doors into the same resource. Your card also lists a **project endpoint**, which we'll use for agents.
## 4. Chat with the model in VS Code
1. In VS Code, open **Extensions** and install **Foundry Toolkit for VS Code**.
1. Open the **Foundry Toolkit** pane on the left. Expand **Microsoft Foundry Resources**, sign in with your **qes account**, and set your project (**qes-ai103 → qesNN**) as the default project.
1. Expand your project, then **Models**, and select **gpt-5.2** to see its deployment details.
1. In **Developer Tools**, expand **Build** and select **Model playground**. Choose **gpt-5.2**, then paste the same instructions and question you used in Python.
> If signing in from VS Code opens a page asking for Microsoft Authenticator, skip this part and tell your teacher. Your Python script already does the same thing.
## Finished early?
1. **Model face-off:** change `model_deployment` to `"gpt-5-mini"` and run the script again. Time each model with `Measure-Command { python hello_foundry.py }` (Windows) or `time python hello_foundry.py` (macOS). Which is faster? Which answer is better?
1. **Change the persona:** rewrite the `instructions` so the model answers in Traditional Chinese, in under 80 words.
1. **Count the tokens:** add `print(response.usage)` at the end. How many input and output tokens did your question use? Remember that gpt-5.2's capacity is shared by the whole class.
## Before you leave
There's nothing to delete. On a shared school PC, sign out of Azure:
```
az logout
```
Also sign out of your account in VS Code (the **Accounts** icon, bottom left).