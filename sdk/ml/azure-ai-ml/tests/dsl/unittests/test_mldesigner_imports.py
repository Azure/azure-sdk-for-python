import pytest


@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestMldesignerImports:
    def test_mldesigner_imports(self):
        from azure.ai.ml.dsl._mldesigner import Input
        assert Input