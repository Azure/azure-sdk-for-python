import json
import os
from pathlib import Path
from typing import Dict

import pytest

from azure.ai.ml._utils._data_utils import download_mltable_metadata_schema, validate_mltable_metadata
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants._common import MLTABLE_METADATA_SCHEMA_URL_FALLBACK
from azure.ai.ml.exceptions import ValidationException


@pytest.fixture
def mltable_schema():
    with open(Path(os.path.dirname(__file__), "../../../../../", "extension/schema/MLTable.schema.json"), "r") as f:
        return json.load(f)


@pytest.mark.unittest
@pytest.mark.skip(reason="extension folder does not exist in GitHub")
class TestDataUtils:
    def test_validate_mltable_metadata_schema(self, tmp_path: Path, mltable_schema: Dict):
        mltable_folder = tmp_path / "mltable_folder"
        mltable_folder.mkdir()
        tmp_metadata_file = mltable_folder / "MLTable"

        file_contents = """
            paths:
                - file: ./tmp_file.csv
            transformations:
                - read_delimited:
                    delimiter: ","
                    encoding: ascii
                    header: all_files_same_headers
        """
        tmp_metadata_file.write_text(file_contents)
        valid_metadata_dict = load_yaml(tmp_metadata_file)
        validate_mltable_metadata(mltable_metadata_dict=valid_metadata_dict, mltable_schema=mltable_schema)
        # no errors raised

        file_contents = """
            transformations:
                - read_delimited:
                    delimiter: ","
                    encoding: ascii
                    header: all_files_same_headers
        """
        tmp_metadata_file.write_text(file_contents)
        missing_paths_dict = load_yaml(tmp_metadata_file)
        with pytest.raises(ValidationException) as ex:
            validate_mltable_metadata(mltable_metadata_dict=missing_paths_dict, mltable_schema=mltable_schema)
        assert "'paths' is a required property" in ex.value.message

        file_contents = """
            paths:
                - file: ./tmp_file.csv
            transformations:
                - read_delimited:
                    delimiter: ","
                    encoding: unknownencoding
                    header: all_files_same_headers
        """
        tmp_metadata_file.write_text(file_contents)
        invalid_encoding_dict = load_yaml(tmp_metadata_file)
        with pytest.raises(ValidationException) as ex:
            validate_mltable_metadata(mltable_metadata_dict=invalid_encoding_dict, mltable_schema=mltable_schema)
        assert "unknownencoding" in ex.value.message
