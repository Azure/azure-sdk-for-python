import os
import shutil
import tempfile
from pathlib import Path
from typing import Tuple

import pytest

from azure.ai.ml._utils._asset_utils import (
    AmlIgnoreFile,
    GitIgnoreFile,
    IgnoreFile,
    get_ignore_file,
    get_object_hash,
    get_directory_size,
    traverse_directory,
    _check_or_modify_auto_delete_setting,
    _validate_auto_delete_setting_in_data_output,
    _validate_workspace_managed_datastore,
)
from azure.ai.ml._utils.utils import convert_windows_path_to_unix
from azure.ai.ml.exceptions import (
    AssetPathException,
    ValidationException,
)
from azure.ai.ml.constants._common import AutoDeleteCondition
from azure.ai.ml.entities._assets.auto_delete_setting import AutoDeleteSetting


@pytest.fixture
def storage_test_directory() -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        shutil.rmtree(temp_dir)
        shutil.copytree("./tests/test_configs/storage/", temp_dir)
        yield temp_dir


@pytest.fixture
def gitignore_file_directory(storage_test_directory: str) -> str:
    return os.path.join(storage_test_directory, "gitignore_only")


@pytest.fixture
def no_ignore_file_directory(storage_test_directory: str) -> str:
    return os.path.join(storage_test_directory, "dont_include_us")


@pytest.fixture
def amlignore_file(storage_test_directory: str) -> AmlIgnoreFile:
    return AmlIgnoreFile(storage_test_directory)


@pytest.fixture
def gitignore_file(storage_test_directory: str) -> GitIgnoreFile:
    return GitIgnoreFile(storage_test_directory)


@pytest.fixture
def no_ignore_file(no_ignore_file_directory: str) -> IgnoreFile:
    return IgnoreFile(None)


