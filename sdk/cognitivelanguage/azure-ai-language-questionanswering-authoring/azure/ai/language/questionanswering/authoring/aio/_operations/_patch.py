# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long,useless-suppression,duplicate-code,arguments-renamed,missing-module-docstring,missing-class-docstring,missing-function-docstring
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from collections.abc import MutableMapping
from typing import Any, Union, overload, IO
from azure.core.polling import AsyncLROPoller
from azure.core.tracing.decorator_async import distributed_trace_async
from ... import models as _models
from ._operations import (
    _QuestionAnsweringAuthoringClientOperationsMixin as _QuestionAnsweringAuthoringClientOperationsMixinGenerated,
)

JSON = MutableMapping[str, Any]


class _QuestionAnsweringAuthoringClientOperationsMixin(_QuestionAnsweringAuthoringClientOperationsMixinGenerated):
    """Mixin class for patching methods with backward compatible parameter names."""

    # create_project overloads with 'options' parameter
    @overload  # type: ignore
    async def create_project(
        self,
        project_name: str,
        options: _models.QuestionAnsweringProject,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
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

    @overload  # type: ignore
    async def create_project(
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
        :return: QuestionAnsweringProject. The QuestionAnsweringProject is compatible with
         MutableMapping
        :rtype: ~azure.ai.language.questionanswering.authoring.models.QuestionAnsweringProject
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload  # type: ignore
    async def create_project(
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
        :return: QuestionAnsweringProject. The QuestionAnsweringProject is compatible with
         MutableMapping
        :rtype: ~azure.ai.language.questionanswering.authoring.models.QuestionAnsweringProject
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def create_project(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, project_name: str, options: Union[_models.QuestionAnsweringProject, JSON, IO[bytes]], **kwargs: Any
    ) -> _models.QuestionAnsweringProject:
        """Create or update a project.

        :param project_name: Name of the project. Required.
        :type project_name: str
        :param options: The resource instance. Is one of the following types: QuestionAnsweringProject,
         JSON, IO[bytes] Required.
        :type options: ~azure.ai.language.questionanswering.authoring.models.QuestionAnsweringProject or
         JSON or IO[bytes]
        :return: QuestionAnsweringProject. The QuestionAnsweringProject is compatible with
         MutableMapping
        :rtype: ~azure.ai.language.questionanswering.authoring.models.QuestionAnsweringProject
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Call the parent implementation with 'body' parameter for backward compatibility
        return await super().create_project(project_name=project_name, body=options, **kwargs)

    # update_synonyms overloads with 'synonyms' parameter
    @overload  # type: ignore
    async def update_synonyms(
        self,
        project_name: str,
        synonyms: _models.SynonymAssets,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
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

    @overload  # type: ignore
    async def update_synonyms(
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

    @overload  # type: ignore
    async def update_synonyms(
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

    @distributed_trace_async
    async def update_synonyms(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, project_name: str, synonyms: Union[_models.SynonymAssets, JSON, IO[bytes]], **kwargs: Any
    ) -> None:
        """Updates all the synonyms of a project.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param synonyms: All the synonyms of a project. Is one of the following types: SynonymAssets, JSON,
         IO[bytes] Required.
        :type synonyms: ~azure.ai.language.questionanswering.authoring.models.SynonymAssets or JSON or
         IO[bytes]
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Call the parent implementation with 'body' parameter for backward compatibility
        return await super().update_synonyms(project_name=project_name, body=synonyms, **kwargs)

    # begin_update_qnas overloads with 'qnas' parameter
    @overload  # type: ignore
    async def begin_update_qnas(
        self,
        project_name: str,
        qnas: list[_models.UpdateQnaRecord],
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[None]:
        """Updates the QnAs of a project.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param qnas: Update QnAs parameters of a project. Required.
        :type qnas: list[~azure.ai.language.questionanswering.authoring.models.UpdateQnaRecord]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns None
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload  # type: ignore
    async def begin_update_qnas(
        self, project_name: str, qnas: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Updates the QnAs of a project.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param qnas: Update QnAs parameters of a project. Required.
        :type qnas: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns None
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def begin_update_qnas(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, project_name: str, qnas: Union[list[_models.UpdateQnaRecord], IO[bytes]], **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Updates the QnAs of a project.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param qnas: Update QnAs parameters of a project. Is either a [UpdateQnaRecord] type or a
         IO[bytes] type. Required.
        :type qnas: list[~azure.ai.language.questionanswering.authoring.models.UpdateQnaRecord] or
         IO[bytes]
        :return: An instance of AsyncLROPoller that returns None
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Call the parent implementation with 'body' parameter for backward compatibility
        return await super().begin_update_qnas(project_name=project_name, body=qnas, **kwargs)

    # begin_update_sources overloads with 'sources' parameter
    @overload  # type: ignore
    async def begin_update_sources(
        self,
        project_name: str,
        sources: list[_models.UpdateSourceRecord],
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[None]:
        """Updates the sources of a project.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param sources: Update sources parameters of a project. Required.
        :type sources: list[~azure.ai.language.questionanswering.authoring.models.UpdateSourceRecord]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns None
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload  # type: ignore
    async def begin_update_sources(
        self, project_name: str, sources: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Updates the sources of a project.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param sources: Update sources parameters of a project. Required.
        :type sources: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns None
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def begin_update_sources(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, project_name: str, sources: Union[list[_models.UpdateSourceRecord], IO[bytes]], **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Updates the sources of a project.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param sources: Update sources parameters of a project. Is either a [UpdateSourceRecord] type or a
         IO[bytes] type. Required.
        :type sources: list[~azure.ai.language.questionanswering.authoring.models.UpdateSourceRecord] or
         IO[bytes]
        :return: An instance of AsyncLROPoller that returns None
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Call the parent implementation with 'body' parameter for backward compatibility
        return await super().begin_update_sources(project_name=project_name, body=sources, **kwargs)


__all__: list[str] = [
    "_QuestionAnsweringAuthoringClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
