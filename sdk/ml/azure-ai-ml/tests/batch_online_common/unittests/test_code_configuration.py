import pytest
import yaml

from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY
from marshmallow import RAISE
from azure.ai.ml.entities import CodeConfiguration


@pytest.mark.unittest
class TestCodeConfiguration:
    def test_scoring_script_missing_throw(self) -> None:
        missing_code_configuration = CodeConfiguration(code="xx", scoring_script=None)
        with pytest.raises(Exception):
            missing_code_configuration._validate()

    def test_schema_validation_pass(self) -> None:
        complete_scoring_script = CodeConfiguration(code="xx", scoring_script="xxx")
        complete_scoring_script._validate()