def generate_link_file(base_dir: str) -> Tuple[os.PathLike, os.PathLike]:
    target_file_name = "target_file_rand_name.txt"
    target_file = Path(os.path.join(os.path.abspath(base_dir), target_file_name))
    target_file.write_text("some text")

    link_file_name = "link_file_rand_name.txt"
    link_file = Path(os.path.join(os.path.abspath(base_dir), link_file_name))

    os.symlink(target_file, link_file)

    assert os.path.islink(link_file)
    return convert_windows_path_to_unix(target_file), convert_windows_path_to_unix(link_file)


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestAssetUtils:
    def test_amlignore_precedence(
        self, storage_test_directory: str, gitignore_file_directory: str, no_ignore_file_directory: str
    ) -> None:
        amlignore_file = get_ignore_file(directory_path=storage_test_directory)
        assert isinstance(amlignore_file, AmlIgnoreFile)

        gitignore_file = get_ignore_file(directory_path=gitignore_file_directory)
        assert isinstance(gitignore_file, GitIgnoreFile)

        no_ignore_file = get_ignore_file(directory_path=no_ignore_file_directory)
        assert isinstance(no_ignore_file, IgnoreFile)
        assert no_ignore_file.path is None

    def test_hashing(
        self,
        storage_test_directory: str,
        amlignore_file: AmlIgnoreFile,
        gitignore_file: GitIgnoreFile,
        no_ignore_file: IgnoreFile,
    ) -> None:
        no_ignore_hash = get_object_hash(path=storage_test_directory, ignore_file=no_ignore_file)
        amlignore_hash = get_object_hash(path=storage_test_directory, ignore_file=amlignore_file)
        gitignore_hash = get_object_hash(path=storage_test_directory, ignore_file=gitignore_file)

        assert no_ignore_hash != amlignore_hash != gitignore_hash

    def test_exclude(
        self,
        storage_test_directory: str,
        amlignore_file: AmlIgnoreFile,
        gitignore_file: GitIgnoreFile,
        no_ignore_file: IgnoreFile,
    ) -> None:
        source_path = Path(storage_test_directory).resolve()
        prefix = source_path.name + "/"

        amlignore_upload_paths = []
        gitignore_upload_paths = []
        no_ignore_upload_paths = []

        for root, _, files in os.walk(source_path, followlinks=True):
            amlignore_upload_paths += list(
                traverse_directory(root, files, source_path, prefix, ignore_file=amlignore_file)
            )
            gitignore_upload_paths += list(
                traverse_directory(root, files, source_path, prefix, ignore_file=gitignore_file)
            )
            no_ignore_upload_paths += list(
                traverse_directory(root, files, source_path, prefix, ignore_file=no_ignore_file)
            )

        assert len(no_ignore_upload_paths) == 7
        assert len(gitignore_upload_paths) == 6
        assert len(amlignore_upload_paths) == 4

    def test_upload_paths_match(self, storage_test_directory: str) -> None:
        source_path = Path(storage_test_directory).resolve()
        prefix = source_path.name + "/"
        upload_paths = []

        for root, _, files in os.walk(source_path, followlinks=True):
            upload_paths += list(traverse_directory(root, files, source_path, prefix))

        for local_path, remote_path in upload_paths:
            remote_path = remote_path.split("/", 2)[-1]  # strip LocalUpload/<asset id> prefix
            if remote_path.startswith("link_file_"):  # ignore symlinks because their remote and local paths will differ
                continue
            assert remote_path in local_path

    def test_symlinks_included_in_hash(self, storage_test_directory: str) -> None:
        """Confirm that changes in the original file are respected when the symlink is hashed"""
        target_file_path, link_file_path = generate_link_file(storage_test_directory)

        # hash symlink, update original file, hash symlink again and compare hashes
        original_hash = get_object_hash(path=link_file_path, ignore_file=no_ignore_file)
        Path(target_file_path).write_text("some more text")
        updated_hash = get_object_hash(path=link_file_path, ignore_file=no_ignore_file)
        assert original_hash != updated_hash

    def test_symlink_upload_paths(self, storage_test_directory: str) -> None:
        """Confirm that symlink name is preserved for upload to storage, but that target file's path is uploaded

        e.g given a file ./dir/foo/bar.txt with a symlink ./other_dir/bar_link.txt, we want to upload the contents of ./dir/food/bar.txt at path ./other_dir/bar_link.txt in the remote storage.
        """
        target_file_path, link_file_path = generate_link_file(storage_test_directory)

        source_path = Path(storage_test_directory).resolve()
        prefix = "random_prefix/"
        upload_paths_list = []

        for root, _, files in os.walk(source_path, followlinks=True):
            upload_paths_list += list(traverse_directory(root, files, source_path, prefix))

        local_paths = [i for i, _ in upload_paths_list]
        remote_paths = [j for _, j in upload_paths_list]

        # When username is too long, temp folder path will be truncated, e.g. longusername -> LONGUS~
        # so resolve target_file_path to get the full path
        assert Path(target_file_path).resolve().as_posix() in local_paths
        # remote file names are relative to root and include the prefix
        assert prefix + Path(link_file_path).relative_to(storage_test_directory).as_posix() in remote_paths

    def test_directory_size_with_ignore_file(self, storage_test_directory: str, amlignore_file: AmlIgnoreFile) -> None:
        base_size = get_directory_size(storage_test_directory)
        with_ignore_size = get_directory_size(storage_test_directory, ignore_file=amlignore_file)

        # Note, the [1] index is the number of files counted in the directory size calculation.
        # The [0] index is the sum file size, which we don't check here due to how instable that
        # value is across systems/builds.
        # Directory size calculated with ignore file should include less files
        assert len(with_ignore_size[1]) < len(base_size[1])

        # Directory size calculated after symlink creation should correctly include linked file size,
        # and count symlink file itself towards file count.
        _, _ = generate_link_file(storage_test_directory)
        with_symlink_size = get_directory_size(storage_test_directory)
        assert len(with_symlink_size[1]) == len(base_size[1]) + 2

    def test_check_or_modify_auto_delete_setting(self):
        _check_or_modify_auto_delete_setting(None)

        setting = {"condition": "created_greater_than"}
        _check_or_modify_auto_delete_setting(setting)
        assert setting["condition"] == "createdGreaterThan"

        setting = AutoDeleteSetting(condition=AutoDeleteCondition.CREATED_GREATER_THAN)
        _check_or_modify_auto_delete_setting(setting)
        assert setting.condition == "createdGreaterThan"

    def test_validate_auto_delete_setting_in_data_output(self):
        with pytest.raises(ValidationException):
            _validate_auto_delete_setting_in_data_output({"value": "30d"})

        _validate_auto_delete_setting_in_data_output(None)
        _validate_auto_delete_setting_in_data_output({})

    def test_validate_workspace_managed_datastore(self):
        with pytest.raises(AssetPathException):
            _validate_workspace_managed_datastore("azureml://datastores/workspacemanageddatastore/123")

        path = _validate_workspace_managed_datastore("azureml://datastores/workspacemanageddatastore")
        assert path == "azureml://datastores/workspacemanageddatastore/paths"

        path = _validate_workspace_managed_datastore("azureml://datastores/workspacemanageddatastore/")
        assert path == "azureml://datastores/workspacemanageddatastore/paths"

        path = _validate_workspace_managed_datastore("azureml://datastores/workspacemanageddatastore123")
        assert path == "azureml://datastores/workspacemanageddatastore123"
