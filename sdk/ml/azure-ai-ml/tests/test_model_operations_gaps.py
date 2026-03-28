from pathlib import Path
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient
from azure.ai.ml.entities._assets import Model
from azure.ai.ml.exceptions import ValidationException


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestModelOperationsGaps(AzureRecordedTestCase):
    def test_create_or_update_rejects_evaluator_when_using_models_ops(
        self, client: MLClient, randstr: Callable[[], str], tmp_path: Path
    ) -> None:
        # Attempting to create a model that is marked as an evaluator using ModelOperations should raise ValidationException
        name = f"model_{randstr('name')}"
        # create a dummy artifact file for the model path
        model_path = tmp_path / "model.pkl"
        model_path.write_text("hello world")

        # First, creating a normal model should succeed
        normal = Model(name=name, version="1", path=str(model_path))
        created = client.models.create_or_update(normal)
        assert created.name == name
        assert created.version == "1"

        # Now attempt to create a model with evaluator properties set; should raise because previous version is regular
        evaluator_model = Model(name=name, version="2", path=str(model_path))
        # _is_evaluator() checks for both "is-evaluator" == "true" and "is-promptflow" == "true"
        evaluator_model.properties = {"is-evaluator": "true", "is-promptflow": "true"}

        with pytest.raises(ValidationException):
            client.models.create_or_update(evaluator_model)

    def test_create_or_update_evaluator_rejected_when_no_existing_model(
        self, client: MLClient, randstr: Callable[[], str], tmp_path: Path
    ) -> None:
        # Creating an evaluator via ModelOperations should be rejected even if no existing model exists
        name = f"model_{randstr('eval')}_noexist"
        model_path = tmp_path / "model2.pkl"
        model_path.write_text("hello world")

        evaluator_only = Model(name=name, version="1", path=str(model_path))
        # _is_evaluator() checks for both "is-evaluator" == "true" and "is-promptflow" == "true"
        evaluator_only.properties = {"is-evaluator": "true", "is-promptflow": "true"}

        with pytest.raises(ValidationException):
            client.models.create_or_update(evaluator_only)
