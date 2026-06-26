# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to drive a hosted RLE Code RL environment by leasing a sandbox,
    then calling reset, step, and state. It submits one incorrect program and one correct program
    to show how the reward and verdict come back from env.step({"code": ...}).

USAGE:
    python sample_rle_code_rl_environment.py --env-id <rle-environment-id> --project <rle-project>

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables or pass the matching command-line arguments:
    1) RLE_ENV_ID - Required. The hosted RLE environment ID.
    2) RLE_PROJECT - Required. The RLE project name.
    3) RLE_CONTROL_PLANE - Optional. The RLE control-plane endpoint. Defaults to http://localhost:5000.
    4) RLE_TOKEN - Optional. Bearer token for RLE control-plane and data-plane calls.
"""

import argparse
import os

from dotenv import load_dotenv

from azure.ai.projects import RLEEnvironment  # pyright: ignore [reportAttributeAccessIssue]


_ATTEMPTS = [
    "a, b = map(int, input().split())\nprint(a - b)",
    "a, b = map(int, input().split())\nprint(a + b)",
]


def main() -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run a basic RLE Code RL environment rollout.")
    parser.add_argument(
        "--env-id",
        default=os.environ.get("RLE_ENV_ID"),
        help="Hosted RLE environment ID, or set RLE_ENV_ID.",
    )
    parser.add_argument(
        "--project",
        default=os.environ.get("RLE_PROJECT"),
        help="RLE project name, or set RLE_PROJECT.",
    )
    parser.add_argument(
        "--control-plane",
        default=os.environ.get("RLE_CONTROL_PLANE"),
        help="RLE control-plane endpoint, or set RLE_CONTROL_PLANE.",
    )
    parser.add_argument("--seed", type=int, default=0, help="Task seed passed to env.reset().")
    args = parser.parse_args()

    if not args.env_id:
        parser.error("provide --env-id or set RLE_ENV_ID")
    if not args.project:
        parser.error("provide --project or set RLE_PROJECT")

    with RLEEnvironment(
        env_id=args.env_id,
        project=args.project,
        control_plane=args.control_plane,
        token=os.environ.get("RLE_TOKEN"),
    ) as env:
        reset_result = env.reset(seed=args.seed)
        observation = reset_result.observation or {}
        problem = observation.get("problem", "")

        print("== reset ==")
        print(f"task tags: {observation.get('tags')}  num_tests: {observation.get('num_tests')}")
        print(f"problem (head): {problem.splitlines()[0][:72] if problem else '(none)'}\n")

        for index, code in enumerate(_ATTEMPTS, start=1):
            step_result = env.step({"code": code})
            step_observation = step_result.observation or {}
            print(f"== check_solution turn {index} ==")
            print(f"  submitted: {code.splitlines()[-1]}")
            print(f"  passed:    {step_observation.get('passed')}")
            print(f"  reward:    {step_result.reward}")

        state = env.state()
        print(f"\nstate: episode_id={state.episode_id} step_count={state.step_count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())