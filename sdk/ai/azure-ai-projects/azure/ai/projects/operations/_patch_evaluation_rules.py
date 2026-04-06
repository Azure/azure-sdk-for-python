# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Union, Any, IO, overload
from azure.core.exceptions import HttpResponseError
from azure.core.tracing.decorator import distributed_trace
from ._operations import EvaluationRulesOperations as GeneratedEvaluationRulesOperations, JSON
from ._patch_agents import _PREVIEW_FEATURE_REQUIRED_CODE, _PREVIEW_FEATURE_ADDED_ERROR_MESSAGE
from .. import models as _models
from ..models._enums import _FoundryFeaturesOptInKeys
from ..models._patch import _FOUNDRY_FEATURES_HEADER_NAME, _has_header_case_insensitive


class EvaluationRulesOperations(GeneratedEvaluationRulesOperations):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.AIProjectClient`'s
        :attr:`evaluation_rules` attribute.
    """

    @overload
    def create_or_update(
        self, id: str, evaluation_rule: _models.EvaluationRule, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.EvaluationRule:
        """Create or update an evaluation rule.

        :param id: Unique identifier for the evaluation rule. Required.
        :type id: str
        :param evaluation_rule: Evaluation rule resource. Required.
        :type evaluation_rule: ~azure.ai.projects.models.EvaluationRule
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: EvaluationRule. The EvaluationRule is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.EvaluationRule
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @overload
    def create_or_update(
        self, id: str, evaluation_rule: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.EvaluationRule:
        """Create or update an evaluation rule.

        :param id: Unique identifier for the evaluation rule. Required.
        :type id: str
        :param evaluation_rule: Evaluation rule resource. Required.
        :type evaluation_rule: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: EvaluationRule. The EvaluationRule is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.EvaluationRule
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @overload
    def create_or_update(
        self, id: str, evaluation_rule: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.EvaluationRule:
        """Create or update an evaluation rule.

        :param id: Unique identifier for the evaluation rule. Required.
        :type id: str
        :param evaluation_rule: Evaluation rule resource. Required.
        :type evaluation_rule: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: EvaluationRule. The EvaluationRule is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.EvaluationRule
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @distributed_trace
    def create_or_update(
        self, id: str, evaluation_rule: Union[_models.EvaluationRule, JSON, IO[bytes]], **kwargs: Any
    ) -> _models.EvaluationRule:
        """Create or update an evaluation rule.

        :param id: Unique identifier for the evaluation rule. Required.
        :type id: str
        :param evaluation_rule: Evaluation rule resource. Is one of the following types:
         EvaluationRule, JSON, IO[bytes] Required.
        :type evaluation_rule: ~azure.ai.projects.models.EvaluationRule or JSON or IO[bytes]
        :return: EvaluationRule. The EvaluationRule is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.EvaluationRule
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if getattr(self._config, "allow_preview", False):
            # Add Foundry-Features header if not already present
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {
                    _FOUNDRY_FEATURES_HEADER_NAME: _FoundryFeaturesOptInKeys.EVALUATIONS_V1_PREVIEW.value
                }
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _FoundryFeaturesOptInKeys.EVALUATIONS_V1_PREVIEW.value
                kwargs["headers"] = headers

        try:
            return super().create_or_update(id, evaluation_rule, **kwargs)
        except HttpResponseError as exc:
            if exc.status_code == 403 and not self._config.allow_preview and exc.model is not None:
                api_error_response = exc.model
                if hasattr(api_error_response, "error") and api_error_response.error is not None:
                    if api_error_response.error.code == _PREVIEW_FEATURE_REQUIRED_CODE:
                        new_exc = HttpResponseError(
                            message=f"{exc.message} {_PREVIEW_FEATURE_ADDED_ERROR_MESSAGE}",
                        )
                        new_exc.status_code = exc.status_code
                        new_exc.reason = exc.reason
                        new_exc.response = exc.response
                        new_exc.model = exc.model
                        raise new_exc from exc
            raise
