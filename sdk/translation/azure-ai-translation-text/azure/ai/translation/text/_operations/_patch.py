# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=C0302

"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, cast, IO, List, Optional, overload, Union
from .. import models as _models
from ._operations import _TextTranslationClientOperationsMixin as TextTranslationClientOperationsMixinGenerated


class _TextTranslationClientOperationsMixin(TextTranslationClientOperationsMixinGenerated):

    @overload
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
        :type to_language: list[str]
        :param from_language: Language of the input text. If not specified, automatic language detection
         is applied to determine the source language. Default value is None.
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

    @overload
    def translate(
        self,
        body: List[_models.TranslateInputItem],
        *,
        client_trace_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.TranslatedTextItem]:
        """Translate text.

        Translates a list of input items with specified 

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

    @overload
    def translate(
        self,
        body: IO[bytes],
        *,
        client_trace_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.TranslatedTextItem]:
        """Translate text.

        Translates the specified binary content for raw JSON input.

        :param body: Binary stream containing JSON request body. Required.
        :type body: IO[bytes]
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: list of TranslatedTextItem
        :rtype: list[~azure.ai.translation.text.models.TranslatedTextItem]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    def translate(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        body: Union[List[str], List[_models.TranslateInputItem], IO[bytes]],
        *,
        to_language: Optional[List[str]] = None,
        from_language: Optional[str] = None,
        client_trace_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.TranslatedTextItem]:
        request_body: Union[_models.TranslateBody, IO[bytes]]

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
            # Handle IO[bytes]
            request_body = cast(Union[_models.TranslateBody, IO[bytes]], body)

        result = super().translate(
            body=request_body, content_type=content_type, client_trace_id=client_trace_id, **kwargs
        )

        return result.value

    @overload
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

    @overload
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

    @overload
    def transliterate(
        self,
        body: IO[bytes],
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
        :type body: IO[bytes]
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
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: list of TransliteratedText
        :rtype: list[~azure.ai.translation.text.models.TransliteratedText]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    def transliterate(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        body: Union[List[str], List[_models.InputTextItem], IO[bytes]],
        *,
        language: str,
        from_script: str,
        to_script: str,
        client_trace_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.TransliteratedText]:
        request_body: Union[_models.TransliterateBody, IO[bytes]]
        if isinstance(body, list):
            inputs: List[_models.InputTextItem] = []
            if all(isinstance(item, _models.InputTextItem) for item in body):
                inputs = cast(List[_models.InputTextItem], body)
            elif all(isinstance(item, str) for item in body):
                for text in body:
                    inputs.append(_models.InputTextItem(text=cast(str, text)))
            request_body = _models.TransliterateBody(inputs=inputs)
        else:
            request_body = cast(Union[_models.TransliterateBody, IO[bytes]], body)

        result = super().transliterate(
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
