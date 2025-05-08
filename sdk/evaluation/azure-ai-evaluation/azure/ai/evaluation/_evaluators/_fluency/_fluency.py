# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Dict, List, Union

from typing_extensions import overload, override

from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._model_configurations import Conversation


class FluencyEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """
    Evaluates the fluency of a given response or a multi-turn conversation, including reasoning.

    The fluency measure assesses the extent to which the generated text conforms to grammatical rules, syntactic
    structures, and appropriate vocabulary usage, resulting in linguistically correct responses.

    Fluency scores range from 1 to 5, with 1 being the least fluent and 5 being the most fluent.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]
    :param threshold: The threshold for the fluency evaluator. Default is 3.
    :type threshold: int

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START fluency_evaluator]
            :end-before: [END fluency_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a FluencyEvaluator.

    .. admonition:: Example with Threshold:

        .. literalinclude:: ../samples/evaluation_samples_threshold.py
            :start-after: [START threshold_fluency_evaluator]
            :end-before: [END threshold_fluency_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize with threshold and call a FluencyEvaluator.

    .. admonition:: Example using Azure AI Project URL:
                
        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START fluency_evaluator]
            :end-before: [END fluency_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call FluencyEvaluator using Azure AI Project URL in the following format
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}

    .. note::

        To align with our support of a diverse set of models, an output key without the `gpt_` prefix has been added.
        To maintain backwards compatibility, the old key with the `gpt_` prefix is still be present in the output;
        however, it is recommended to use the new key moving forward as the old key will be deprecated in the future.
    """

    _PROMPTY_FILE = "fluency.prompty"
    _RESULT_KEY = "fluency"

    id = "azureml://registries/azureml/models/Fluency-Evaluator/versions/4"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, model_config, *, threshold=3):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        self._threshold = threshold
        self._higher_is_better = True
        super().__init__(
            model_config=model_config,
            prompty_file=prompty_path,
            result_key=self._RESULT_KEY,
            threshold=threshold,
            _higher_is_better=self._higher_is_better
        )

    @overload
    def __call__(
        self,
        *,
        response: str,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate fluency in given response

        :keyword response: The response to be evaluated.
        :paramtype response: str
        :return: The fluency score
        :rtype: Dict[str, float]
        """

    @overload
    def __call__(
        self,
        *,
        conversation: Conversation,
    ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]:
        """Evaluate fluency for a conversation

        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages", and potentially a global context under the key "context". Conversation turns are expected
            to be dictionaries with keys "content", "role", and possibly "context".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The fluency score
        :rtype: Dict[str, Union[float, Dict[str, List[float]]]]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """
        Evaluate fluency. Accepts either a response for a single evaluation,
        or a conversation for a multi-turn evaluation. If the conversation has more than one turn,
        the evaluator will aggregate the results of each turn.

        :keyword response: The response to be evaluated. Mutually exclusive with the "conversation" parameter.
        :paramtype response: Optional[str]
        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages". Conversation turns are expected to be dictionaries with keys "content" and "role".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The fluency score.
        :rtype: Union[Dict[str, float], Dict[str, Union[float, Dict[str, List[float]]]]]
        """
        return super().__call__(*args, **kwargs)
