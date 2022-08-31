import pytest
import hashlib
import os
import shutil
from pathlib import Path
from azure.ai.ml._utils._asset_utils import get_content_hash


@pytest.mark.unittest
class TestGetContentHash:
    def test_get_content_hash_should_not_change(self):
        root = Path.cwd().joinpath("code")
        content1 = b"test\n"
        content2 = b"file2 content\n"
        content3 = b"file3 content\n"
        content4 = b"file4 content\n"
        test_files = [
            ("file1.txt", content1),
            ("folder1/file2.txt", content2),
            ("Folder2/folder1/file4.txt", content4),
            ("Folder2/file3.txt", content3),
        ]
        for test_file in test_files:
            file_path = root.joinpath(test_file[0])
            os.makedirs(file_path.parent, exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(test_file[1])

        hash = get_content_hash(root)
        actual_hash = hashlib.sha256()
        actual_hash.update(b"4")
        actual_hash.update(b"#file1.txt#" + str(len(content1)).encode())
        actual_hash.update(b"#folder1/file2.txt#" + str(len(content2)).encode())
        actual_hash.update(b"#Folder2/file3.txt#" + str(len(content3)).encode())
        actual_hash.update(b"#Folder2/folder1/file4.txt#" + str(len(content4)).encode())
        actual_hash.update(content1)
        actual_hash.update(content2)
        actual_hash.update(content3)
        actual_hash.update(content4)
        assert actual_hash.hexdigest() == hash == "3f99429630ebd5882337eedef79dc029a9b406338cd6f466206aef2c951453be"
        shutil.rmtree(root)
