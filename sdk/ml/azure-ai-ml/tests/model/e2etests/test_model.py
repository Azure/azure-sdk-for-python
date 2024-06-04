import os
import re
import uuid
from pathlib import Path
from typing import Callable, Iterator
from unittest.mock import patch

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import sleep_if_live

from azure.ai.ml import MLClient, load_model
from azure.ai.ml._restclient.v2022_05_01.models import ListViewType
from azure.ai.ml.constants._common import LONG_URI_REGEX_FORMAT
from azure.ai.ml.entities._assets import Model
from azure.core.paging import ItemPaged


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


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.production_experiences_test
class TestModel(AzureRecordedTestCase):
    def test_crud_file(self, client: MLClient, randstr: Callable[[], str], tmp_path: Path) -> None:
        path = Path("./tests/test_configs/model/model_full.yml")
        model_name = randstr("model_name")

        model = load_model(path)
        model.name = model_name
        model = client.models.create_or_update(model)
        assert model.name == model_name
        assert model.version == "3"
        assert model.description == "this is my test model"
        assert model.type == "mlflow_model"
        assert re.match(LONG_URI_REGEX_FORMAT, model.path)

        with pytest.raises(Exception):
            with patch("azure.ai.ml._artifacts._artifact_utilities.get_object_hash", return_value="DIFFERENT_HASH"):
                model = load_model(source=artifact_path)
                model = client.models.create_or_update(model)

        model = client.models.get(model.name, "3")
        assert model.name == model_name
        assert model.version == "3"
        assert model.description == "this is my test model"

        models = client.models.list(name=model_name)
        assert isinstance(models, ItemPaged)
        test_model = next(iter(models), None)
        assert isinstance(test_model, Model)

        # client.models.delete(name=model.name, version="3")
        # with pytest.raises(Exception):
        #     client.models.get(name=model.name, version="3")

    def test_crud_model_with_stage(self, client: MLClient, randstr: Callable[[], str], tmp_path: Path) -> None:
        path = Path("./tests/test_configs/model/model_with_stage.yml")
        model_name = randstr("model_prod_name")

        model = load_model(path)
        model.name = model_name
        model = client.models.create_or_update(model)
        assert model.name == model_name
        assert model.version == "3"
        assert model.description == "this is my test model with stage"
        assert model.type == "mlflow_model"
        assert model.stage == "Production"
        assert re.match(LONG_URI_REGEX_FORMAT, model.path)

        with pytest.raises(Exception):
            with patch("azure.ai.ml._artifacts._artifact_utilities.get_object_hash", return_value="DIFFERENT_HASH"):
                model = load_model(source=artifact_path)
                model = client.models.create_or_update(model)

        model = client.models.get(model.name, "3")
        assert model.name == model_name
        assert model.version == "3"
        assert model.description == "this is my test model with stage"
        assert model.stage == "Production"

        model_list = client.models.list(name=model.name, stage="Production")
        model_stage_list = [m.stage for m in model_list if m is not None]
        assert model.stage in model_stage_list

    def test_list_no_name(self, client: MLClient) -> None:
        models = client.models.list()
        assert isinstance(models, Iterator)
        test_model = next(iter(models), None)
        assert isinstance(test_model, Model)

    def test_models_get_latest_label(self, client: MLClient, randstr: Callable[[], str], tmp_path: Path) -> None:
        name = f"model_{randstr('name')}"
        versions = ["1", "2", "3", "4"]
        model_path = tmp_path / "model.pkl"
        model_path.write_text("hello world")
        for version in versions:
            client.models.create_or_update(Model(name=name, version=version, path=str(model_path)))
            assert client.models.get(name, label="latest").version == version

    def test_model_archive_restore_version(self, client: MLClient, randstr: Callable[[], str], tmp_path: Path) -> None:
        name = f"model_{randstr('name')}"
        versions = ["1", "2"]
        version_archived = versions[0]
        model_path = tmp_path / "model.pkl"
        model_path.write_text("hello world")
        for version in versions:
            client.models.create_or_update(Model(name=name, version=version, path=str(model_path)))

        def get_model_list():
            # Wait for list index to update before calling list command
            sleep_if_live(30)
            model_list = client.models.list(name=name, list_view_type=ListViewType.ACTIVE_ONLY)
            return [m.version for m in model_list if m is not None]

        assert version_archived in get_model_list()
        client.models.archive(name=name, version=version_archived)
        assert version_archived not in get_model_list()
        client.models.restore(name=name, version=version_archived)
        assert version_archived in get_model_list()

    @pytest.mark.skip(reason="Task 1791832: Inefficient, possibly causing testing pipeline to time out.")
    def test_model_archive_restore_container(
        self, client: MLClient, randstr: Callable[[], str], tmp_path: Path
    ) -> None:
        name = f"model_{randstr('name')}"
        version = "1"
        model_path = tmp_path / "model.pkl"
        model_path.write_text("hello world")
        client.models.create_or_update(Model(name=name, version=version, path=str(model_path)))

        def get_model_list():
            # Wait for list index to update before calling list command
            sleep_if_live(30)
            model_list = client.models.list(list_view_type=ListViewType.ACTIVE_ONLY)
            return [m.name for m in model_list if m is not None]

        assert name in get_model_list()
        client.models.archive(name=name)
        assert name not in get_model_list()
        client.models.restore(name=name)
        assert name in get_model_list()

    @pytest.mark.skipif(condition=not is_live(), reason="Registry uploads do not record well. Investigate later")
    def test_create_get_download_model_registry(self, registry_client: MLClient, randstr: Callable[[], str]) -> None:
        model_path = Path("./tests/test_configs/model/model_full.yml")
        model_name = randstr("model_name")
        model_version = "2"

        model_entity = load_model(model_path)
        model_entity.name = model_name
        model_entity.version = model_version
        model = registry_client.models.create_or_update(model_entity)
        assert model.name == model_name
        assert model.version == model_version
        assert model.description == "this is my test model"
        assert model.type == "mlflow_model"

        model_get = registry_client.models.get(name=model_name, version=model_version)
        assert model == model_get
        assert model_get.name == model_name
        assert model_get.version == model_version
        assert model_get.description == "this is my test model"
        assert model_get.type == "mlflow_model"

        registry_client.models.download(name=model_name, version=model_version, download_path="downloaded")
        wd = os.path.join(os.getcwd(), f"downloaded/{model_name}")
        assert os.path.exists(wd)
        assert os.path.exists(f"{wd}/lightgbm_mlflow_model/MLmodel")

    @pytest.mark.skipif(condition=not is_live(), reason="Registry uploads do not record well. Investigate later")
    def test_list_model_registry(self, registry_client: MLClient, randstr: Callable[[], str]) -> None:
        model_path = Path("./tests/test_configs/model/model_full.yml")
        model_name = randstr("model_name")
        model_version = "2"

        model_entity = load_model(model_path)
        model_entity.name = model_name
        model_entity.version = model_version
        model = registry_client.models.create_or_update(model_entity)
        assert model.name == model_name
        assert model.version == model_version
        assert model.description == "this is my test model"
        assert model.type == "mlflow_model"

        model_list = registry_client.models.list()
        model_list = [m.name for m in model_list if m is not None]
        assert model.name in model_list

    @pytest.mark.skip(reason="_prepare_to_copy method was removed")
    def test_promote_model(self, randstr: Callable[[], str], client: MLClient, registry_client: MLClient) -> None:
        # Create model in workspace
        model_path = Path("./tests/test_configs/model/model_full.yml")
        model_name = f"model_{randstr('name')}"
        model_version = "2"
        model_entity = load_model(model_path)
        model_entity.name = model_name
        model_entity.version = model_version
        client.models.create_or_update(model_entity)
        # Start promoting to registry
        # 1. Get registered model in workspace
        model_in_workspace = client.models.get(name=model_name, version=model_version)
        # 2. Prepare model to copy
        model_to_promote = client.models._prepare_to_copy(model_in_workspace)
        # 3. Copy model to registry
        model = registry_client.models.create_or_update(model_to_promote)
        model = model.result()
        # 4. Check that model has been promoted
        model = registry_client.models.get(name=model_name, version=model_version)
        assert model.name == model_name
        assert model.version == model_version
