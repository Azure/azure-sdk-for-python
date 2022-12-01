from pathlib import Path

import pytest

from azure.ai.ml._file_utils.file_utils import traverse_up_path_and_find_file


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestFileUtils:
    def test_traverse_up_path_and_find_file_multi_layers(self, tmp_path: Path):
        filename = "hello.txt"
        root = tmp_path
        filepath = root / filename
        filepath.write_text("content")

        start = root
        for i in range(10):
            start = start / f"sub{i}"
            start.mkdir()

        a = traverse_up_path_and_find_file(start, filename)
        assert a == str(filepath)

    def test_traverse_up_path_and_find_file(self, tmpdir):
        path = tmpdir.mkdir("sub")
        p = path.join("sub2")
        file_path = path.join("file.txt")
        file_path.write("content")
        ret = traverse_up_path_and_find_file(p, "file.txt")
        assert ret == file_path

    def test_traverse_up_path_and_find_file_with_dir_name(self, tmp_path: Path):
        filename = "hello.txt"
        root = tmp_path
        filepath = root / ".azure"
        filepath.mkdir()
        filepath = filepath / filename
        filepath.write_text("content")

        start = root
        for i in range(10):
            start = start / f"sub{i}"
            start.mkdir()

        a = traverse_up_path_and_find_file(start, filename, ".azure")
        assert a == str(filepath)
