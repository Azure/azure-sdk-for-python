# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=C0302

"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from collections.abc import MutableMapping
from typing import Any, cast, IO, List, Optional, overload, Union

from azure.core import MatchConditions, PipelineClient
from azure.core.rest import HttpRequest, HttpResponse

from .. import models as _models
from .._configuration import TextTranslationClientConfiguration
from .._utils.utils import ClientMixinABC
from ._operations import _TextTranslationClientOperationsMixin as _TextTranslationClientOperationsMixinGenerated

JSON = MutableMapping[str, Any]


class _TextTranslationClientOperationsMixin(
    ClientMixinABC[PipelineClient[HttpRequest, HttpResponse], TextTranslationClientConfiguration]
):
    """Mixin class that delegates to the generated operations class while providing custom method signatures."""

    def _get_generated_operations(self) -> _TextTranslationClientOperationsMixinGenerated:  # pylint: disable=protected-access
        """Get an instance of the generated operations mixin.

        This creates a wrapper object that shares the same _client, _config, _serialize, and _deserialize
        attributes with self, allowing the generated operations to work correctly.

        :return: An instance of the generated operations mixin.
        :rtype: _TextTranslationClientOperationsMixinGenerated
        """
        if not hasattr(self, "_generated_ops_cache"):
            # Create a lightweight wrapper that shares attributes with self
            class GeneratedOpsWrapper(_TextTranslationClientOperationsMixinGenerated):
                pass

            wrapper = GeneratedOpsWrapper.__new__(GeneratedOpsWrapper)
            # Share the client infrastructure from self
            wrapper._client = self._client  # type: ignore
            wrapper._config = self._config  # type: ignore
            wrapper._serialize = self._serialize  # type: ignore
            wrapper._deserialize = self._deserialize  # type: ignore
            self._generated_ops_cache = wrapper  # type: ignore
        return self._generated_ops_cache  # type: ignore

    def get_supported_languages(
        self,
        *,
        client_trace_id: Optional[str] = None,
        scope: Optional[str] = None,
        accept_language: Optional[str] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        **kwargs: Any
    ) -> _models.GetSupportedLanguagesResult:
        """Gets the set of languages currently supported by other operations of the Translator.

        Gets the set of languages currently supported by other operations of the Translator.

        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword scope: A comma-separated list of names defining the group of languages to return.
         Allowed group names are: ``translation``, ``transliteration`` and ``dictionary``.
         If no scope is given, then all groups are returned, which is equivalent to passing
         ``scope=translation,transliteration,dictionary``. To decide which set of supported languages
         is appropriate for your scenario, see the description of the `response object
         <#response-body>`_. Default value is None.
        :paramtype scope: str
        :keyword accept_language: The language to use for user interface strings. Some of the fields in
         the response are names of languages or
         names of regions. Use this parameter to define the language in which these names are returned.
         The language is specified by providing a well-formed BCP 47 language tag. For instance, use
         the value ``fr``
         to request names in French or use the value ``zh-Hant`` to request names in Chinese
         Traditional.
         Names are provided in the English language when a target language is not specified or when
         localization
         is not available. Default value is None.
        :paramtype accept_language: str
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: GetSupportedLanguagesResult. The GetSupportedLanguagesResult is compatible with
         MutableMapping
        :rtype: ~azure.ai.translation.text.models.GetSupportedLanguagesResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._get_generated_operations().get_supported_languages(
            client_trace_id=client_trace_id,
            scope=scope,
            accept_language=accept_language,
            etag=etag,
            match_condition=match_condition,
            **kwargs
        )

    @overload  # type: ignore[override]
    def translate(
        self,
        body: List[str],
        *,
        to_language: List[str],
        from_language: Optional[str] = None,
        client_trace_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.TranslatedTextItem]:
        """Translate Text.

        Translates texts to the specified target languages.

        :param body: List of text strings to translate. Required.
        :type body: list[str]
        :keyword to_language: List of target languages of the translation outputs. The target language(s)
         must be one of the supported languages included in the translation scope. Required.
        :paramtype to_language: list[str]
        :keyword from_language: Language of the input text. If not specified, automatic language detection
         is applied to determine the source language. Default value is None.
        :paramtype from_language: str
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: list of TranslatedTextItem
        :rtype: list[~azure.ai.translation.text.models.TranslatedTextItem]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload  # type: ignore[override]
    def translate(
        self,
        body: List[_models.TranslateInputItem],
        *,
        client_trace_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.TranslatedTextItem]:
        """Translate text.

        Translates a list of input items with specified configurations.

        :param body: List of TranslateInputItem objects containing text and configurations for translation. Required.
        :type body: list[~azure.ai.translation.text.models.TranslateInputItem]
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: list of TranslatedTextItem
        :rtype: list[~azure.ai.translation.text.models.TranslatedTextItem]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload  # type: ignore[override]
    def translate(
        self,
        body: JSON,
        *,
        client_trace_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.TranslatedTextItem]:
        """Translate text.

        Translates text using a JSON body.

        :param body: JSON body containing translation request. Required.
        :type body: JSON
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: list of TranslatedTextItem
        :rtype: list[~azure.ai.translation.text.models.TranslatedTextItem]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    def translate(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        body: Union[List[str], List[_models.TranslateInputItem], JSON, IO[bytes]],
        *,
        to_language: Optional[List[str]] = None,
        from_language: Optional[str] = None,
        client_trace_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.TranslatedTextItem]:
        request_body: Union[_models.TranslateBody, JSON, IO[bytes]]

        if isinstance(body, list):
            if all(isinstance(item, _models.TranslateInputItem) for item in body):
                # Handle List[TranslateInputItem]
                request_body = _models.TranslateBody(inputs=cast(List[_models.TranslateInputItem], body))
            elif all(isinstance(item, str) for item in body):
                # Handle List[str] - convert to TranslateInputItem with targets
                targets = [_models.TranslationTarget(language=lang) for lang in (to_language or [])]
                inputs = [
                    _models.TranslateInputItem(text=cast(str, text), targets=targets, language=from_language)
                    for text in cast(List[str], body)
                ]
                request_body = _models.TranslateBody(inputs=inputs)
            else:
                raise ValueError(
                    "Invalid body type: list must contain either all strings or all TranslateInputItem objects"
                )
        else:
            # Handle JSON (dict/MutableMapping) or IO[bytes]
            request_body = body  # type: ignore

        result = self._get_generated_operations().translate(
            body=request_body, content_type=content_type, client_trace_id=client_trace_id, **kwargs
        )

        return result.value

    @overload  # type: ignore[override]
    def transliterate(
        self,
        body: List[str],
        *,
        language: str,
        from_script: str,
        to_script: str,
        client_trace_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.TransliteratedText]:
        """Transliterate Text.

        Transliterate Text.

        :param body: Defines the content of the request. Required.
        :type body: list[str]
        :keyword language: Specifies the language of the text to convert from one script to another.
         Possible languages are listed in the transliteration scope obtained by querying the service
         for its supported languages. Required.
        :paramtype language: str
        :keyword from_script: Specifies the script used by the input text. Look up supported languages
         using the transliteration scope,
         to find input scripts available for the selected language. Required.
        :paramtype from_script: str
        :keyword to_script: Specifies the output script. Look up supported languages using the
         transliteration scope, to find output
         scripts available for the selected combination of input language and input script. Required.
        :paramtype to_script: str
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: list of TransliteratedText
        :rtype: list[~azure.ai.translation.text.models.TransliteratedText]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload  # type: ignore[override]
    def transliterate(
        self,
        body: List[_models.InputTextItem],
        *,
        language: str,
        from_script: str,
        to_script: str,
        client_trace_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.TransliteratedText]:
        """Transliterate Text.

        Transliterate Text.

        :param body: Defines the content of the request. Required.
        :type body: list[~azure.ai.translation.text.models.InputTextItem]
        :keyword language: Specifies the language of the text to convert from one script to another.
         Possible languages are listed in the transliteration scope obtained by querying the service
         for its supported languages. Required.
        :paramtype language: str
        :keyword from_script: Specifies the script used by the input text. Look up supported languages
         using the transliteration scope,
         to find input scripts available for the selected language. Required.
        :paramtype from_script: str
        :keyword to_script: Specifies the output script. Look up supported languages using the
         transliteration scope, to find output
         scripts available for the selected combination of input language and input script. Required.
        :paramtype to_script: str
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: list of TransliteratedText
        :rtype: list[~azure.ai.translation.text.models.TransliteratedText]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload  # type: ignore[override]
    def transliterate(
        self,
        body: JSON,
        *,
        language: str,
        from_script: str,
        to_script: str,
        client_trace_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.TransliteratedText]:
        """Transliterate Text.

        Transliterates text using a JSON body.

        :param body: JSON body containing transliteration request. Required.
        :type body: JSON
        :keyword language: Specifies the language of the text to convert from one script to another.
         Possible languages are listed in the transliteration scope obtained by querying the service
         for its supported languages. Required.
        :paramtype language: str
        :keyword from_script: Specifies the script used by the input text. Look up supported languages
         using the transliteration scope,
         to find input scripts available for the selected language. Required.
        :paramtype from_script: str
        :keyword to_script: Specifies the output script. Look up supported languages using the
         transliteration scope, to find output
         scripts available for the selected combination of input language and input script. Required.
        :paramtype to_script: str
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: list of TransliteratedText
        :rtype: list[~azure.ai.translation.text.models.TransliteratedText]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    def transliterate(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        body: Union[List[str], List[_models.InputTextItem], JSON, IO[bytes]],
        *,
        language: str,
        from_script: str,
        to_script: str,
        client_trace_id: Optional[str] = None,
        content_type: str = "application/json"
    ) -> List[_models.TransliteratedText]:
        request_body: Union[_models.TransliterateBody, JSON, IO[bytes]]
        if isinstance(body, list):
            inputs: List[_models.InputTextItem] = []
            if all(isinstance(item, _models.InputTextItem) for item in body):
                inputs = cast(List[_models.InputTextItem], body)
            elif all(isinstance(item, str) for item in body):
                for text in body:
                    inputs.append(_models.InputTextItem(text=cast(str, text)))
            request_body = _models.TransliterateBody(inputs=inputs)
        else:
            # Handle JSON (dict) or IO[bytes]
            request_body = body  # type: ignore

        result = self._get_generated_operations().transliterate(
            body=request_body,
            language=language,
            from_script=from_script,
            to_script=to_script,
            content_type=content_type,
            client_trace_id=client_trace_id,
        )
        return result.value


__all__: List[str] = [
    "_TextTranslationClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
