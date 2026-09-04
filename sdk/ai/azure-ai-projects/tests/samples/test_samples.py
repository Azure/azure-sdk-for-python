# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import re
import pytest
from devtools_testutils import (
    recorded_by_proxy,
    AzureRecordedTestCase,
    RecordedTransport,
)
from test_base import (
    agentInsightsServicePreparer,
    fineTuningServicePreparer,
    modelsServicePreparer,
    servicePreparer,
)
from sample_executor import (
    AdditionalSampleTestDetail,
    SyncSampleExecutor,
    additionalSampleTests,
    get_sample_paths,
    SamplePathPasser,
)
from test_samples_helpers import get_sample_env_vars
from test_fine_tuning_samples_helpers import get_fine_tuning_sample_env_vars


def _assert_agent_insights_output(print_output_calls: list[str]) -> None:
    output = "\n".join(print_output_calls)

    assert re.search(
        r"^Run status: succeeded$", output, re.MULTILINE
    ), "Agent Insights run did not succeed."

    def read_count(label: str) -> int:
        match = re.search(rf"^{re.escape(label)}: (\d+)$", output, re.MULTILINE)
        assert match is not None, f"Agent Insights sample did not print '{label}'."
        return int(match.group(1))

    assert read_count("Traces analyzed") > 0
    assert (
        read_count("Insights created")
        + read_count("Insights updated")
        + read_count("Insights reopened")
        > 0
    )
    assert read_count("Listed insights") > 0


