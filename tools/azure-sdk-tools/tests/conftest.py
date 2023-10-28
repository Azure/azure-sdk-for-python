import pytest
import tempfile
import os

from typing import List
from tempfile import TemporaryDirectory

def create_temp_directory(fake_creation_paths: List[str]) -> TemporaryDirectory:
    tmp_dir = TemporaryDirectory()

    for file in fake_creation_paths:
        target_path = os.path.join(tmp_dir.name, file)
        dirname = os.path.join(tmp_dir.name, os.path.dirname(file))

        if not os.path.exists(dirname):
            os.mkdir(dirname)

        with open(target_path, "w"):
            pass

    return tmp_dir

@pytest.fixture()
def tmp_directory_create():
    return create_temp_directory
