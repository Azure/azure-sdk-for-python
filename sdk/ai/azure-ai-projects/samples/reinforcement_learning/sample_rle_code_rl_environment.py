# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to drive a hosted RLE Code RL environment
    using `project_client.rle.create_session(...)`. It leases a sandbox from the
    environment, then calls reset, step, and state. It submits one incorrect program and one correct
    program to show how the reward and verdict come back from env.step({"code": ...}).

    All requests are issued through the AIProjectClient pipeline against the Foundry project
    endpoint, just like the other operation groups on the client.

USAGE:
    python sample_rle_code_rl_environment.py --env-id <rle-environment-id>

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" azure-identity python-dotenv

    Set these environment variables or pass the matching command-line arguments:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview
       page of your Microsoft Foundry project.
    2) RLE_ENV_ID - Required. The hosted RLE environment ID.
"""

import argparse
import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

_ATTEMPTS = [
    "a, b = map(int, input().split())\nprint(a - b)",
    "a, b = map(int, input().split())\nprint(a + b)",
]


def main() -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run a basic RLE Code RL environment rollout.")
    parser.add_argument(
        "--endpoint",
        default=os.environ.get("FOUNDRY_PROJECT_ENDPOINT"),
        help="Foundry project endpoint, or set FOUNDRY_PROJECT_ENDPOINT.",
    )
    parser.add_argument(
        "--env-id",
        default=os.environ.get("RLE_ENV_ID"),
        help="Hosted RLE environment ID, or set RLE_ENV_ID.",
    )
    parser.add_argument("--seed", type=int, default=0, help="Task seed passed to env.reset().")
    args = parser.parse_args()

    if not args.endpoint:
        parser.error("provide --endpoint or set FOUNDRY_PROJECT_ENDPOINT")
    if not args.env_id:
        parser.error("provide --env-id or set RLE_ENV_ID")

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=args.endpoint, credential=credential) as project_client,
    ):
        with project_client.rle.create_session(args.env_id) as session:
            reset_result = session.reset(seed=args.seed)
            observation = reset_result.observation or {}
            problem = observation.get("problem", "")

            print("== reset ==")
            print(f"task tags: {observation.get('tags')}  num_tests: {observation.get('num_tests')}")
            print(f"problem (head): {problem.splitlines()[0][:72] if problem else '(none)'}\n")

            for index, code in enumerate(_ATTEMPTS, start=1):
                step_result = session.step({"code": code})
                step_observation = step_result.observation or {}
                print(f"== check_solution turn {index} ==")
                print(f"  submitted: {code.splitlines()[-1]}")
                print(f"  passed:    {step_observation.get('passed')}")
                print(f"  reward:    {step_result.reward}")

            state = session.state()
            print(f"\nstate: episode_id={state.episode_id} step_count={state.step_count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
