# pylint: disable=line-too-long,useless-suppression,too-many-lines
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=C0302

"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, cast, IO, List, Optional, overload, Union
from ... import models as _models
from ._operations import _TextTranslationClientOperationsMixin as TextTranslationClientOperationsMixinGenerated


class _TextTranslationClientOperationsMixin(TextTranslationClientOperationsMixinGenerated):

    @overload
    async def translate(
        self,
        body: List[str],
        *,
        to_language: List[str],
        from_language: Optional[str] = None,
        client_trace_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.TranslatedTextItem]:
        """Translate text to the specified target language.

        This is a simplified overload that accepts a list of strings as input
        and translates them to the specified target language.

        :param body: List of text strings to translate. Required.
        :type body: list[str]
        :param to_language: Language code to translate the input text into. Required.
        :type to_language: str
        :param from_language: Language code of the input text. If not specified, the service will
         attempt to detect the language automatically. Default value is None.
        """

    @overload
    async def translate(
        self,
        body: List[_models.TranslateInputItem],
        *,
        client_trace_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.TranslatedTextItem]:
        # pylint: disable=line-too-long
        """Translate text to one or more target languages.

        Translates input text to the specified target language(s). This overload accepts
        a list of TranslateInputItem objects for structured input.

        :param body: List of TranslateInputItem objects containing text to translate. Required.
        :type body: list[~azure.ai.translation.text.models.TranslateInputItem]
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: TranslationResult containing the translated text
        :rtype: ~azure.ai.translation.text.models.TranslationResult
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = [
                    {
                        "text": "str"  # Text to translate. Required.
                    }
                ]

                # response body for status code(s): 200
                response == [
                    {
                        "translations": [
                            {
                                "text": "str",  # A string giving the translated
                                  text. Required.
                                "to": "str",  # A string representing the language
                                  code of the target language. Required.
                                "alignment": {
                                    "proj": "str"  # Maps input text to
                                      translated text. The alignment information is only provided when
                                      the request  parameter includeAlignment is true. Alignment is
                                      returned as a string value of the following  format:
                                      [[SourceTextStartIndex]:[SourceTextEndIndex]"u2013[TgtTextStartIndex]:[TgtTextEndIndex]].
                                      The colon separates start and end index, the dash separates the
                                      languages, and space separates the words.  One word may align
                                      with zero, one, or multiple words in the other language, and the
                                      aligned words may  be non-contiguous. When no alignment
                                      information is available, the alignment element will be empty.
                                      Required.
                                },
                                "sentLen": {
                                    "srcSentLen": [
                                        0  # An integer array representing
                                          the lengths of the sentences in the input text.  The length
                                          of the array is the number of sentences, and the values are
                                          the length of each sentence. Required.
                                    ],
                                    "transSentLen": [
                                        0  # An integer array representing
                                          the lengths of the sentences in the translated text.  The
                                          length of the array is the number of sentences, and the
                                          values are the length of each sentence. Required.
                                    ]
                                },
                                "transliteration": {
                                    "script": "str",  # A string specifying the
                                      script used in the output. Required.
                                    "text": "str"  # A string which is the result
                                      of converting the input string to the output script. Required.
                                }
                            }
                        ],
                        "detectedLanguage": {
                            "language": "str",  # A string representing the code of the
                              detected language. Required.
                            "score": 0.0  # A float value indicating the confidence in
                              the result. The score is between zero and one and a low score indicates a
                              low confidence. Required.
                        },
                        "sourceText": {
                            "text": "str"  # Input text in the default script of the
                              source language. Required.
                        }
                    }
                ]
        """

    @overload
    async def translate(
        self,
        body: IO[bytes],
        *,
        client_trace_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.TranslatedTextItem]:
        # pylint: disable=line-too-long
        """Translate text to one or more target languages.

        Translates input text to the specified target language(s). This overload accepts
        binary content for raw JSON input.

        :param body: Binary stream containing JSON request body. Required.
        :type body: IO[bytes]
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: TranslationResult containing the translated text
        :rtype: ~azure.ai.translation.text.models.TranslationResult
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == [
                    {
                        "translations": [
                            {
                                "text": "str",  # A string giving the translated
                                  text. Required.
                                "to": "str",  # A string representing the language
                                  code of the target language. Required.
                                "alignment": {
                                    "proj": "str"  # Maps input text to
                                      translated text. The alignment information is only provided when
                                      the request  parameter includeAlignment is true. Alignment is
                                      returned as a string value of the following  format:
                                      [[SourceTextStartIndex]:[SourceTextEndIndex]"u2013[TgtTextStartIndex]:[TgtTextEndIndex]].
                                      The colon separates start and end index, the dash separates the
                                      languages, and space separates the words.  One word may align
                                      with zero, one, or multiple words in the other language, and the
                                      aligned words may  be non-contiguous. When no alignment
                                      information is available, the alignment element will be empty.
                                      Required.
                                },
                                "sentLen": {
                                    "srcSentLen": [
                                        0  # An integer array representing
                                          the lengths of the sentences in the input text.  The length
                                          of the array is the number of sentences, and the values are
                                          the length of each sentence. Required.
                                    ],
                                    "transSentLen": [
                                        0  # An integer array representing
                                          the lengths of the sentences in the translated text.  The
                                          length of the array is the number of sentences, and the
                                          values are the length of each sentence. Required.
                                    ]
                                },
                                "transliteration": {
                                    "script": "str",  # A string specifying the
                                      script used in the output. Required.
                                    "text": "str"  # A string which is the result
                                      of converting the input string to the output script. Required.
                                }
                            }
                        ],
                        "detectedLanguage": {
                            "language": "str",  # A string representing the code of the
                              detected language. Required.
                            "score": 0.0  # A float value indicating the confidence in
                              the result. The score is between zero and one and a low score indicates a
                              low confidence. Required.
                        },
                        "sourceText": {
                            "text": "str"  # Input text in the default script of the
                              source language. Required.
                        }
                    }
                ]
        """

    async def translate(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        body: Union[List[str], List[_models.TranslateInputItem], IO[bytes]],
        *,
        to_language: Optional[List[str]] = None,
        from_language: Optional[str] = None,
        client_trace_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.TranslatedTextItem]:
        """Implementation of translate that handles multiple input types.

        This method automatically converts different input types into the required TranslateBody format.
        """
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

        result = await super().translate(
            body=request_body, content_type=content_type, client_trace_id=client_trace_id, **kwargs
        )

        return result.value

    @overload
    async def transliterate(
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
        """Transliterate text from one script to another.

        Converts text written in one script to another script for the specified language.
        This overload accepts a list of strings for simplified usage.

        :param body: List of text strings to transliterate. Required.
        :type body: list[str]
        :keyword language: Language code of the text to convert from one script to another.
         Possible languages are listed in the transliteration scope obtained by querying the service
         for its supported languages. Required.
        :paramtype language: str
        :keyword from_script: Script of the input text. Look up supported languages
         using the transliteration scope to find input scripts available for the selected language.
         Required.
        :paramtype from_script: str
        :keyword to_script: Output script. Look up supported languages using the
         transliteration scope to find output scripts available for the selected combination
         of input language and input script. Required.
        :paramtype to_script: str
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: TransliterateResult containing the transliterated text results
        :rtype: ~azure.ai.translation.text.models.TransliterateResult
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # Simplified usage with list of strings
                result = client.transliterate(
                    body=["こんにちは", "さようなら"],
                    language="ja",
                    from_script="Jpan",
                    to_script="Latn"
                )

                # response body for status code(s): 200
                response == [
                    {
                        "script": "str",  # A string specifying the script used in the
                          output. Required.
                        "text": "str"  # A string which is the result of converting the input
                          string to the output script. Required.
                    }
                ]
        """

    @overload
    async def transliterate(
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
        """Transliterate text from one script to another.

        Converts text written in one script to another script for the specified language.
        This overload accepts a list of InputTextItem objects for explicit control.

        :param body: List of InputTextItem objects containing text to transliterate. Required.
        :type body: list[~azure.ai.translation.text.models.InputTextItem]
        :keyword language: Language code of the text to convert from one script to another.
         Possible languages are listed in the transliteration scope obtained by querying the service
         for its supported languages. Required.
        :paramtype language: str
        :keyword from_script: Script of the input text. Look up supported languages
         using the transliteration scope to find input scripts available for the selected language.
         Required.
        :paramtype from_script: str
        :keyword to_script: Output script. Look up supported languages using the
         transliteration scope to find output scripts available for the selected combination
         of input language and input script. Required.
        :paramtype to_script: str
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: TransliterateResult containing the transliterated text results
        :rtype: ~azure.ai.translation.text.models.TransliterateResult
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                from azure.ai.translation.text.models import InputTextItem

                # Usage with InputTextItem objects
                body = [
                    InputTextItem(text="こんにちは"),
                    InputTextItem(text="さようなら")
                ]
                result = client.transliterate(
                    body=body,
                    language="ja",
                    from_script="Jpan",
                    to_script="Latn"
                )

                # response body for status code(s): 200
                response == [
                    {
                        "script": "str",  # A string specifying the script used in the
                          output. Required.
                        "text": "str"  # A string which is the result of converting the input
                          string to the output script. Required.
                    }
                ]
        """

    @overload
    async def transliterate(
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
        """Transliterate text from one script to another.

        Converts text written in one script to another script for the specified language.
        This overload accepts binary content for raw JSON input.

        :param body: Binary stream containing JSON request body. Required.
        :type body: IO[bytes]
        :keyword language: Language code of the text to convert from one script to another.
         Possible languages are listed in the transliteration scope obtained by querying the service
         for its supported languages. Required.
        :paramtype language: str
        :keyword from_script: Script of the input text. Look up supported languages
         using the transliteration scope to find input scripts available for the selected language.
         Required.
        :paramtype from_script: str
        :keyword to_script: Output script. Look up supported languages using the
         transliteration scope to find output scripts available for the selected combination
         of input language and input script. Required.
        :paramtype to_script: str
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: TransliterateResult containing the transliterated text results
        :rtype: ~azure.ai.translation.text.models.TransliterateResult
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == [
                    {
                        "script": "str",  # A string specifying the script used in the
                          output. Required.
                        "text": "str"  # A string which is the result of converting the input
                          string to the output script. Required.
                    }
                ]
        """

    async def transliterate(  # pyright: ignore[reportIncompatibleMethodOverride]
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
        """Implementation of transliterate that handles multiple input types.

        This method automatically converts simplified inputs (List[str], List[InputTextItem])
        into the required TransliterateBody format before calling the parent implementation.
        """
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

        result = await super().transliterate(
            body=request_body,
            language=language,
            from_script=from_script,
            to_script=to_script,
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
