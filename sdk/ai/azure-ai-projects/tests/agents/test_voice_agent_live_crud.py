# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Recorded HTTP-only CRUD for all native persisted Live delegation owners."""

from contextlib import ExitStack

import pytest
from azure.ai.projects import models
from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import recorded_by_proxy

from test_base import TestBase
from live_agent_crud_test_base import (
    PROMPT_INSTRUCTIONS,
    assert_live_version,
    live_definition,
    liveAgentServicePreparer,
    owned_agent_name,
    sanitize_live_deployments,
)


class TestVoiceAgentLiveCrud(TestBase):
    # Separate nodes avoid parametrized-recorder decorator argument loss.
    @liveAgentServicePreparer()
    @recorded_by_proxy()
    def test_live_agent_client_crud(self, **kwargs):
        self._exercise_crud("client", **kwargs)

    @liveAgentServicePreparer()
    @recorded_by_proxy()
    def test_live_agent_responses_crud(self, **kwargs):
        self._exercise_crud("responses", **kwargs)

    @liveAgentServicePreparer()
    @recorded_by_proxy()
    def test_live_agent_managed_agent_crud(self, **kwargs):
        self._exercise_crud("foundry_managed_agent", **kwargs)

    def _exercise_crud(self, mode, **kwargs):
        sanitize_live_deployments(kwargs)
        name = owned_agent_name(mode, live=self.is_live)
        backend_name = owned_agent_name("prompt", live=self.is_live) if mode == "foundry_managed_agent" else None
        with self.create_client(allow_preview=True, **kwargs) as client:

            def delete_owned_version(agent_name, agent_version):
                result = client.agents.delete_version(agent_name=agent_name, agent_version=agent_version)
                assert isinstance(result, models.DeleteAgentVersionResponse)
                assert result.name == agent_name and result.version == agent_version
                assert result.deleted
                with pytest.raises(ResourceNotFoundError):
                    client.agents.get_version(agent_name=agent_name, agent_version=agent_version)

            with ExitStack() as cleanup:
                backend = None
                if backend_name is not None:
                    backend = client.agents.create_version(
                        agent_name=backend_name,
                        definition=models.PromptAgentDefinition(
                            model=kwargs["foundry_model_name"], instructions=PROMPT_INSTRUCTIONS
                        ),
                    )
                    cleanup.callback(delete_owned_version, backend_name, backend.version)
                    self._validate_agent_version(backend, expected_name=backend_name)
                    retrieved_backend = client.agents.get_version(
                        agent_name=backend_name, agent_version=backend.version
                    )
                    self._validate_agent_version(
                        retrieved_backend, expected_name=backend_name, expected_version=backend.version
                    )
                    assert isinstance(retrieved_backend.definition, models.PromptAgentDefinition)
                    assert retrieved_backend.definition.model == kwargs["foundry_model_name"]
                    assert retrieved_backend.definition.instructions == PROMPT_INSTRUCTIONS

                versions = {}
                for instructions in ("Delegate the spoken question.", "Delegate the spoken question; answer briefly."):
                    definition = live_definition(
                        mode,
                        kwargs["foundry_voice_live_model_name"],
                        kwargs["foundry_model_name"],
                        instructions,
                        backend=backend,
                    )
                    created = client.agents.create_version(agent_name=name, definition=definition)
                    cleanup.callback(delete_owned_version, name, created.version)
                    assert_live_version(created, definition, name=name)
                    assert created.version not in versions
                    versions[created.version] = definition

                latest_version = created.version
                agent = client.agents.get(agent_name=name)
                self._validate_agent(agent, expected_name=name, expected_latest_version=latest_version)
                assert_live_version(
                    agent.versions.latest, versions[latest_version], name=name, version_id=latest_version
                )
                for version_id, expected in versions.items():
                    retrieved = client.agents.get_version(agent_name=name, agent_version=version_id)
                    assert_live_version(retrieved, expected, name=name, version_id=version_id)

                listed = {version.version: version for version in client.agents.list_versions(agent_name=name)}
                assert set(listed) == set(versions)
                for version_id, expected in versions.items():
                    assert_live_version(listed[version_id], expected, name=name, version_id=version_id)
