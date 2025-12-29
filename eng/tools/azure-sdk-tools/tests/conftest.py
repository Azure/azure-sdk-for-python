import pytest
import tempfile
import os

from typing import List
from tempfile import TemporaryDirectory


@pytest.fixture()
def tmp_directory_create():
    with TemporaryDirectory() as tmp_dir:

        def create_temp_directory(fake_creation_paths: List[str]) -> TemporaryDirectory:
            for file in fake_creation_paths:
                target_path = os.path.join(tmp_dir, file)
                dirname = os.path.join(tmp_dir, os.path.dirname(file))

                if not os.path.exists(dirname):
                    os.mkdir(dirname)

                with open(target_path, "w"):
                    pass
            return tmp_dir

        yield create_temp_directory
