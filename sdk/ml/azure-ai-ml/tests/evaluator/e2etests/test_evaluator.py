import os
import re
import uuid
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import sleep_if_live

from azure.ai.ml import MLClient, load_model
from azure.ai.ml._restclient.v2022_05_01.models import ListViewType
from azure.ai.ml.constants._common import LONG_URI_REGEX_FORMAT
from azure.ai.ml.entities._assets import Model
from azure.core.paging import ItemPaged
from pathlib import Path
from azure.ai.ml.exceptions import ValidationException


@pytest.fixture
def uuid_name() -> str:
    name = str(uuid.uuid1())
    yield name


@pytest.fixture
def artifact_path(tmpdir_factory) -> str:  # type: ignore
    file_name = tmpdir_factory.mktemp("artifact_testing").join("artifact_file.txt")
    file_name.write("content")
    return str(file_name)


# previous bodiless_matcher fixture doesn't take effect because of typo, please add it in method level if needed


def _load_flow(name: str, version: str = "42", **kwargs) -> Model:
    """Load the flow supplied with the tests."""
    return Model(
        path="./tests/test_configs/flows/basic/",
        name=name,
        type="custom_model",
        description="This is evaluator.",
        version=version,
        properties={"is-promptflow": "true", "is-evaluator": "true"},
        **kwargs,
    )


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.production_experiences_test
class TestEvaluator(AzureRecordedTestCase):
    def test_crud_file(self, client: MLClient, randstr: Callable[[], str]) -> None:
        model_name = randstr("model_name")

        model = _load_flow(model_name, version="3")
        model.name = model_name
        model = client.evaluators.create_or_update(model)
        assert model.name == model_name
        assert model.version == "3"
        assert model.description == "This is evaluator."
        assert model.type == "custom_model"
        assert "is-promptflow" in model.properties and model.properties["is-promptflow"] == "true"
        assert "is-evaluator" in model.properties and model.properties["is-evaluator"] == "true"
        assert re.match(LONG_URI_REGEX_FORMAT, model.path)

        model = client.evaluators.get(name=model.name, version="3")
        assert model.name == model_name
        assert model.version == "3"
        assert model.description == "This is evaluator."
        assert "is-promptflow" in model.properties and model.properties["is-promptflow"] == "true"
        assert "is-evaluator" in model.properties and model.properties["is-evaluator"] == "true"

        models = client.evaluators.list(name=model_name)
        assert isinstance(models, ItemPaged)
        test_model = next(iter(models), None)
        assert isinstance(test_model, Model)

        # TODO: Enable this test when listing without name will be available.
        # models = client.evaluators.list()
        # assert isinstance(models, Iterator)
        # test_model = next(iter(models), None)
        # assert isinstance(test_model, Model)

    def test_crud_evaluator_with_stage(self, client: MLClient, randstr: Callable[[], str]) -> None:
        model_name = randstr("model_prod_name")
        model = _load_flow(model_name, stage="Production", version="3")

        model = client.evaluators.create_or_update(model)
        assert model.name == model_name
        assert model.version == "3"
        assert model.description == "This is evaluator."
        assert model.type == "custom_model"
        assert model.stage == "Production"
        assert re.match(LONG_URI_REGEX_FORMAT, model.path)

        model = client.evaluators.get(name=model.name, version="3")
        assert model.name == model_name
        assert model.version == "3"
        assert model.description == "This is evaluator."
        assert model.stage == "Production"

        model_list = client.evaluators.list(name=model.name, stage="Production")
        model_stage_list = [m.stage for m in model_list if m is not None]
        assert model.stage in model_stage_list

    def test_evaluators_get_latest_label(self, client: MLClient, randstr: Callable[[], str]) -> None:
        model_name = f"model_{randstr('name')}"
        for version in ["1", "2", "3", "4"]:
            model = _load_flow(model_name, version=version)
            client.evaluators.create_or_update(model)
            assert client.evaluators.get(name=model_name, label="latest").version == version

    @pytest.mark.skip(
        "Skipping test for archive and restore as we have removed it from interface. "
        "These test will be available when the appropriate API will be enabled at "
        "GenericAssetService."
    )
    def test_evaluator_archive_restore_version(self, client: MLClient, randstr: Callable[[], str]) -> None:
        model_name = f"model_{randstr('name')}"

        versions = ["1", "2"]
        version_archived = versions[0]
        for version in versions:
            model = _load_flow(model_name, version=version)
            client.evaluators.create_or_update(model)

        def get_evaluator_list():
            # Wait for list index to update before calling list command
            sleep_if_live(30)
            model_list = client.evaluators.list(name=model_name, list_view_type=ListViewType.ACTIVE_ONLY)
            return [m.version for m in model_list if m is not None]

        assert version_archived in get_evaluator_list()
        client.evaluators.archive(name=model_name, version=version_archived)
        assert version_archived not in get_evaluator_list()
        client.evaluators.restore(name=model_name, version=version_archived)
        assert version_archived in get_evaluator_list()

    @pytest.mark.skip(reason="Task 1791832: Inefficient, possibly causing testing pipeline to time out.")
    def test_evaluator_archive_restore_container(self, client: MLClient, randstr: Callable[[], str]) -> None:
        model_name = f"model_{randstr('name')}"
        version = "1"
        model = _load_flow(model_name, version=version)

        client.evaluators.create_or_update(model)

        def get_evaluator_list():
            # Wait for list index to update before calling list command
            sleep_if_live(30)
            model_list = client.evaluators.list(list_view_type=ListViewType.ACTIVE_ONLY)
            return [m.name for m in model_list if m is not None]

        assert model_name in get_evaluator_list()
        client.evaluators.archive(name=model_name)
        assert model_name not in get_evaluator_list()
        client.evaluators.restore(name=model_name)
        assert model_name in get_evaluator_list()

    @pytest.mark.skipif(
        condition=not is_live(),
        reason="Registry uploads do not record well. Investigate later",
    )
    def test_create_get_download_evaluator_registry(
        self, registry_client: MLClient, randstr: Callable[[], str]
    ) -> None:
        model_name = randstr("model_name")
        model_version = "2"

        model_entity = _load_flow(model_name, version=model_version)
        model = registry_client.evaluators.create_or_update(model_entity)
        assert model.name == model_name
        assert model.version == model_version
        assert model.description == "This is evaluator."
        assert model.type == "custom_model"

        model_get = registry_client.evaluators.get(name=model_name, version=model_version)
        assert model == model_get
        assert model_get.name == model_name
        assert model_get.version == model_version
        assert model_get.description == "This is evaluator."
        assert model_get.type == "custom_model"

        registry_client.evaluators.download(name=model_name, version=model_version, download_path="downloaded")
        wd = os.path.join(os.getcwd(), f"downloaded/{model_name}")
        assert os.path.exists(wd)
        assert os.path.exists(f"{wd}/basic/flow.dag.yaml")

    @pytest.mark.parametrize("use_registry", [True, False])
    @pytest.mark.skipif(
        condition=not is_live(),
        reason="Registry uploads do not record well. Investigate later",
    )
    def test_list_evaluator(
        self,
        registry_client: MLClient,
        client: MLClient,
        randstr: Callable[[], str],
        use_registry: bool,
    ) -> None:
        ml_cli = registry_client if use_registry else client
        model_name = randstr("model_name")
        model_version = "1"
        model_entity = _load_flow(model_name, version=model_version)
        model = ml_cli.evaluators.create_or_update(model_entity)
        assert model.name == model_name
        assert model.version == model_version
        assert model.description == "This is evaluator."
        assert model.type == "custom_model"

        # Check that we only can create evaluators with the same name.
        model_path = Path("./tests/test_configs/model/model_full.yml")
        model_version = "2"

        model_entity = load_model(model_path)
        model_entity.name = model_name
        model_entity.version = model_version
        with pytest.raises(ValidationException) as cm:
            ml_cli.models.create_or_update(model_entity)
        assert "previous version of model was marked as promptflow evaluator" in cm.value.args[0]

        # Check that only one model was created.
        model_list = list(ml_cli.evaluators.list(model_name))
        assert len(model_list) == 1
        assert "is-promptflow" in model_list[0].properties and model_list[0].properties["is-promptflow"] == "true"
        assert "is-evaluator" in model_list[0].properties and model_list[0].properties["is-evaluator"] == "true"
