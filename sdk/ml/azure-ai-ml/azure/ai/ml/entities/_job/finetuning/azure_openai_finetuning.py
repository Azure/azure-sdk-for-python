from azure.ai.ml._restclient.v2024_01_01_preview.models import ModelProvider, AzureOpenAiHyperParameters
from typing import Any, Optional
from azure.ai.ml.entities._job.finetuning.finetuning_job import FineTuningJob


class AzureOpenAIFineTuningJob(FineTuningJob):
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

    @property
    def hyperparameters(self) -> AzureOpenAiHyperParameters:
        """Get hyperparameters.

        :return:
        :rtype: AzureOpenAiHyperParameters
        """
        hyperparameters = AzureOpenAiHyperParameters()
        hyperparameters.batch_size = self._hyperparameters.get("batch_size", None)
        hyperparameters.learning_rate = self._hyperparameters.get("learning_rate_multiplier", None)
        hyperparameters.max_epochs = self._hyperparameters.get("n_epochs", None)
        return hyperparameters

    @hyperparameters.setter
    def hyperparameters(self, hyperparameters: AzureOpenAiHyperParameters) -> None:
        """Set hyperparameters.

        :param hyperparameters: Hyperparameters for finetuning the model.
        :type hyperparameters: AzureOpenAiHyperParameters
        """
        if hyperparameters:
            self.hyperparameters = {
                "batch_size": hyperparameters.batch_size,
                "learning_rate_multiplier": hyperparameters.learning_rate_multiplier,
                "n_epochs": hyperparameters.n_epochs,
            }
