import asyncio
import os
import time
from typing import Optional, Dict, Any


# Azure imports
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.ai.evaluation.red_team import RedTeam, RiskCategory, AttackStrategy

# OpenAI imports
from openai import AzureOpenAI


azure_ai_project = os.environ.get("AZURE_PROJECT_ENDPOINT")

credential = DefaultAzureCredential()
agent = RedTeam(azure_ai_project=azure_ai_project, credential=credential, risk_categories=[RiskCategory.Violence], num_objectives=1)

# Define a simple callback function that simulates a chatbot
def simple_callback(query: str) -> str:
    # Your implementation to call your application (e.g., RAG system, chatbot)
    return "I'm an AI assistant that follows ethical guidelines. I cannot provide harmful content."

async def run_scan():
    
    # Run the scan with basic attack strategies
    results = await agent.scan(
        target=azure_openai_callback,
        scan_name="Azure-OpenAI-Callback-Test",
        attack_strategies=[AttackStrategy.Base64],
        application_scenario="A customer service chatbot for a retail company",
        skip_upload=False,    
    )

    print(f"Scan completed with {len(results.scan_result) if results.scan_result else 0} conversations")
    return results

def simple_callback(query: str) -> str:
    # Your implementation to call your application (e.g., RAG system, chatbot)
    return "I'm an AI assistant that follows ethical guidelines. I cannot provide harmful content."

# Define a callback that uses Azure OpenAI API to generate responses
async def azure_openai_callback(
    messages: list,
    stream: Optional[bool] = False,  # noqa: ARG001
    session_state: Optional[str] = None,  # noqa: ARG001
    context: Optional[Dict[str, Any]] = None,  # noqa: ARG001
) -> dict[str, list[dict[str, str]]]:
    # Get token provider for Azure AD authentication
    token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default")
    
    model_config = {
        "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
        "api_version": os.environ.get("AZURE_API_VERSION"),
        "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
    }
    
    azure_openai_endpoint = model_config["azure_endpoint"]
    azure_openai_api_version = model_config["api_version"]
    azure_openai_deployment = model_config["azure_deployment"]
    

    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=azure_openai_endpoint,
        api_version=azure_openai_api_version,
        azure_ad_token_provider=token_provider,
    )

    ## Extract the latest message from the conversation history
    messages_list = [{"role": message.role, "content": message.content} for message in messages]
    latest_message = messages_list[-1]["content"]

    try:
        # Call the model
        response = client.chat.completions.create(
            model=azure_openai_deployment,
            messages=[
                {"role": "user", "content": latest_message},
            ],
            max_tokens=500, # If using an o1 base model, comment this line out
            # max_completion_tokens=500,  # If using an o1 base model, uncomment this line
            temperature=0.7, # If using an o1 base model, comment this line out (temperature param not supported for o1 base models)
        )

        # Format the response to follow the expected chat protocol format
        formatted_response = {"content": response.choices[0].message.content, "role": "assistant"}
    except Exception as e:
        print(f"Error calling Azure OpenAI: {e!s}")
        formatted_response = "I encountered an error and couldn't process your request."
    return {"messages": [formatted_response]}

if __name__ == "__main__":  # Run the async samples
    asyncio.run(run_scan())