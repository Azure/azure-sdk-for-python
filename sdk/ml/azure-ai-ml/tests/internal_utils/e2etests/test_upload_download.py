import os
import tempfile
import time
import uuid
from pathlib import Path, PurePath
from typing import Tuple

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import sleep_if_live

from azure.ai.ml import MLClient
from azure.ai.ml._artifacts._artifact_utilities import _update_metadata
from azure.ai.ml._artifacts._blob_storage_helper import BlobStorageClient
from azure.ai.ml._artifacts._fileshare_storage_helper import FileStorageClient
from azure.ai.ml._artifacts._gen2_storage_helper import Gen2StorageClient
from azure.ai.ml._restclient.v2022_10_01.models import DatastoreType
from azure.ai.ml._utils._asset_utils import _parse_name_version, get_object_hash
from azure.ai.ml._utils._storage_utils import get_storage_client
from azure.ai.ml.entities import Model
from azure.ai.ml.entities._credentials import NoneCredentialConfiguration

container_name = "testblob"
file_share_name = "testfileshare"
file_system_name = "testfilesystem"


@pytest.fixture
def blob_account_url(storage_account_name: str) -> str:
    return f"https://{storage_account_name}.blob.core.windows.net"


@pytest.fixture
def gen2_account_url(storage_account_name: str) -> str:
    return f"https://{storage_account_name}.dfs.core.windows.net"


@pytest.fixture
def storage_account_secret(account_keys: Tuple[str, str]) -> str:
    return account_keys[0]


file_path = Path("sub_dir/test.txt")
TEST_ARTIFACT_FILE = "artifact_file.txt"
TEST_ARTIFACT_DIR = "artifact_testing_dir"


@pytest.fixture(scope="session")
def upload_dir(tmp_path_factory):
    """Fixture that sets up a directory with a file that is uploaded by
    other tests

    Returns:
        Path: Path to the base of the directory
    """
    base = tmp_path_factory.mktemp("test_dir")
    actual_file_path = base / file_path
    actual_file_path.parent.mkdir(parents=True, exist_ok=True)
    with actual_file_path.open("w") as f:
        f.write("content")

    return base


@pytest.fixture
def uuid_name(variable_recorder) -> str:
    return variable_recorder.get_or_record("uuid_name", str(uuid.uuid1()) + ":1")


@pytest.fixture
def dir_asset_id(variable_recorder) -> str:
    return variable_recorder.get_or_record("dir_asset_id", str(uuid.uuid4()))


@pytest.fixture
def file_asset_id(variable_recorder) -> str:
    return variable_recorder.get_or_record("file_asset_id", str(uuid.uuid4()))


@pytest.fixture
def artifact_path(tmpdir_factory, variable_recorder) -> str:  # type: ignore
    file_name = tmpdir_factory.mktemp("artifact_testing").join(TEST_ARTIFACT_FILE)
    file_content = variable_recorder.get_or_record("file_content", str(uuid.uuid4()))
    file_name.write(file_content)
    return str(file_name)


