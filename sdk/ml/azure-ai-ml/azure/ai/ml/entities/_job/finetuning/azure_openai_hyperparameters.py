from typing import Optional
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    AzureOpenAiHyperParameters as RestAzureOpenAiHyperParameters,
)
from azure.ai.ml._utils._experimental import experimental


@experimental
class AzureOpenAIHyperparameters(RestTranslatableMixin):
    """Hyperparameters for Azure OpenAI model finetuning."""

    def __init__(
        self,
        *,
        batch_size: Optional[int] = None,
        learning_rate_multiplier: Optional[float] = None,
        n_epochs: Optional[int] = None,
        **kwargs: Optional[dict],
    ):
        """
        Initialize AzureOpenAIHyperparameters.
        param batch_size: The batch size for training.
        type batch_size: int
        param learning_rate_multiplier: The learning rate multiplier.
        type learning_rate_multiplier: float
        param n_epochs: The number of epochs.
        type n_epochs: int
        """
        self._batch_size = batch_size
        self._learning_rate_multiplier = learning_rate_multiplier
        self._n_epochs = n_epochs
        # Not exposed in the public API, so need to check how to handle this
        # self._additional_properties = kwargs

    @property
    def batch_size(self) -> Optional[int]:
        """Get the batch size for training."""
        return self._batch_size

    @batch_size.setter
    def batch_size(self, value: Optional[int]) -> None:
        """Set the batch size for training."""
        self._batch_size = value

    @property
    def learning_rate_multiplier(self) -> Optional[float]:
        """Get the learning rate multiplier."""
        return self._learning_rate_multiplier

    @learning_rate_multiplier.setter
    def learning_rate_multiplier(self, value: Optional[float]) -> None:
        """Set the learning rate multiplier."""
        self._learning_rate_multiplier = value

    @property
    def n_epochs(self) -> Optional[int]:
        """Get the number of epochs."""
        return self._n_epochs

    @n_epochs.setter
    def n_epochs(self, value: Optional[int]) -> None:
        """Set the number of epochs."""
        self._n_epochs = value

    # Not exposed in the public API, so need to check how to handle this
    # @property
    # def additional_properties(self) -> dict:
    #    """Get additional properties."""
    #    return self._additional_properties

    # @additional_properties.setter
    # def additional_properties(self, value: dict) -> None:
    #    """Set additional properties."""
    #    self._additional_properties = value

    def _to_rest_object(self) -> RestAzureOpenAiHyperParameters:
        return RestAzureOpenAiHyperParameters(
            batch_size=self._batch_size,
            learning_rate_multiplier=self._learning_rate_multiplier,
            n_epochs=self._n_epochs,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AzureOpenAIHyperparameters):
            return NotImplemented
        return (
            self._batch_size == other._batch_size
            and self._learning_rate_multiplier == other._learning_rate_multiplier
            and self._n_epochs == other._n_epochs
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @classmethod
    def _from_rest_object(cls, obj: RestAzureOpenAiHyperParameters) -> "AzureOpenAIHyperparameters":
        aoai_hyperparameters = cls(
            batch_size=obj.batch_size,
            learning_rate_multiplier=obj.learning_rate_multiplier,
            n_epochs=obj.n_epochs,
        )
        return aoai_hyperparameters