class TestSamples(AzureRecordedTestCase):

    # To run this test with a specific sample, use:
    # pytest tests/samples/test_samples.py::TestSamples::test_agent_tools_samples[sample_agent_memory_search]
    @servicePreparer()
    # @additionalSampleTests(
    #     [
    #         AdditionalSampleTestDetail( # 2/28/2026 westus2 get 500
    #             test_id="sample_agent_azure_function",
    #             sample_filename="sample_agent_azure_function.py",
    #             env_vars={
    #                 "STORAGE_INPUT_QUEUE_NAME": "sanitized_input_queue_name",
    #                 "STORAGE_OUTPUT_QUEUE_NAME": "sanitized_output_queue_name",
    #                 "STORAGE_QUEUE_SERVICE_ENDPOINT": "sanitized_queue_service_endpoint",
    #             },
    #         ),
    #     ]
    # )
    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "agents/tools",
            samples_to_skip=[
                "sample_agent_file_search_structured_inputs.py",  # No issue to run. Just postpone recording.
                "sample_agent_code_interpreter_structured_inputs.py",  # No issue to run. Just postpone recording.
                "sample_agent_azure_function.py",  # In the list of additional sample tests above due to more parameters needed
                "sample_agent_computer_use.py",  # 400 BadRequestError: Invalid URI (URI string too long)
                "sample_agent_browser_automation.py",  # APITimeoutError: request timed out
                "sample_agent_openapi.py",  # 400 2/28/2026 validation/tool_user_error; failing weather GET curl call in OpenAPI tool
                "sample_agent_memory_search.py",  # Skipped until re-enabled and recorded on Foundry endpoint that supports the new versioning schema
                "sample_agent_to_agent.py",  # Skipped not sample should work, but not able to obtain a project endpoint that work with a2a at this moment
            ],
        ),
    )
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX2)
    def test_agent_tools_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = SyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        executor.execute()
        executor.validate_print_calls_by_llm()

    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "memories",
            samples_to_skip=[],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX2)
    # To run this test: pytest tests/samples/test_samples.py::TestSamples::test_memory_samples -s
    def test_memory_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = SyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        executor.execute()
        executor.validate_print_calls_by_llm()

    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "agents",
            samples_to_skip=[
                "sample_external_agents_crud.py",  # Skipped until recordings are available.
                "sample_workflow_multi_agent.py",  # No issue to run.  Just postpone recording.
                "sample_workflow_multi_agent_with_mcp_approval.py",  # No issue to run.  Just postpone recording.
            ],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX2)
    def test_agents_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = SyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        executor.execute()
        executor.validate_print_calls_by_llm()

    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "agent_insights",
            samples_to_skip=[],
        ),
    )
    @agentInsightsServicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX2)
    def test_agent_insights_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = SyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        executor.execute()
        _assert_agent_insights_output(executor.print_output_calls)
        executor.validate_print_calls_by_llm()

    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "connections",
            samples_to_skip=[],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX2)
    def test_connections_samples(self, sample_path: str, **kwargs) -> None:
        kwargs = kwargs.copy()
        kwargs["connection_name"] = "mcp"
        env_vars = get_sample_env_vars(kwargs)
        executor = SyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        executor.execute()
        executor.validate_print_calls_by_llm()

    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "files",
            samples_to_skip=[],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX2)
    def test_files_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = SyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        executor.execute()
        executor.validate_print_calls_by_llm()

    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "deployments",
            samples_to_skip=[],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX2)
    def test_deployments_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = SyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        executor.execute()
        executor.validate_print_calls_by_llm()

    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "models",
            samples_to_test=[
                # `sample_models_basic.py` uses the `create()` helper which shells out
                # to AzCopy. AzCopy traffic isn't captured by the test proxy, so the
                # sample can't be replayed from a recording. Live re-recording is still
                # exercised via the standalone tests in `tests/models/`.
                "sample_models_create_and_poll.py",
            ],
        ),
    )
    @modelsServicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX2)
    def test_models_samples(self, sample_path: str, **kwargs) -> None:
        import secrets  # local import to avoid module-level dep

        env_vars = get_sample_env_vars(kwargs)
        # Foundry permanently reserves a `<name>/<version>` asset namespace even
        # after `models.delete`, so every live re-recording needs a unique name.
        # Sanitize back to a stable value in conftest so playback URLs match.
        suffix = secrets.token_hex(4) if self.is_live else "00000000"
        env_vars["MODEL_NAME"] = f"recsmplmdl{suffix}"
        env_vars["MODEL_VERSION"] = "1"
        executor = SyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        executor.execute()
        # `validate_print_calls_by_llm` is intentionally not called: it requires
        # an Azure OpenAI connection on the Foundry project, which the canary
        # project used for `.beta.models` recordings does not have. The sample
        # is still validated end-to-end by `executor.execute()` (any exception
        # fails the test).

    @servicePreparer()
    # @additionalSampleTests(
    #     [
    #         AdditionalSampleTestDetail(
    #             test_id="sample_dataset_generation_job_simpleqna_with_prompt_source",
    #             sample_filename="sample_dataset_generation_job_simpleqna_with_prompt_source.py",
    #             env_vars={
    #                 "POLL_INTERVAL_SECONDS": "60",
    #             },
    #         ),
    #     ]
    # )
    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "datasets",
            samples_to_skip=[
                "sample_dataset_generation_job_simpleqna_with_prompt_source.py",  # Specified through AdditionalSampleTestDetail
                "sample_dataset_generation_job_traces_for_finetuning.py",  # PR #47067: recording not yet available
                "sample_dataset_generation_job_simpleqna_for_finetuning.py",  # PR #47067: recording not yet available
                "sample_dataset_generation_job_traces_for_evaluation.py",  # PR #47067: recording not yet available
                "sample_dataset_generation_job_simpleqna_with_agent_source.py",  # PR #47067: recording not yet available
                "sample_dataset_generation_job_simpleqna_with_file_source.py",  # PR #47067: recording not yet available
                "sample_dataset_generation_job_simpleqna_for_finetuning_with_app_polling.py",  # Need test recordings
            ],
        ),
    )
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX2)
    # To run this test: pytest tests/samples/test_samples.py::TestSamples::test_datasets_samples[sample_dataset_generation_job_simpleqna_with_prompt_source] -s
    def test_datasets_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = SyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        executor.execute()
        executor.validate_print_calls_by_llm()

    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "chat_completions",
            samples_to_skip=[],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX2)
    def test_chat_completions_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = SyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        executor.execute()
        executor.validate_print_calls_by_llm()

    @servicePreparer()
    @additionalSampleTests(
        [
            AdditionalSampleTestDetail(
                test_id="sample_create_hosted_agent_from_remote_build",
                sample_filename="sample_create_hosted_agent_from_code.py",
                env_vars={
                    "FOUNDRY_HOSTED_AGENT_REMOTE_BUILD": "true",
                    "ZIP_FILE_PATH": "tests/samples/assets/basic-agent.zip",
                },
            ),
            AdditionalSampleTestDetail(
                test_id="sample_create_hosted_agent_from_code",
                sample_filename="sample_create_hosted_agent_from_code.py",
                env_vars={
                    "FOUNDRY_HOSTED_AGENT_REMOTE_BUILD": "false",
                    "ZIP_FILE_PATH": "tests/samples/assets/basic-agent-prebuilt.zip",
                },
            ),
            AdditionalSampleTestDetail(
                test_id="sample_session_log_stream",
                sample_filename="sample_session_log_stream.py",
                env_vars={
                    "ZIP_FILE_PATH": "tests/samples/assets/basic-agent.zip",
                },
            ),
            AdditionalSampleTestDetail(
                test_id="sample_sessions_crud",
                sample_filename="sample_sessions_crud.py",
                env_vars={
                    "ZIP_FILE_PATH": "tests/samples/assets/basic-agent.zip",
                },
            ),
            AdditionalSampleTestDetail(
                test_id="sample_sessions_files_upload_download",
                sample_filename="sample_sessions_files_upload_download.py",
                env_vars={
                    "ZIP_FILE_PATH": "tests/samples/assets/basic-agent.zip",
                },
            ),
            AdditionalSampleTestDetail(
                test_id="sample_agent_user_identity_isolation",
                sample_filename="sample_agent_user_identity_isolation.py",
                env_vars={
                    "ZIP_FILE_PATH": "tests/samples/assets/basic-agent.zip",
                    "DELEGATED_USER_IDENTITY": "86636782-5c1b-455e-b25f-91fc467ac05d",
                    "DELEGATED_USER_IDENTITY_2": "340fcd8b-b87e-41d5-b4d5-fc02df14e807",
                },
            ),
        ]
    )
    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "hosted_agents",
            samples_to_skip=[
                "sample_toolbox_with_skill.py",  # Skip due to RBAC assignment that cannot be recorded
                "sample_create_hosted_agent_from_code.py",  # Specified through AdditionalSampleTestDetail
                "sample_agent_user_identity_isolation.py",  # Specified through AdditionalSampleTestDetail
                "sample_session_log_stream.py",  # Specified through AdditionalSampleTestDetail
                "sample_sessions_crud.py",  # Specified through AdditionalSampleTestDetail
                "sample_sessions_files_upload_download.py",  # Specified through AdditionalSampleTestDetail
                "sample_routines_with_dispatch.py",  # 500
                "sample_routines_with_schedule_trigger.py",  # 500
                "sample_routines_with_timer_trigger.py",  # Timer is used causing request response not matched
                "sample_routines_with_github_issue_trigger.py",  # Cannot run without interact on Github
                "sample_routines_with_teams_message_trigger.py",  # Cannot run without live Teams event
                "sample_toolbox_with_reminder_preview.py",  # Skip due to RBAC assignment that cannot be recorded
            ],
        ),
    )
    @SamplePathPasser()
    # To run a single sample: pytest tests\samples\test_samples.py::TestSamples::test_hosted_agents_samples[sample_agent_endpoint] -s
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX2)
    def test_hosted_agents_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = SyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        executor.execute()

        if os.path.basename(sample_path) == "sample_agent_user_identity_isolation.py":
            # This sample intentionally exercises a wrong-user 404 branch to
            # prove response-chain isolation, so execution success is the
            # authoritative validation signal for this case.
            return

        executor.validate_print_calls_by_llm()

    @additionalSampleTests(
        [
            AdditionalSampleTestDetail(
                test_id="sample_skills_upload_and_download",
                sample_filename="sample_skills_upload_and_download.py",
                env_vars={
                    "ZIP_FILE_PATH": "tests/samples/assets/team-status-update.zip",
                },
            ),
        ]
    )
    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "skills",
            samples_to_skip=[
                "sample_skills_upload_and_download.py",  # Specified through AdditionalSampleTestDetail
            ],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX2)
    def test_skills_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = SyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        executor.execute()
        executor.validate_print_calls_by_llm()

    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "toolboxes",
            samples_to_skip=[],
        ),
    )
    @servicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX2)
    def test_toolboxes_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_sample_env_vars(kwargs)
        executor = SyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        executor.execute()
        executor.validate_print_calls_by_llm()

    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "finetuning",
            samples_to_skip=[
                "sample_finetuning_reinforcement_job.py",  # 403 PermissionDeniedError: missing Microsoft.MachineLearningServices/workspaces/agents/action
                "sample_finetuning_dpo_job.py",  # 401 AuthenticationError: missing AIServices/agents/write data action
            ],
        ),
    )
    @fineTuningServicePreparer()
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX2)
    def test_finetuning_samples(self, sample_path: str, **kwargs) -> None:
        env_vars = get_fine_tuning_sample_env_vars(sample_path, kwargs)
        executor = SyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
        executor.execute()
        executor.validate_print_calls_by_llm()
