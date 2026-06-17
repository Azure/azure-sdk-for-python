# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to upload a Python script that calls
    Foundry (with `DefaultAzureCredential`) and run it inside a Code
    Interpreter sandboxed container by:

    1. Minting an Entra access token locally (the sandbox can't acquire
       one on its own).
    2. Generating a tiny `runner.py` that stubs out `python-dotenv`,
       patches `azure.identity.DefaultAzureCredential` to return the
       locally-minted token for any requested scope, and then executes
       the uploaded target script.
    3. Uploading both files via `file_ids` on the Code Interpreter tool.
    4. Configuring `network_policy` so the container can reach PyPI and
       the Foundry endpoint.
    5. Prompting the agent to pip-install the required packages and exec
       the runner, then printing the captured stdout / stderr / traceback.

    Security note:
        The locally-minted token is uploaded to the Code Interpreter file
        store and appears in the response transcript. Entra access tokens
        are typically valid for about an hour. Use this pattern only for
        short-lived demos against non-production resources.

USAGE:
    python sample_agent_run_uploaded_script.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
import tempfile
from urllib.parse import urlparse

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    CodeInterpreterTool,
    AutoCodeInterpreterToolParam,
    ContainerNetworkPolicyAllowlistParam,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]

target_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "sample_agent_openapi.py"))
target_filename = os.path.basename(target_script_path)
runner_filename = "runner.py"

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    # Mint a short-lived token locally and bake it into the runner.
    token = credential.get_token("https://ai.azure.com/.default")

    runner_source = f"""\
import os
import sys
import types

os.environ["FOUNDRY_PROJECT_ENDPOINT"] = {endpoint!r}
os.environ["FOUNDRY_MODEL_NAME"] = {model_name!r}

# Stub python-dotenv so the target script's `from dotenv import load_dotenv` works.
_dotenv = types.ModuleType("dotenv")
_dotenv.load_dotenv = lambda *a, **kw: None
sys.modules["dotenv"] = _dotenv

# Patch DefaultAzureCredential to return the locally-minted token for any scope.
import azure.identity
from azure.core.credentials import AccessToken, AccessTokenInfo

_TOKEN = {token.token!r}
_EXPIRES_ON = {token.expires_on}

class _InjectedCredential:
    def __init__(self, *a, **kw): pass
    def get_token(self, *scopes, **kw): return AccessToken(_TOKEN, _EXPIRES_ON)
    def get_token_info(self, *scopes, **kw): return AccessTokenInfo(_TOKEN, _EXPIRES_ON)
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def close(self): pass

azure.identity.DefaultAzureCredential = _InjectedCredential

import glob, runpy
target = glob.glob("/mnt/data/*{target_filename}")[0]
runpy.run_path(target, run_name="__main__")
"""

    # Upload runner + target.
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp.write(runner_source)
        runner_local_path = tmp.name
    try:
        with open(runner_local_path, "rb") as f:
            uploaded_runner = openai_client.files.create(purpose="assistants", file=f)
        with open(target_script_path, "rb") as f:
            uploaded_target = openai_client.files.create(purpose="assistants", file=f)
    finally:
        os.unlink(runner_local_path)
    print(f"Uploaded runner (file id: {uploaded_runner.id})")
    print(f"Uploaded {target_filename} (file id: {uploaded_target.id})")

    # Allow the container to reach PyPI and the Foundry endpoint.
    endpoint_host = urlparse(endpoint).hostname
    code_interpreter_tool = CodeInterpreterTool(
        container=AutoCodeInterpreterToolParam(
            file_ids=[uploaded_runner.id, uploaded_target.id],
            network_policy=ContainerNetworkPolicyAllowlistParam(
                allowed_domains=[
                    endpoint_host,
                    "pypi.org",
                    "files.pythonhosted.org",
                ],
            ),
        ),
    )

    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=PromptAgentDefinition(
            model=model_name,
            instructions=(
                "You are a Python execution assistant. Two files are mounted under "
                "/mnt/data/. Always use the code interpreter tool; never paraphrase "
                "or simulate output."
            ),
            tools=[code_interpreter_tool],
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    response = openai_client.responses.create(
        input=(
            "Run the uploaded runner inside the code interpreter.\n"
            "1. import subprocess, sys, io, contextlib, traceback, runpy, glob, importlib\n"
            "2. Install required pip packages and PRINT pip's returncode + stdout + stderr:\n"
            "     r = subprocess.run([sys.executable, '-m', 'pip', 'install', "
            "'azure-ai-projects', 'azure-identity', 'jsonref'], "
            "capture_output=True, text=True)\n"
            "     print('pip rc=', r.returncode)\n"
            "     print('pip stdout:', r.stdout)\n"
            "     print('pip stderr:', r.stderr)\n"
            "3. importlib.invalidate_caches()\n"
            "4. runner = glob.glob('/mnt/data/*runner.py')[0]\n"
            "5. Run the runner with stdout/stderr capture:\n"
            "     stdout_buf, stderr_buf, tb = io.StringIO(), io.StringIO(), ''\n"
            "     try:\n"
            "         with contextlib.redirect_stdout(stdout_buf), "
            "contextlib.redirect_stderr(stderr_buf):\n"
            "             runpy.run_path(runner, run_name='__main__')\n"
            "     except Exception:\n"
            "         tb = traceback.format_exc()\n"
            "     print('--- STDOUT ---'); print(stdout_buf.getvalue())\n"
            "     print('--- STDERR ---'); print(stderr_buf.getvalue())\n"
            "     print('--- TRACEBACK ---'); print(tb)\n"
            "Do not redact, truncate, or paraphrase any of the captured output."
        ),
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    )

    code_blocks = [out.code for out in response.output if out.type == "code_interpreter_call" and out.code]
    for i, code in enumerate(code_blocks, start=1):
        print(f"\nCode Interpreter code [{i}/{len(code_blocks)}]:")
        print(code)

    print(f"\nAgent response:\n{response.output_text}")

    print("\nCleaning up...")
    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    openai_client.files.delete(uploaded_runner.id)
    openai_client.files.delete(uploaded_target.id)
    print("Cleanup done")
