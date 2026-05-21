# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Live, recorded async tests for ``project_client.beta.models``.

Mirrors :mod:`tests.models.test_models` for the async client. ``models_create``
itself is implemented only on the sync client (it shells out to ``azcopy``); the
async surface is exercised via ``list``, ``list_versions``, ``get`` and
``delete`` against a model registered with the sync helper as part of the
fixture.
"""

import os

import pytest
from devtools_testutils import (
    add_general_regex_sanitizer,
    is_live,
    is_live_and_not_recording,
)
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

from test_base import TestBase, servicePreparer

script_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.environ.get("DATA_FOLDER", os.path.join(script_dir, "../test_data/models"))


@pytest.mark.skipif(
    not is_live_and_not_recording(),
    reason="Skipped when using recordings due to flakiness of recording blob storage calls",
)
class TestModelsAsync(TestBase):

    # cls & pytest tests\models\test_models_async.py::TestModelsAsync::test_models_async_list_get_delete -s
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_models_async_list_get_delete(self, **kwargs):
        """Register a model with the sync helper, then drive list/get/delete async."""
        from azure.ai.projects import AIProjectClient as SyncAIProjectClient

        model_name = self.test_models_params["model_name_1"]
        model_version = self.test_models_params["model_version"]
        expected_model_name = model_name if is_live() else "sanitized-model-name"
        add_general_regex_sanitizer(regex=r"test-model-name-\d{5}", value="sanitized-model-name", function_scoped=True)

        endpoint = kwargs["foundry_project_endpoint"]

        # Set up: register a model using the sync helper (azcopy is sync).
        with SyncAIProjectClient(
            endpoint=endpoint,
            credential=self.get_credential(SyncAIProjectClient, is_async=False),
        ) as sync_client:
            registered = sync_client.beta.models.models_create(
                name=model_name,
                version=model_version,
                source=data_folder,
                weight_type="FullWeight",
                description="Registered by test_models_async",
                tags={"source": "test_models_async.py"},
            )
            assert registered is not None
            assert registered.name == expected_model_name

        # Exercise: drive the async client.
        async with self.create_async_client(**kwargs) as project_client:

            print(f"[test_models_async] get {model_name}@{model_version}")
            fetched = await project_client.beta.models.get(name=model_name, version=model_version)
            assert fetched.name == expected_model_name
            assert fetched.version == model_version

            print(f"[test_models_async] list_versions({model_name!r})")
            versions = []
            async for mv in project_client.beta.models.list_versions(name=model_name):
                versions.append(mv)
            assert any(mv.version == model_version for mv in versions)

            print("[test_models_async] list (latest of every model)")
            seen = 0
            async for mv in project_client.beta.models.list():
                seen += 1
                assert mv.name and mv.version
            assert seen > 0

            print(f"[test_models_async] delete {model_name}@{model_version}")
            try:
                await project_client.beta.models.delete(name=model_name, version=model_version)
            except HttpResponseError as ex:
                if ex.status_code != 200:
                    raise

            print(f"[test_models_async] get on deleted {model_name}@{model_version} should 404")
            with pytest.raises((ResourceNotFoundError, HttpResponseError)):
                await project_client.beta.models.get(name=model_name, version=model_version)
