# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this async sample demonstrates how to drive a hosted RLE (OpenEnv)
    Wordle environment using `project_client.rle.get_openenv_client(...)`. It hands out an instance
    via `get_instance()`, which drives reset, step, and state through the Foundry project endpoint.
    The sample submits a sequence of 5-letter word guesses and prints the per-letter feedback and
    reward signals that come back from instance.step(message=...).

    This mirrors sample_rle.py, using the async client so every reset/step is awaited on the async
    pipeline. All requests are issued through the AIProjectClient pipeline against the Foundry project
    endpoint, just like the other operation groups on the client.

USAGE:
    python sample_rle_async.py --name <rle-environment-name> --version <version>

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" azure-identity python-dotenv

    Set these environment variables or pass the matching command-line arguments:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview
       page of your Microsoft Foundry project.
    2) FOUNDRY_PROJECT_API_KEY - Required. The project API key used to authenticate requests.
    3) RLE_ENV_NAME - Required. The hosted RLE environment name.
    4) RLE_ENV_VERSION - Optional. The hosted RLE environment version.
"""

import argparse
import asyncio
import os
from typing import Any, Mapping

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.ai.projects.aio import AIProjectClient

# A handful of distinct valid 5-letter guesses for the Wordle environment.
_GUESSES = ["crane", "moist", "pluck", "vigor"]


def _summarize(observation: Mapping[str, Any]) -> str:
    """Extract the most recent Wordle feedback line from a step observation."""
    metadata = observation.get("metadata") or {}
    messages = metadata.get("raw_messages") or []
    content = messages[-1].get("content", "") if messages else ""
    marker = "Feedback:"
    if marker in content:
        tail = content.rsplit(marker, 1)[1].strip().splitlines()
        return " | ".join(line.strip() for line in tail[:2])
    return content.strip().splitlines()[-1] if content.strip() else "(no feedback)"


async def run(args):
    # Authenticate with a project API key instead of an Entra token: the key is injected as the
    # "api-key" header via a custom authentication policy, bypassing BearerTokenCredentialPolicy.
    key_credential = AzureKeyCredential(args.api_key)
    async with AIProjectClient(
        endpoint=args.endpoint,
        credential=key_credential,
        authentication_policy=AzureKeyCredentialPolicy(key_credential, "api-key"),
    ) as project_client:
        # get_openenv_client is a plain (non-awaited) factory: it does no I/O. Entering the async
        # context resolves the environment and creates the instance group that reserves quota (a
        # missing environment fails on entry).
        async with project_client.rle.get_openenv_client(
            name=args.name,
            version=args.version,
        ) as openenv_client:
            # get_instance() leases a running instance on demand (create + poll to Running), so on the
            # async surface it is awaited; the returned instance is then an async context manager.
            instance = await openenv_client.get_instance()
            async with instance:
                reset_result = await instance.reset(seed=args.seed)
                observation = reset_result.observation or {}
                prompt = observation.get("prompt", "")

                print("== reset ==")
                first_line = prompt.strip().splitlines()[0] if prompt.strip() else "(no prompt)"
                print(f"prompt (head): {first_line}\n")

                for index, guess in enumerate(_GUESSES, start=1):
                    step_result = await instance.step(message=guess)
                    step_observation = step_result.observation or {}
                    metadata = step_observation.get("metadata") or {}
                    rewards = metadata.get("reward_signals") or {}
                    print(f"== guess {index}: {guess} ==")
                    print(f"  feedback:  {_summarize(step_observation)}")
                    print(f"  greens:    {rewards.get('wordle.greens')}  yellows: {rewards.get('wordle.yellows')}")
                    print(f"  correct:   {rewards.get('wordle.correct')}  reward: {step_result.reward}")
                    if rewards.get("wordle.correct") or step_result.done:
                        print("  solved!")
                        break

                state = await instance.state()
                print(f"\nstate: episode_id={state.episode_id} step_count={state.step_count}")


def main() -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run a basic RLE Wordle environment rollout.")
    parser.add_argument(
        "--endpoint",
        default=os.environ.get("FOUNDRY_PROJECT_ENDPOINT"),
        help="Foundry project endpoint, or set FOUNDRY_PROJECT_ENDPOINT.",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("FOUNDRY_PROJECT_API_KEY"),
        help="Project API key, or set FOUNDRY_PROJECT_API_KEY.",
    )
    parser.add_argument(
        "--name",
        default=os.environ.get("RLE_ENV_NAME"),
        help="Hosted RLE environment name, or set RLE_ENV_NAME.",
    )
    parser.add_argument(
        "--version",
        default=os.environ.get("RLE_ENV_VERSION"),
        help="Hosted RLE environment version, or set RLE_ENV_VERSION (optional).",
    )
    parser.add_argument("--seed", type=int, default=0, help="Task seed passed to instance.reset().")
    args = parser.parse_args()

    if not args.endpoint:
        parser.error("provide --endpoint or set FOUNDRY_PROJECT_ENDPOINT")
    if not args.api_key:
        parser.error("provide --api-key or set FOUNDRY_PROJECT_API_KEY")
    if not args.name:
        parser.error("provide --name or set RLE_ENV_NAME")

    asyncio.run(run(args))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
