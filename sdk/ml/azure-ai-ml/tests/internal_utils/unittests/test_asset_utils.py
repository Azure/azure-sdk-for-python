import os
import shutil
import tempfile
from pathlib import Path
from typing import Callable, Tuple

import pytest

from azure.ai.ml._utils._asset_utils import (
    AmlIgnoreFile,
    GitIgnoreFile,
    IgnoreFile,
    get_ignore_file,
    get_object_hash,
    get_local_paths,
    construct_local_and_remote_paths,
)
from azure.ai.ml._utils.utils import convert_windows_path_to_unix


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
def no_ignore_file() -> IgnoreFile:
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

@pytest.fixture
def fake_remote_prefix() -> str:
    return "LocalUpload/1234"


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

        amlignore_upload_paths = []
        gitignore_upload_paths = []
        no_ignore_upload_paths = []

        amlignore_upload_paths, _ = get_local_paths(source_path, ignore_file=amlignore_file)
        gitignore_upload_paths, _ = get_local_paths(source_path, ignore_file=gitignore_file)
        no_ignore_upload_paths, _ = get_local_paths(source_path, ignore_file=no_ignore_file)

        assert len(no_ignore_upload_paths) == 7
        assert len(gitignore_upload_paths) == 6
        assert len(amlignore_upload_paths) == 4

    def test_upload_paths_match(self, storage_test_directory: str, fake_remote_prefix: str) -> None:
        source_path = Path(storage_test_directory).resolve()
        upload_paths = construct_local_and_remote_paths(source_path, dest=fake_remote_prefix)

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

    def test_symlink_upload_paths(self, storage_test_directory: str, fake_remote_prefix: str) -> None:
        """Confirm that symlink name is preserved for upload to storage, but that target file's path is uploaded

        e.g given a symlink "./other_dir/bar_link.txt" with target file "./dir/foo/bar.txt", we want to upload the
        contents of "./dir/food/bar.txt" at path "LocalUpload/<artifact hash>/other_dir/bar_link.txt" in the remote
        storage.
        """
        target_file_path, link_file_path = generate_link_file(storage_test_directory)
        upload_pairs = construct_local_and_remote_paths(storage_test_directory, dest=fake_remote_prefix)

        local_paths = [i for i, _ in upload_pairs]
        remote_paths = [j for _, j in upload_pairs]
        
        # When username is too long, temp folder path will be truncated, e.g. longusername -> LONGUS~ so resolve 
        # target_file_path to get the full path
        assert Path(target_file_path).resolve().as_posix() in local_paths
        # remote file names are relative so only what's after the prefix should match
        assert any([rp.replace(fake_remote_prefix, "")  in link_file_path for rp in remote_paths])
