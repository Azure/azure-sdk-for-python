# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from __future__ import annotations

from typing import Any, Union, overload, IO, Any, TYPE_CHECKING
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

# Import specific model types only for static type checking to avoid runtime circular imports.
if TYPE_CHECKING:
    from ..models import _models

from ._operations import (
    _QuestionAnsweringAuthoringClientOperationsMixin as _QuestionAnsweringAuthoringClientOperationsMixinGenerated,
)


class _QuestionAnsweringAuthoringClientOperationsMixin(_QuestionAnsweringAuthoringClientOperationsMixinGenerated):
    """Mixin class for patching methods with backward compatible parameter names."""

    # create_project overloads with 'options' parameter
    @overload
    def create_project(
        self,
        project_name: str,
        options: _models.QuestionAnsweringProject,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> _models.QuestionAnsweringProject:
        """Create or update a project.

        :param project_name: Name of the project. Required.
        :type project_name: str
        :param options: The resource instance. Required.
        :type options: ~azure.ai.language.questionanswering.authoring.models.QuestionAnsweringProject
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: QuestionAnsweringProject. The QuestionAnsweringProject is compatible with MutableMapping
        :rtype: ~azure.ai.language.questionanswering.authoring.models.QuestionAnsweringProject
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_project(
        self, project_name: str, options: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.QuestionAnsweringProject:
        """Create or update a project.

        :param project_name: Name of the project. Required.
        :type project_name: str
        :param options: The resource instance. Required.
        :type options: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: QuestionAnsweringProject. The QuestionAnsweringProject is compatible with MutableMapping
        :rtype: ~azure.ai.language.questionanswering.authoring.models.QuestionAnsweringProject
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_project(
        self, project_name: str, options: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.QuestionAnsweringProject:
        """Create or update a project.

        :param project_name: Name of the project. Required.
        :type project_name: str
        :param options: The resource instance. Required.
        :type options: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: QuestionAnsweringProject. The QuestionAnsweringProject is compatible with MutableMapping
        :rtype: ~azure.ai.language.questionanswering.authoring.models.QuestionAnsweringProject
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def create_project(
        self,
        project_name: str,
        options: Union[_models.QuestionAnsweringProject, JSON, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> _models.QuestionAnsweringProject:
        """Create or update a project.

        :param project_name: Name of the project. Required.
        :type project_name: str
        :param options: The resource instance. Is either a QuestionAnsweringProject, JSON, or IO[bytes] type. Required.
        :type options: ~azure.ai.language.questionanswering.authoring.models.QuestionAnsweringProject or JSON or IO[bytes]
        :keyword content_type: Body Parameter content-type. Default value is "application/json".
        :paramtype content_type: str
        :return: QuestionAnsweringProject. The QuestionAnsweringProject is compatible with MutableMapping
        :rtype: ~azure.ai.language.questionanswering.authoring.models.QuestionAnsweringProject
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Call the parent implementation with 'body' parameter for backward compatibility
        return super().create_project(project_name=project_name, body=options, content_type=content_type, **kwargs)

    # update_synonyms overloads with 'synonyms' parameter
    @overload
    def update_synonyms(
        self,
        project_name: str,
        synonyms: _models.SynonymAssets,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> None:
        """Updates all the synonyms of a project.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param synonyms: All the synonyms of a project. Required.
        :type synonyms: ~azure.ai.language.questionanswering.authoring.models.SynonymAssets
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def update_synonyms(
        self, project_name: str, synonyms: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> None:
        """Updates all the synonyms of a project.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param synonyms: All the synonyms of a project. Required.
        :type synonyms: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def update_synonyms(
        self, project_name: str, synonyms: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> None:
        """Updates all the synonyms of a project.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param synonyms: All the synonyms of a project. Required.
        :type synonyms: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def update_synonyms(
        self,
        project_name: str,
        synonyms: Union[_models.SynonymAssets, JSON, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> None:
        """Updates all the synonyms of a project.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param synonyms: All the synonyms of a project. Is either a SynonymAssets, JSON, or IO[bytes] type. Required.
        :type synonyms: ~azure.ai.language.questionanswering.authoring.models.SynonymAssets or JSON or IO[bytes]
        :keyword content_type: Body Parameter content-type. Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Call the parent implementation with 'body' parameter for backward compatibility
        return super().update_synonyms(project_name=project_name, body=synonyms, content_type=content_type, **kwargs)

    # begin_update_qnas overloads with 'qnas' parameter
    @overload
    def begin_update_qnas(
        self,
        project_name: str,
        qnas: list[_models.UpdateQnaRecord],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        """Updates the QnAs of a project.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param qnas: Update QnAs parameters of a project. Required.
        :type qnas: list[~azure.ai.language.questionanswering.authoring.models.UpdateQnaRecord]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_update_qnas(
        self, project_name: str, qnas: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Updates the QnAs of a project.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param qnas: Update QnAs parameters of a project. Required.
        :type qnas: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_update_qnas(
        self, project_name: str, qnas: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Updates the QnAs of a project.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param qnas: Update QnAs parameters of a project. Required.
        :type qnas: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_update_qnas(
        self,
        project_name: str,
        qnas: Union[list[_models.UpdateQnaRecord], JSON, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        """Updates the QnAs of a project.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param qnas: Update QnAs parameters of a project. Is either a list of UpdateQnaRecord, JSON, or IO[bytes] type. Required.
        :type qnas: list[~azure.ai.language.questionanswering.authoring.models.UpdateQnaRecord] or JSON or IO[bytes]
        :keyword content_type: Body Parameter content-type. Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Call the parent implementation with 'body' parameter for backward compatibility
        return super().begin_update_qnas(project_name=project_name, body=qnas, content_type=content_type, **kwargs)

    # begin_update_sources overloads with 'sources' parameter
    @overload
    def begin_update_sources(
        self,
        project_name: str,
        sources: list[_models.UpdateSourceRecord],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        """Updates the sources of a project.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param sources: Update sources parameters of a project. Required.
        :type sources: list[~azure.ai.language.questionanswering.authoring.models.UpdateSourceRecord]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_update_sources(
        self, project_name: str, sources: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Updates the sources of a project.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param sources: Update sources parameters of a project. Required.
        :type sources: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_update_sources(
        self, project_name: str, sources: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Updates the sources of a project.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param sources: Update sources parameters of a project. Required.
        :type sources: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_update_sources(
        self,
        project_name: str,
        sources: Union[list[_models.UpdateSourceRecord], JSON, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        """Updates the sources of a project.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param sources: Update sources parameters of a project. Is either a list of UpdateSourceRecord, JSON, or IO[bytes] type. Required.
        :type sources: list[~azure.ai.language.questionanswering.authoring.models.UpdateSourceRecord] or JSON or IO[bytes]
        :keyword content_type: Body Parameter content-type. Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Call the parent implementation with 'body' parameter for backward compatibility
        return super().begin_update_sources(
            project_name=project_name, body=sources, content_type=content_type, **kwargs
        )


__all__: list[str] = [
    "_QuestionAnsweringAuthoringClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
