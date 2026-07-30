# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Run a sample file and validate its captured output with an LLM.

Example:
    python .\\tests\\samples\\llm-analyze.py --sample-path="samples\\agents\\tools\\sample_agent_file_search.py" \
        --foundry_project_endpoint="https://foundy6maq.services.ai.azure.com/api/projects/project6maq" \
        --foundry_model_name="gpt-5" \
        --llm_validation_project_endpoint="https://foundy6maq.services.ai.azure.com/api/projects/project6maq" \
        --llm_model_name="gpt-5"

Example using environment variables:
    python .\\tests\\samples\\llm-analyze.py --sample-path="samples\\agents\\tools\\sample_agent_file_search.py"
    This uses `.env` or existing environment variables for values such as
    `FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_MODEL_NAME`,
    `LLM_VALIDATION_PROJECT_ENDPOINT`, and `LLM_MODEL_NAME`.
    If `LLM_MODEL_NAME` is not set, validation defaults to `gpt-5.2`.

Example JSON output:
    {
      "correct": true,
      "llm_comment": "Execution completed successfully with substantive output.",
      "log_file": "C:\\Users\\<user>\\AppData\\Local\\Temp\\sample_agent_file_search_success_<timestamp>.log",
      "captured_prints_file": "C:\\Users\\<user>\\AppData\\Local\\Temp\\sample_agent_file_search_output_<timestamp>.txt",
      "duration": 117.912
    }

Notes:
    - Values are loaded from `.env` first. Explicit CLI arguments override environment variables.
    - `--sample-path` is the only dedicated CLI option. All other `--lower_case_name=value` arguments are mapped to uppercase environment variables and override `.env` values.
        - Validation uses `LLM_VALIDATION_PROJECT_ENDPOINT` and `LLM_MODEL_NAME` only.
            If `LLM_MODEL_NAME` is unset, the default validation model is `gpt-5.2`.
    - Extra lower-case CLI arguments are mapped to upper-case environment variables for the sample.
      Pass sample environment variables as extra CLI args using lower-case names. Examples:
          --foundry_project_endpoint="https://.../api/projects/..."
          --foundry_model_name="gpt-5"
          --llm_validation_project_endpoint="https://.../api/projects/..."
          --llm_model_name="gpt-5"
          --ai_search_index_name="index_sample"
      These become:
          FOUNDRY_PROJECT_ENDPOINT
          FOUNDRY_MODEL_NAME
          LLM_VALIDATION_PROJECT_ENDPOINT
          LLM_MODEL_NAME
          AI_SEARCH_INDEX_NAME
    - The final output is JSON only: correctness, LLM comment, temp log path, captured prints path, and duration.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from io import BytesIO
from pathlib import Path
from typing import cast

from dotenv import load_dotenv

SAMPLES_ROOT = Path(__file__).resolve().parent
TESTS_ROOT = SAMPLES_ROOT.parent
PROJECT_ROOT = TESTS_ROOT.parent

load_dotenv(PROJECT_ROOT / ".env")

sys.path.insert(0, str(PROJECT_ROOT))
try:
    from azure.ai.projects import AIProjectClient
    from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
finally:
    sys.path.pop(0)

sys.path.insert(0, str(TESTS_ROOT))

from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential

from sample_executor import (  # pylint: disable=wrong-import-position
    LIVE_LLM_VALIDATION_MODEL,
    AsyncSampleExecutor,
    SyncSampleExecutor,
)
from test_base import patched_open_crlf_to_lf  # pylint: disable=wrong-import-position

LIVE_MODE_ENV = {"AZURE_TEST_RUN_LIVE": "true"}


class _CredentialProvider:
    def __init__(self, credential: TokenCredential):
        self._credential = credential

    def get_credential(self, *_args, **_kwargs):
        return self._credential


class _AsyncCredentialProvider:
    def __init__(self, credential: AsyncTokenCredential):
        self._credential = credential

    def get_credential(self, *_args, **_kwargs):
        return self._credential