@pytest.fixture
def artifact_path_dir(tmpdir_factory, variable_recorder) -> str:  # type: ignore
    file_name = tmpdir_factory.mktemp(TEST_ARTIFACT_DIR).join(TEST_ARTIFACT_FILE)
    file_content = variable_recorder.get_or_record("file_content", str(uuid.uuid4()))
    file_name.write(file_content)
    return str(file_name.dirpath())


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.skipif(condition=not is_live(), reason="test are flaky in playback")
@pytest.mark.core_sdk_test
class TestUpload(AzureRecordedTestCase):
    def test_upload_file_blob(
        self,
        storage_account_name: str,
        storage_account_secret: str,
        dir_asset_id: str,
        file_asset_id: str,
        upload_dir: Path,
    ) -> None:
        blob_storage_client: BlobStorageClient = get_storage_client(
            credential=storage_account_secret,
            container_name=container_name,
            storage_account=storage_account_name,
            storage_type=DatastoreType.AZURE_BLOB,
        )
        assert isinstance(blob_storage_client, BlobStorageClient)
        _ = blob_storage_client.upload(
            str(upload_dir / file_path), show_progress=False, asset_hash=file_asset_id, name="name", version="version"
        )
        _ = blob_storage_client.upload(
            str(upload_dir), show_progress=False, asset_hash=dir_asset_id, name="name", version="version"
        )

        _ = blob_storage_client.upload(
            str(upload_dir / file_path), show_progress=False, asset_hash=file_asset_id, name="name", version="version"
        )
        _ = blob_storage_client.upload(
            str(upload_dir), show_progress=False, asset_hash=dir_asset_id, name="name", version="version"
        )

    def test_upload_file_gen2(
        self,
        storage_account_name: str,
        storage_account_secret: str,
        dir_asset_id: str,
        file_asset_id: str,
        upload_dir: Path,
    ) -> None:
        adlsgen2_storage_client = get_storage_client(
            credential=storage_account_secret,
            container_name=container_name,
            storage_account=storage_account_name,
            storage_type=DatastoreType.AZURE_DATA_LAKE_GEN2,
        )
        assert isinstance(adlsgen2_storage_client, Gen2StorageClient)
        _ = adlsgen2_storage_client.upload(
            str(upload_dir / file_path), show_progress=False, asset_hash=file_asset_id, name="name", version="version"
        )
        _ = adlsgen2_storage_client.upload(
            str(upload_dir), show_progress=False, asset_hash=dir_asset_id, name="name", version="version"
        )

    @pytest.mark.skip("File datastores aren't supported by service, so disabling these tests until they're relevant")
    def test_upload_file_fileshare(
        self,
        storage_account_name: str,
        storage_account_secret: str,
        dir_asset_id: str,
        file_asset_id: str,
        upload_dir: Path,
    ) -> None:
        file_storage_client = get_storage_client(
            credential=storage_account_secret,
            container_name=file_share_name,
            storage_account=storage_account_name,
            storage_type=DatastoreType.AZURE_FILE,
        )
        assert isinstance(file_storage_client, FileStorageClient)

        file_asset_id1 = file_storage_client.upload(
            str(upload_dir / file_path), show_progress=False, asset_hash=file_asset_id, name="name", version="version"
        )
        file_asset_id2 = file_storage_client.upload(
            str(upload_dir / file_path), show_progress=False, asset_hash=file_asset_id, name="name", version="version"
        )
        assert file_asset_id1 == file_asset_id2

        dir_asset_id1 = file_storage_client.upload(
            str(upload_dir), show_progress=False, asset_hash=dir_asset_id, name="name", version="version"
        )
        dir_asset_id2 = file_storage_client.upload(
            str(upload_dir), show_progress=False, asset_hash=dir_asset_id, name="name", version="version"
        )
        assert dir_asset_id1 == dir_asset_id2

    def test_artifact_blob_file_upload(
        self,
        storage_account_name: str,
        storage_account_secret: str,
        artifact_path: str,
        uuid_name: str,
        variable_recorder,
    ) -> None:
        name, version = _parse_name_version(uuid_name)
        file_hash = variable_recorder.get_or_record("file_hash", get_object_hash(artifact_path))

        blob_storage_client = get_storage_client(
            credential=storage_account_secret,
            container_name=container_name,
            storage_account=storage_account_name,
            storage_type=DatastoreType.AZURE_BLOB,
        )
        _ = blob_storage_client.upload(
            artifact_path,
            show_progress=False,
            asset_hash=file_hash,
            name=name,
            version=str(version),
        )
        artifact_info = blob_storage_client.upload(
            artifact_path, show_progress=False, asset_hash=file_hash, name="name", version="version"
        )

        assert (name, str(version)) == (artifact_info["name"], artifact_info["version"])

    @pytest.mark.skip(reason="test timing out")
    def test_artifact_blob_dir_upload_and_download(
        self,
        storage_account_name: str,
        storage_account_secret: str,
        artifact_path_dir: str,
        uuid_name: str,
        variable_recorder,
    ) -> None:
        name, version = _parse_name_version(uuid_name)
        dir_hash = variable_recorder.get_or_record("dir_hash", get_object_hash(artifact_path_dir))

        blob_storage_client = get_storage_client(
            credential=storage_account_secret,
            container_name=container_name,
            storage_account=storage_account_name,
            storage_type=DatastoreType.AZURE_BLOB,
        )
        upload_info = blob_storage_client.upload(
            artifact_path_dir,
            show_progress=False,
            asset_hash=dir_hash,
            name=name,
            version=str(version),
        )
        artifact_info = blob_storage_client.upload(
            artifact_path_dir, show_progress=False, asset_hash=dir_hash, name="name", version="version"
        )
        assert (name, str(version)) == (artifact_info["name"], artifact_info["version"])

        temp_dir = Path(tempfile.gettempdir(), name)
        temp_dir.mkdir(parents=True, exist_ok=True)
        with temp_dir as td:
            blob_storage_client.download(starts_with=upload_info["indicator file"], destination=td)
            assert TEST_ARTIFACT_FILE in os.listdir(td)

    @pytest.mark.skip(reason="test timing out")
    def test_artifact_gen2_dir_upload_download(
        self,
        storage_account_name: str,
        storage_account_secret: str,
        uuid_name: str,
        variable_recorder,
    ) -> None:
        # creating nested directory with files here (using a fixture causes issues and directory is limited to this test)
        top_level = tempfile.TemporaryDirectory()
        nested_level = tempfile.TemporaryDirectory(dir=top_level.name)

        file1_name = PurePath(top_level.name).joinpath(TEST_ARTIFACT_FILE)
        with open(file1_name, "w") as f:
            f.write(str(uuid.uuid4()))
        file2_name = PurePath(nested_level.name).joinpath(TEST_ARTIFACT_FILE)
        with open(file2_name, "w") as f:
            f.write(str(uuid.uuid4()))

        artifact_path_dir, nested_dir_name = top_level.name, nested_level.name

        name, version = _parse_name_version(uuid_name)
        dir_hash = variable_recorder.get_or_record("dir_hash", get_object_hash(artifact_path_dir))

        gen2_storage_client = get_storage_client(
            credential=storage_account_secret,
            container_name=container_name,
            storage_account=storage_account_name,
            storage_type=DatastoreType.AZURE_DATA_LAKE_GEN2,
        )
        upload_info = gen2_storage_client.upload(
            artifact_path_dir,
            show_progress=False,
            asset_hash=dir_hash,
            name=name,
            version=str(version),
        )
        artifact_info = gen2_storage_client.upload(
            artifact_path_dir, show_progress=False, asset_hash=dir_hash, name="name", version="version"
        )

        assert (name, str(version)) == (artifact_info["name"], artifact_info["version"])

        temp_dir = Path(tempfile.gettempdir(), name)
        temp_dir.mkdir(parents=True, exist_ok=True)
        with temp_dir as td:
            gen2_storage_client.download(starts_with=upload_info["indicator file"], destination=td)
            dir_name = artifact_path_dir.split("/")[-1]
            assert TEST_ARTIFACT_FILE in os.listdir(("/".join([str(td), dir_name])))
            assert dir_name in os.listdir(td)
            assert nested_dir_name.split("/")[-1] in os.listdir(dir_name)  # ensure nested directory was created

    @pytest.mark.skip("File datastores aren't supported by service, so disabling these tests until they're relevant")
    def test_artifact_fileshare_file_upload(
        self,
        storage_account_name: str,
        storage_account_secret: str,
        artifact_path: str,
        uuid_name: str,
        variable_recorder,
    ) -> None:
        name, version = _parse_name_version(uuid_name)
        file_hash = variable_recorder.get_or_record("file_hash", get_object_hash(artifact_path))

        file_storage_client = get_storage_client(
            credential=storage_account_secret,
            container_name=file_share_name,
            storage_account=storage_account_name,
            storage_type=DatastoreType.AZURE_FILE,
        )
        _ = file_storage_client.upload(
            artifact_path,
            show_progress=False,
            asset_hash=file_hash,
            name=name,
            version=str(version),
        )
        artifact_info = file_storage_client.upload(
            artifact_path, show_progress=False, asset_hash=file_hash, name="name", version="version"
        )

        assert (name, str(version)) == (artifact_info["name"], artifact_info["version"])

    @pytest.mark.skip("File datastores aren't supported by service, so disabling these tests until they're relevant")
    def test_arm_id_fileshare_dir_upload(
        self,
        storage_account_name: str,
        storage_account_secret: str,
        artifact_path_dir: str,
        uuid_name: str,
        variable_recorder,
    ) -> None:
        name, version = _parse_name_version(uuid_name)
        dir_hash = variable_recorder.get_or_record("dir_hash", get_object_hash(artifact_path_dir))

        file_storage_client = get_storage_client(
            credential=storage_account_secret,
            container_name=file_share_name,
            storage_account=storage_account_name,
            storage_type=DatastoreType.AZURE_FILE,
        )
        _ = file_storage_client.upload(
            artifact_path_dir,
            show_progress=False,
            asset_hash=dir_hash,
            name=name,
            version=str(version),
        )
        artifact_info = file_storage_client.upload(
            artifact_path_dir, show_progress=False, asset_hash=dir_hash, name="name", version="version"
        )

        assert (name, str(version)) == (artifact_info["name"], artifact_info["version"])

    def test_update_blob_metadata(
        self,
        storage_account_name: str,
        storage_account_secret: str,
        dir_asset_id: str,
        file_asset_id: str,
        blob_account_url: str,
        upload_dir: Path,
    ) -> None:
        blob_storage_client = get_storage_client(
            credential=storage_account_secret,
            container_name=container_name,
            storage_account=storage_account_name,
            storage_type=DatastoreType.AZURE_BLOB,
        )
        assert isinstance(blob_storage_client, BlobStorageClient)
        datastore_info = {
            "storage_type": DatastoreType.AZURE_BLOB,
            "storage_account": storage_account_name,
            "container_name": blob_storage_client.container,
            "credential": storage_account_secret,
            "account_url": blob_account_url,
        }
        UPDATED_VERSION = "version from mfe"

        # upload artifact w/o version
        uploaded_file_info = blob_storage_client.upload(
            str(upload_dir / file_path), show_progress=False, asset_hash=file_asset_id, name="name", version=None
        )
        # update artifact blob metadata with new version
        _update_metadata(
            name=uploaded_file_info["name"],
            version=UPDATED_VERSION,
            indicator_file=uploaded_file_info["indicator file"],
            datastore_info=datastore_info,
        )
        # confirm metadata matches new version
        client = blob_storage_client.container_client.get_blob_client(uploaded_file_info["indicator file"])
        metadata = client.get_blob_properties().get("metadata")
        assert metadata.get("version") == UPDATED_VERSION

        # upload artifact w/o version
        uploaded_dir_info = blob_storage_client.upload(
            str(upload_dir), show_progress=False, asset_hash=dir_asset_id, name="name", version=None
        )
        # update artifact blob metadata with new version
        _update_metadata(
            name=uploaded_dir_info["name"],
            version=UPDATED_VERSION,
            indicator_file=uploaded_dir_info["indicator file"],
            datastore_info=datastore_info,
        )
        # confirm metadata matches new version
        client = blob_storage_client.container_client.get_blob_client(uploaded_dir_info["indicator file"])
        metadata = client.get_blob_properties().get("metadata")
        assert metadata.get("version") == UPDATED_VERSION

    def test_update_gen2_metadata(
        self,
        storage_account_name: str,
        storage_account_secret: str,
        dir_asset_id: str,
        file_asset_id: str,
        gen2_account_url: str,
        upload_dir: Path,
    ) -> None:
        gen2_storage_client = get_storage_client(
            credential=storage_account_secret,
            container_name=container_name,
            storage_account=storage_account_name,
            storage_type=DatastoreType.AZURE_DATA_LAKE_GEN2,
        )
        assert isinstance(gen2_storage_client, Gen2StorageClient)
        datastore_info = {
            "storage_type": DatastoreType.AZURE_DATA_LAKE_GEN2,
            "storage_account": storage_account_name,
            "container_name": gen2_storage_client.file_system,
            "credential": storage_account_secret,
            "account_url": gen2_account_url,
        }
        UPDATED_VERSION = "version from mfe"

        # upload artifact w/o version
        uploaded_file_info = gen2_storage_client.upload(
            str(upload_dir / file_path), show_progress=False, asset_hash=file_asset_id, name="name", version=None
        )
        # update artifact blob metadata with new version
        _update_metadata(
            name=uploaded_file_info["name"],
            version=UPDATED_VERSION,
            indicator_file=uploaded_file_info["indicator file"],
            datastore_info=datastore_info,
        )
        # confirm metadata matches new version
        client = gen2_storage_client.file_system_client.get_directory_client(uploaded_file_info["indicator file"])
        metadata = client.get_directory_properties().metadata
        assert metadata.get("version") == UPDATED_VERSION

        # upload artifact w/o version
        uploaded_dir_info = gen2_storage_client.upload(
            str(upload_dir), show_progress=False, asset_hash=dir_asset_id, name="name", version=None
        )
        # update artifact blob metadata with new version
        _update_metadata(
            name=uploaded_dir_info["name"],
            version=UPDATED_VERSION,
            indicator_file=uploaded_dir_info["indicator file"],
            datastore_info=datastore_info,
        )
        # confirm metadata matches new version
        client = gen2_storage_client.file_system_client.get_directory_client(uploaded_dir_info["indicator file"])
        metadata = client.get_directory_properties().metadata
        assert metadata.get("version") == UPDATED_VERSION

    @pytest.mark.skip(
        "Changes to assets to remove datastore param + inability to set default datastore makes this scenario impossible to be auto-tested currently."
    )
    def test_credentialless_datastore_upload_download(
        self,
        client: MLClient,
        credentialless_datastore: str,
        artifact_path: str,
    ):
        credentialless_ds = client.datastores.get(name=credentialless_datastore)
        assert isinstance(credentialless_ds.credentials, NoneCredentialConfiguration)

        test_model = Model(path=artifact_path)
        created_model = client.models.create_or_update(test_model)
        assert test_model.name == created_model.name
        sleep_if_live(5)  # wait for create/upload step

        client.models.download(name=created_model.name, version=created_model.version)
