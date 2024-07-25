# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: completions_aoai_quickstart.py

DESCRIPTION:
    This sample demonstrates how to get started with Completions using the Azure OpenAI SDK for Python.

USAGE:
    python completions_aoai_quickstart.py

    Before running the sample:

    pip install openai

    Set the environment variables with your own values:
    1) AZURE_OPENAI_KEY - your Azure OpenAI API key.
    2) AZURE_OPENAI_ENDPOINT - the endpoint to your Azure OpenAI resource.
"""

# These lines are intentionally excluded from the sample code, we use them to configure any vars
# or to tweak usage in ways that keep samples looking consistent when rendered in docs and tools
import os
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZ_OPENAI_ENDPOINT")

def completions_aoai_quickstart() -> None:
    import os
    from openai import AzureOpenAI

    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("API_VERSION_GA"),
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        )

    #This will correspond to the custom name you chose for your deployment when you deployed a model.
    # Use a gpt-35-turbo-instruct deployment.
    deployment_name=os.environ["AZURE_OPENAI_COMPLETIONS_DEPLOYMENT"]

    # Send a completion call to generate an answer
    prompt = 'Write a tagline for an ice cream shop.'
    response = client.completions.create(model=deployment_name, prompt=prompt, max_tokens=10)
    print(prompt + response.choices[0].text)

if __name__ == '__main__':
    completions_aoai_quickstart()