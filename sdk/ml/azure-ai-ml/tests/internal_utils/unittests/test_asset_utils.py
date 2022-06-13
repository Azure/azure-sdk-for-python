import pytest
import os
from pathlib import Path
from typing import Callable

from azure.ai.ml._utils._asset_utils import (
    get_ignore_file,
    AmlIgnoreFile,
    GitIgnoreFile,
    get_object_hash,
    traverse_directory,
    IgnoreFile,
)


@pytest.fixture
def gitignore_file_directory() -> str:
    return "./tests/test_configs/storage/gitignore_only/"


@pytest.fixture
def storage_test_directory() -> str:
    return "./tests/test_configs/storage/"


@pytest.fixture
def no_ignore_file_directory() -> str:
    return "./tests/test_configs/storage/dont_include_us/"


@pytest.fixture
def amlignore_file(storage_test_directory: str) -> AmlIgnoreFile:
    return AmlIgnoreFile(storage_test_directory)


@pytest.fixture
def gitignore_file(storage_test_directory: str) -> GitIgnoreFile:
    return GitIgnoreFile(storage_test_directory)


@pytest.fixture
def no_ignore_file(no_ignore_file_directory: str) -> IgnoreFile:
    return IgnoreFile(None)


@pytest.mark.unittest
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

        for root, dirs, files in os.walk(source_path, followlinks=True):
            upload_paths += list(traverse_directory(root, files, source_path, prefix))

        for local_path, remote_path in upload_paths:
            remote_path = remote_path.split("/", 2)[-1]  # strip LocalUpload/<asset id> prefix
            if remote_path.startswith("link_file_"):  # ignore symlinks because their remote and local paths will differ
                continue
            assert remote_path in local_path

    def test_symlinks_included_in_hash(self, randstr: Callable[[], str], tmp_path: Path) -> None:
        """Confirm that changes in the original file are respected when the symlink is hashed"""

        # create target file
        target_file_name = tmp_path / f"target_file_{randstr()}.txt"
        target_file_name.write_text("some text")

        # create symlink
        link_file_name = tmp_path / f"link_file_{randstr()}.txt"
        os.symlink(target_file_name, link_file_name)
        assert os.path.islink(link_file_name)

        # hash symlink, update original file, hash symlink again and compare hashes
        original_hash = get_object_hash(path=link_file_name, ignore_file=no_ignore_file)
        target_file_name.write_text("some more text")
        updated_hash = get_object_hash(path=link_file_name, ignore_file=no_ignore_file)
        assert original_hash != updated_hash

    def test_symlink_upload_paths(self, randstr: Callable[[], str], storage_test_directory: str) -> None:
        """Confirm that symlink name is preserved for upload to storage, but that target file's path is uploaded

        e.g given a file ./dir/foo/bar.txt with a symlink ./other_dir/bar_link.txt, we want to upload the contents of ./dir/food/bar.txt at path ./other_dir/bar_link.txt in the remote storage.
        """
        source_path = Path(storage_test_directory).resolve()
        prefix = source_path.name + "/"
        upload_paths_list = []
        randstr = randstr()

        target_file_name = os.path.join(os.path.abspath(storage_test_directory), f"target_file_{randstr}.txt")
        link_file_name = os.path.join(os.path.abspath(storage_test_directory), f"link_file_{randstr}.txt")
        os.symlink(target_file_name, link_file_name)
        assert os.path.islink(link_file_name)

        for root, _, files in os.walk(source_path, followlinks=True):
            upload_paths_list += list(traverse_directory(root, files, source_path, prefix))

        local_paths = [i for i, _ in upload_paths_list]
        remote_paths = [j for _, j in upload_paths_list]

        assert target_file_name in local_paths
        assert f"storage/link_file_{randstr}.txt" in remote_paths  # remote file names are relative