class _CliSampleExecutor(SyncSampleExecutor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_file_path: str | None = None

    def _write_error_log(self, reason: str, exception_info: str) -> str | None:
        self.log_file_path = super()._write_error_log(reason, exception_info)
        return self.log_file_path

    def _write_failed_log(self, reason: str) -> str | None:
        self.log_file_path = super()._write_failed_log(reason)
        return self.log_file_path

    def _write_passed_log(self, reason: str = "Validation passed") -> str | None:
        self.log_file_path = super()._write_passed_log(reason)
        return self.log_file_path

    def validate_print_calls_by_llm_cli(self, *, endpoint: str, model: str, instructions: str | None = None) -> dict:
        instructions = self._resolve_validation_instructions(instructions)
        response = None
        uploaded_file_ids: list[str] = []
        credential = cast(TokenCredential, self.tokenCredential)
        with (
            AIProjectClient(
                endpoint=endpoint,
                credential=credential,
                logging_enable=True,
            ) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            try:
                validation_text_file = BytesIO(self._build_validation_txt_bytes(self._build_validation_text()))
                validation_text_file.name = "sample_validation_log.txt"  # type: ignore[attr-defined]
                uploaded = openai_client.files.create(file=validation_text_file, purpose="assistants")
                uploaded_file_ids.append(uploaded.id)

                request_params = self._get_validation_request_params(instructions, model=model)
                file_ids = [uploaded.id]
                for file_path in self._collect_sample_code_files_for_code_interpreter():
                    with open(file_path, "rb") as source_file:
                        uploaded = openai_client.files.create(file=source_file, purpose="assistants")
                    uploaded_file_ids.append(uploaded.id)
                    file_ids.append(uploaded.id)

                request_params["tools"] = [
                    {"type": "code_interpreter", "container": {"type": "auto", "file_ids": file_ids}}
                ]
                response = openai_client.responses.create(**request_params)
                report = json.loads(response.output_text)
            except Exception as ex:  # pylint: disable=broad-exception-caught
                raw_output = getattr(response, "output_text", None)
                reason = f"LLM validation request/parsing failed: {type(ex).__name__}: {ex}"
                if raw_output:
                    reason += f". Raw output_text: {raw_output}"
                report = {"correct": False, "reason": reason}
            finally:
                for file_id in uploaded_file_ids:
                    try:
                        openai_client.files.delete(file_id)
                    except Exception:  # pylint: disable=broad-exception-caught
                        pass

        if report.get("correct"):
            self._write_passed_log(report.get("reason", "Validation passed"))
        else:
            self._write_failed_log(report.get("reason", "Validation failed"))
        return report


class _CliAsyncSampleExecutor(AsyncSampleExecutor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_file_path: str | None = None

    def _write_error_log(self, reason: str, exception_info: str) -> str | None:
        self.log_file_path = super()._write_error_log(reason, exception_info)
        return self.log_file_path

    def _write_failed_log(self, reason: str) -> str | None:
        self.log_file_path = super()._write_failed_log(reason)
        return self.log_file_path

    def _write_passed_log(self, reason: str = "Validation passed") -> str | None:
        self.log_file_path = super()._write_passed_log(reason)
        return self.log_file_path

    async def validate_print_calls_by_llm_async_cli(
        self, *, endpoint: str, model: str, instructions: str | None = None
    ) -> dict:
        instructions = self._resolve_validation_instructions(instructions)
        response = None
        uploaded_file_ids: list[str] = []
        credential = cast(AsyncTokenCredential, self.tokenCredential)
        async with (
            AsyncAIProjectClient(
                endpoint=endpoint,
                credential=credential,
                logging_enable=True,
            ) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            try:
                validation_text_file = BytesIO(self._build_validation_txt_bytes(self._build_validation_text()))
                validation_text_file.name = "sample_validation_log.txt"  # type: ignore[attr-defined]
                uploaded = await openai_client.files.create(file=validation_text_file, purpose="assistants")
                uploaded_file_ids.append(uploaded.id)

                request_params = self._get_validation_request_params(instructions, model=model)
                file_ids = [uploaded.id]
                for file_path in self._collect_sample_code_files_for_code_interpreter():
                    with open(file_path, "rb") as source_file:
                        uploaded = await openai_client.files.create(file=source_file, purpose="assistants")
                    uploaded_file_ids.append(uploaded.id)
                    file_ids.append(uploaded.id)

                request_params["tools"] = [
                    {"type": "code_interpreter", "container": {"type": "auto", "file_ids": file_ids}}
                ]
                response = await openai_client.responses.create(**request_params)
                report = json.loads(response.output_text)
            except Exception as ex:  # pylint: disable=broad-exception-caught
                raw_output = getattr(response, "output_text", None)
                reason = f"LLM validation request/parsing failed: {type(ex).__name__}: {ex}"
                if raw_output:
                    reason += f". Raw output_text: {raw_output}"
                report = {"correct": False, "reason": reason}
            finally:
                for file_id in uploaded_file_ids:
                    try:
                        await openai_client.files.delete(file_id)
                    except Exception:  # pylint: disable=broad-exception-caught
                        pass

        if report.get("correct"):
            self._write_passed_log(report.get("reason", "Validation passed"))
        else:
            self._write_failed_log(report.get("reason", "Validation failed"))
        return report


@contextmanager
def _temporary_env(env_vars: dict[str, str]):
    previous = {key: os.environ.get(key) for key in env_vars}
    os.environ.update(env_vars)
    try:
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


@contextmanager
def _suppress_terminal_output():
    with open(os.devnull, "w", encoding="utf-8") as devnull:
        with redirect_stdout(devnull), redirect_stderr(devnull):
            yield


def _parse_args() -> tuple[argparse.Namespace, dict[str, str]]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-path", "--sample_path", dest="sample_path")
    args, unknown = parser.parse_known_args()

    def _clean_cli_value(value: str) -> str:
        cleaned = value.strip()
        while cleaned and cleaned[-1] in {",", '"', "'"}:
            cleaned = cleaned[:-1].rstrip()
        while cleaned and cleaned[0] in {'"', "'"}:
            cleaned = cleaned[1:].lstrip()
        return cleaned

    if args.sample_path:
        args.sample_path = _clean_cli_value(args.sample_path)

    arg_env_vars: dict[str, str] = {}
    i = 0
    while i < len(unknown):
        item = unknown[i]
        if not item.startswith("--"):
            raise SystemExit(f"Unexpected argument: {item}")
        name = item[2:]
        if "=" in name:
            name, value = name.split("=", 1)
        else:
            i += 1
            if i >= len(unknown):
                raise SystemExit(f"Missing value for argument: --{name}")
            value = unknown[i]
        arg_env_vars[name.replace("-", "_").upper()] = _clean_cli_value(value)
        i += 1

    args.sample_path = args.sample_path or os.environ.get("SAMPLE_PATH")
    args.llm_endpoint = arg_env_vars.get("LLM_VALIDATION_PROJECT_ENDPOINT") or os.environ.get(
        "LLM_VALIDATION_PROJECT_ENDPOINT"
    )
    args.llm_model_name = (
        arg_env_vars.get("LLM_MODEL_NAME") or os.environ.get("LLM_MODEL_NAME") or LIVE_LLM_VALIDATION_MODEL
    )

    if not args.sample_path:
        raise SystemExit("Missing sample path. Provide --sample-path or set SAMPLE_PATH.")
    if not args.llm_endpoint:
        raise SystemExit(
            "Missing LLM endpoint. Set LLM_VALIDATION_PROJECT_ENDPOINT or pass --llm_validation_project_endpoint."
        )
    return args, arg_env_vars


def _build_result(report: dict, *, log_file: str | None, duration: float) -> dict:
    captured_prints_file = report.get("captured_prints_file")
    return {
        "correct": report.get("correct", False),
        "llm_comment": report.get("reason"),
        "log_file": log_file,
        "captured_prints_file": captured_prints_file,
        "duration": round(duration, 3),
    }


def _run_sync_sample(sample_path: str, args: argparse.Namespace, env_vars: dict[str, str]) -> dict:
    with DefaultAzureCredential() as credential:
        executor = _CliSampleExecutor(
            _CredentialProvider(credential),
            sample_path,
            env_vars=env_vars,
        )
        try:
            with _suppress_terminal_output():
                sample_start_time = time.perf_counter()
                executor.execute(patched_open_fn=patched_open_crlf_to_lf)
                sample_duration = time.perf_counter() - sample_start_time
                report = executor.validate_print_calls_by_llm_cli(endpoint=args.llm_endpoint, model=args.llm_model_name)
        except Exception as ex:  # pylint: disable=broad-exception-caught
            report = {"correct": False, "reason": f"Sample execution failed: {type(ex).__name__}: {ex}"}
            sample_duration = 0.0
    report["captured_prints_file"] = executor.output_file_path
    return _build_result(report, log_file=executor.log_file_path, duration=sample_duration)


async def _run_async_sample(sample_path: str, args: argparse.Namespace, env_vars: dict[str, str]) -> dict:
    async with AsyncDefaultAzureCredential() as credential:
        executor = _CliAsyncSampleExecutor(
            _AsyncCredentialProvider(credential),
            sample_path,
            env_vars=env_vars,
        )
        try:
            with _suppress_terminal_output():
                sample_start_time = time.perf_counter()
                await executor.execute_async(patched_open_fn=patched_open_crlf_to_lf)
                sample_duration = time.perf_counter() - sample_start_time
                report = await executor.validate_print_calls_by_llm_async_cli(
                    endpoint=args.llm_endpoint,
                    model=args.llm_model_name,
                )
        except Exception as ex:  # pylint: disable=broad-exception-caught
            report = {"correct": False, "reason": f"Sample execution failed: {type(ex).__name__}: {ex}"}
            sample_duration = 0.0
    report["captured_prints_file"] = executor.output_file_path
    return _build_result(report, log_file=executor.log_file_path, duration=sample_duration)


def main() -> int:
    args, env_vars = _parse_args()
    sample_path = (
        str((PROJECT_ROOT / args.sample_path).resolve()) if not os.path.isabs(args.sample_path) else args.sample_path
    )
    with _temporary_env(LIVE_MODE_ENV):
        result = (
            asyncio.run(_run_async_sample(sample_path, args, env_vars))
            if sample_path.endswith("_async.py")
            else _run_sync_sample(sample_path, args, env_vars)
        )

    print(json.dumps(result, indent=2))
    return 0 if result.get("correct") else 1


if __name__ == "__main__":
    raise SystemExit(main())
