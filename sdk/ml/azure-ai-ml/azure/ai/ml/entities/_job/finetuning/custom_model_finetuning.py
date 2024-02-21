from azure.ai.ml._restclient.v2024_01_01_preview.models import ModelProvider
from typing import Any
from azure.ai.ml.entities._job.finetuning.finetuning_job import FineTuningJob


class CustomModelFineTuningJob(FineTuningJob):
    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        # Extract any task specific settings
        model = kwargs.pop("model", None)
        task = kwargs.pop("task", None)
        training_data = kwargs.pop("training_data", None)
        validation_data = kwargs.pop("validation_data", None)
        hyperparameters = kwargs.pop("hyperparameters", None)
        super().__init__(
            task=task,
            model=model,
            model_provider=ModelProvider.AZURE_OPEN_AI,
            training_data=training_data,
            validation_data=validation_data,
            hyperparameters=hyperparameters,
            **kwargs,
        )
