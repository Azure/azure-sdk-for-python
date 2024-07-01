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
from ._operations import TextTranslationClientOperationsMixin as TextTranslationClientOperationsMixinGenerated


class TextTranslationClientOperationsMixin(TextTranslationClientOperationsMixinGenerated):
    @overload
    def translate(
        self,
        body: List[str],
        *,
        to_language: List[str],
        client_trace_id: Optional[str] = None,
        from_language: Optional[str] = None,
        text_type: Optional[Union[str, _models.TextType]] = None,
        category: Optional[str] = None,
        profanity_action: Optional[Union[str, _models.ProfanityAction]] = None,
        profanity_marker: Optional[Union[str, _models.ProfanityMarker]] = None,
        include_alignment: Optional[bool] = None,
        include_sentence_length: Optional[bool] = None,
        suggested_from: Optional[str] = None,
        from_script: Optional[str] = None,
        to_script: Optional[str] = None,
        allow_fallback: Optional[bool] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.TranslatedTextItem]:
        # pylint: disable=line-too-long
        """Translate Text.

        Translate Text.

        :param body: Defines the content of the request. Required.
        :type body: list[str]
        :keyword to_language: Specifies the language of the output text. The target language must be one of the
         supported languages included
         in the translation scope. For example, use to_language=de to translate to German.
         It's possible to translate to multiple languages simultaneously by repeating the parameter in
         the query string.
         For example, use to_language=de&to_language=it to translate to German and Italian. Required.
        :paramtype to_language: list[str]
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword from_language: Specifies the language of the input text. Find which languages are
         available to translate from by
         looking up supported languages using the translation scope. If the from parameter isn't
         specified,
         automatic language detection is applied to determine the source language.

         You must use the from parameter rather than autodetection when using the dynamic dictionary
         feature.
         Note: the dynamic dictionary feature is case-sensitive. Default value is None.
        :paramtype from_language: str
        :keyword text_type: Defines whether the text being translated is plain text or HTML text. Any
         HTML needs to be a well-formed,
         complete element. Possible values are: plain (default) or html. Known values are: "Plain" and
         "Html". Default value is None.
        :paramtype text_type: str or ~azure.ai.translation.text.models.TextType
        :keyword category: A string specifying the category (domain) of the translation. This parameter
         is used to get translations
         from a customized system built with Custom Translator. Add the Category ID from your Custom
         Translator
         project details to this parameter to use your deployed customized system. Default value is:
         general. Default value is None.
        :paramtype category: str
        :keyword profanity_action: Specifies how profanities should be treated in translations.
         Possible values are: NoAction (default), Marked or Deleted. Known values are: "NoAction",
         "Marked", and "Deleted". Default value is None.
        :paramtype profanity_action: str or ~azure.ai.translation.text.models.ProfanityAction
        :keyword profanity_marker: Specifies how profanities should be marked in translations.
         Possible values are: Asterisk (default) or Tag. Known values are: "Asterisk" and "Tag".
         Default value is None.
        :paramtype profanity_marker: str or ~azure.ai.translation.text.models.ProfanityMarker
        :keyword include_alignment: Specifies whether to include alignment projection from source text
         to translated text.
         Possible values are: true or false (default). Default value is None.
        :paramtype include_alignment: bool
        :keyword include_sentence_length: Specifies whether to include sentence boundaries for the
         input text and the translated text.
         Possible values are: true or false (default). Default value is None.
        :paramtype include_sentence_length: bool
        :keyword suggested_from: Specifies a fallback language if the language of the input text can't
         be identified.
         Language autodetection is applied when the from parameter is omitted. If detection fails,
         the suggestedFrom language will be assumed. Default value is None.
        :paramtype suggested_from: str
        :keyword from_script: Specifies the script of the input text. Default value is None.
        :paramtype from_script: str
        :keyword to_script: Specifies the script of the translated text. Default value is None.
        :paramtype to_script: str
        :keyword allow_fallback: Specifies that the service is allowed to fall back to a general system
         when a custom system doesn't exist.
         Possible values are: true (default) or false.

         allowFallback=false specifies that the translation should only use systems trained for the
         category specified
         by the request. If a translation for language X to language Y requires chaining through a
         pivot language E,
         then all the systems in the chain (X → E and E → Y) will need to be custom and have the same
         category.
         If no system is found with the specific category, the request will return a 400 status code.
         allowFallback=true
         specifies that the service is allowed to fall back to a general system when a custom system
         doesn't exist. Default value is None.
        :paramtype allow_fallback: bool
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: list of TranslatedTextItem
        :rtype: list[~azure.ai.translation.text.models.TranslatedTextItem]
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = [
                    str"  # Text to translate. Required.
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
    def translate(
        self,
        body: List[_models.InputTextItem],
        *,
        to_language: List[str],
        client_trace_id: Optional[str] = None,
        from_language: Optional[str] = None,
        text_type: Optional[Union[str, _models.TextType]] = None,
        category: Optional[str] = None,
        profanity_action: Optional[Union[str, _models.ProfanityAction]] = None,
        profanity_marker: Optional[Union[str, _models.ProfanityMarker]] = None,
        include_alignment: Optional[bool] = None,
        include_sentence_length: Optional[bool] = None,
        suggested_from: Optional[str] = None,
        from_script: Optional[str] = None,
        to_script: Optional[str] = None,
        allow_fallback: Optional[bool] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.TranslatedTextItem]:
        # pylint: disable=line-too-long
        """Translate Text.

        Translate Text.

        :param body: Defines the content of the request. Required.
        :type body: list[~azure.ai.translation.text.models.InputTextItem]
        :keyword to_language: Specifies the language of the output text. The target language must be one of the
         supported languages included
         in the translation scope. For example, use to_language=de to translate to German.
         It's possible to translate to multiple languages simultaneously by repeating the parameter in
         the query string.
         For example, use to_language=de&to_language=it to translate to German and Italian. Required.
        :paramtype to_language: list[str]
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword from_language: Specifies the language of the input text. Find which languages are
         available to translate from by
         looking up supported languages using the translation scope. If the from parameter isn't
         specified,
         automatic language detection is applied to determine the source language.

         You must use the from parameter rather than autodetection when using the dynamic dictionary
         feature.
         Note: the dynamic dictionary feature is case-sensitive. Default value is None.
        :paramtype from_language: str
        :keyword text_type: Defines whether the text being translated is plain text or HTML text. Any
         HTML needs to be a well-formed,
         complete element. Possible values are: plain (default) or html. Known values are: "Plain" and
         "Html". Default value is None.
        :paramtype text_type: str or ~azure.ai.translation.text.models.TextType
        :keyword category: A string specifying the category (domain) of the translation. This parameter
         is used to get translations
         from a customized system built with Custom Translator. Add the Category ID from your Custom
         Translator
         project details to this parameter to use your deployed customized system. Default value is:
         general. Default value is None.
        :paramtype category: str
        :keyword profanity_action: Specifies how profanities should be treated in translations.
         Possible values are: NoAction (default), Marked or Deleted. Known values are: "NoAction",
         "Marked", and "Deleted". Default value is None.
        :paramtype profanity_action: str or ~azure.ai.translation.text.models.ProfanityAction
        :keyword profanity_marker: Specifies how profanities should be marked in translations.
         Possible values are: Asterisk (default) or Tag. Known values are: "Asterisk" and "Tag".
         Default value is None.
        :paramtype profanity_marker: str or ~azure.ai.translation.text.models.ProfanityMarker
        :keyword include_alignment: Specifies whether to include alignment projection from source text
         to translated text.
         Possible values are: true or false (default). Default value is None.
        :paramtype include_alignment: bool
        :keyword include_sentence_length: Specifies whether to include sentence boundaries for the
         input text and the translated text.
         Possible values are: true or false (default). Default value is None.
        :paramtype include_sentence_length: bool
        :keyword suggested_from: Specifies a fallback language if the language of the input text can't
         be identified.
         Language autodetection is applied when the from parameter is omitted. If detection fails,
         the suggestedFrom language will be assumed. Default value is None.
        :paramtype suggested_from: str
        :keyword from_script: Specifies the script of the input text. Default value is None.
        :paramtype from_script: str
        :keyword to_script: Specifies the script of the translated text. Default value is None.
        :paramtype to_script: str
        :keyword allow_fallback: Specifies that the service is allowed to fall back to a general system
         when a custom system doesn't exist.
         Possible values are: true (default) or false.

         allowFallback=false specifies that the translation should only use systems trained for the
         category specified
         by the request. If a translation for language X to language Y requires chaining through a
         pivot language E,
         then all the systems in the chain (X → E and E → Y) will need to be custom and have the same
         category.
         If no system is found with the specific category, the request will return a 400 status code.
         allowFallback=true
         specifies that the service is allowed to fall back to a general system when a custom system
         doesn't exist. Default value is None.
        :paramtype allow_fallback: bool
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: list of TranslatedTextItem
        :rtype: list[~azure.ai.translation.text.models.TranslatedTextItem]
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
    def translate(
        self,
        body: IO[bytes],
        *,
        to_language: List[str],
        client_trace_id: Optional[str] = None,
        from_language: Optional[str] = None,
        text_type: Optional[Union[str, _models.TextType]] = None,
        category: Optional[str] = None,
        profanity_action: Optional[Union[str, _models.ProfanityAction]] = None,
        profanity_marker: Optional[Union[str, _models.ProfanityMarker]] = None,
        include_alignment: Optional[bool] = None,
        include_sentence_length: Optional[bool] = None,
        suggested_from: Optional[str] = None,
        from_script: Optional[str] = None,
        to_script: Optional[str] = None,
        allow_fallback: Optional[bool] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.TranslatedTextItem]:
        # pylint: disable=line-too-long
        """Translate Text.

        Translate Text.

        :param body: Defines the content of the request. Required.
        :type body: IO[bytes]
        :keyword to_language: Specifies the language of the output text. The target language must be one of the
         supported languages included
         in the translation scope. For example, use to_language=de to translate to German.
         It's possible to translate to multiple languages simultaneously by repeating the parameter in
         the query string.
         For example, use to_language=de&to_language=it to translate to German and Italian. Required.
        :paramtype to_language: list[str]
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword from_language: Specifies the language of the input text. Find which languages are
         available to translate from by
         looking up supported languages using the translation scope. If the from parameter isn't
         specified,
         automatic language detection is applied to determine the source language.

         You must use the from parameter rather than autodetection when using the dynamic dictionary
         feature.
         Note: the dynamic dictionary feature is case-sensitive. Default value is None.
        :paramtype from_language: str
        :keyword text_type: Defines whether the text being translated is plain text or HTML text. Any
         HTML needs to be a well-formed,
         complete element. Possible values are: plain (default) or html. Known values are: "Plain" and
         "Html". Default value is None.
        :paramtype text_type: str or ~azure.ai.translation.text.models.TextType
        :keyword category: A string specifying the category (domain) of the translation. This parameter
         is used to get translations
         from a customized system built with Custom Translator. Add the Category ID from your Custom
         Translator
         project details to this parameter to use your deployed customized system. Default value is:
         general. Default value is None.
        :paramtype category: str
        :keyword profanity_action: Specifies how profanities should be treated in translations.
         Possible values are: NoAction (default), Marked or Deleted. Known values are: "NoAction",
         "Marked", and "Deleted". Default value is None.
        :paramtype profanity_action: str or ~azure.ai.translation.text.models.ProfanityAction
        :keyword profanity_marker: Specifies how profanities should be marked in translations.
         Possible values are: Asterisk (default) or Tag. Known values are: "Asterisk" and "Tag".
         Default value is None.
        :paramtype profanity_marker: str or ~azure.ai.translation.text.models.ProfanityMarker
        :keyword include_alignment: Specifies whether to include alignment projection from source text
         to translated text.
         Possible values are: true or false (default). Default value is None.
        :paramtype include_alignment: bool
        :keyword include_sentence_length: Specifies whether to include sentence boundaries for the
         input text and the translated text.
         Possible values are: true or false (default). Default value is None.
        :paramtype include_sentence_length: bool
        :keyword suggested_from: Specifies a fallback language if the language of the input text can't
         be identified.
         Language autodetection is applied when the from parameter is omitted. If detection fails,
         the suggestedFrom language will be assumed. Default value is None.
        :paramtype suggested_from: str
        :keyword from_script: Specifies the script of the input text. Default value is None.
        :paramtype from_script: str
        :keyword to_script: Specifies the script of the translated text. Default value is None.
        :paramtype to_script: str
        :keyword allow_fallback: Specifies that the service is allowed to fall back to a general system
         when a custom system doesn't exist.
         Possible values are: true (default) or false.

         allowFallback=false specifies that the translation should only use systems trained for the
         category specified
         by the request. If a translation for language X to language Y requires chaining through a
         pivot language E,
         then all the systems in the chain (X → E and E → Y) will need to be custom and have the same
         category.
         If no system is found with the specific category, the request will return a 400 status code.
         allowFallback=true
         specifies that the service is allowed to fall back to a general system when a custom system
         doesn't exist. Default value is None.
        :paramtype allow_fallback: bool
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: list of TranslatedTextItem
        :rtype: list[~azure.ai.translation.text.models.TranslatedTextItem]
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

    def translate(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        body: Union[List[str], List[_models.InputTextItem], IO[bytes]],
        *,
        to_language: List[str],
        client_trace_id: Optional[str] = None,
        from_language: Optional[str] = None,
        text_type: Optional[Union[str, _models.TextType]] = None,
        category: Optional[str] = None,
        profanity_action: Optional[Union[str, _models.ProfanityAction]] = None,
        profanity_marker: Optional[Union[str, _models.ProfanityMarker]] = None,
        include_alignment: Optional[bool] = None,
        include_sentence_length: Optional[bool] = None,
        suggested_from: Optional[str] = None,
        from_script: Optional[str] = None,
        to_script: Optional[str] = None,
        allow_fallback: Optional[bool] = None,
        **kwargs: Any
    ) -> List[_models.TranslatedTextItem]:
        request_body: Union[List[_models.InputTextItem], IO[bytes]]
        if isinstance(body, list) and all(isinstance(item, str) for item in body):
            input_text_items: List[_models.InputTextItem] = []
            for text in body:
                input_text_items.append(_models.InputTextItem(text=cast(str, text)))
            request_body = input_text_items
        else:
            request_body = cast(Union[List[_models.InputTextItem], IO[bytes]], body)

        return super().translate(
            body=request_body,
            to_language=to_language,
            client_trace_id=client_trace_id,
            from_language=from_language,
            text_type=text_type,
            category=category,
            profanity_action=profanity_action,
            profanity_marker=profanity_marker,
            include_alignment=include_alignment,
            include_sentence_length=include_sentence_length,
            suggested_from=suggested_from,
            from_script=from_script,
            to_script=to_script,
            allow_fallback=allow_fallback,
            **kwargs
        )

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
                        "script": "str",  # A string specifying the script used in the
                          output. Required.
                        "text": "str"  # A string which is the result of converting the input
                          string to the output script. Required.
                    }
                ]
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
                        "script": "str",  # A string specifying the script used in the
                          output. Required.
                        "text": "str"  # A string which is the result of converting the input
                          string to the output script. Required.
                    }
                ]
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

    def transliterate(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        body: Union[List[str], List[_models.InputTextItem], IO[bytes]],
        *,
        language: str,
        from_script: str,
        to_script: str,
        client_trace_id: Optional[str] = None,
        **kwargs: Any
    ) -> List[_models.TransliteratedText]:
        request_body: Union[List[_models.InputTextItem], IO[bytes]]
        if isinstance(body, list) and all(isinstance(item, str) for item in body):
            input_text_items: List[_models.InputTextItem] = []
            for text in body:
                input_text_items.append(_models.InputTextItem(text=cast(str, text)))
            request_body = input_text_items
        else:
            request_body = cast(Union[List[_models.InputTextItem], IO[bytes]], body)

        return super().transliterate(
            body=request_body,
            language=language,
            from_script=from_script,
            to_script=to_script,
            client_trace_id=client_trace_id,
            **kwargs
        )

    @overload
    def find_sentence_boundaries(
        self,
        body: List[str],
        *,
        client_trace_id: Optional[str] = None,
        language: Optional[str] = None,
        script: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.BreakSentenceItem]:
        # pylint: disable=line-too-long
        """Find Sentence Boundaries.

        Find Sentence Boundaries.

        :param body: Defines the content of the request. Required.
        :type body: list[str]
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword language: Language tag identifying the language of the input text.
         If a code isn't specified, automatic language detection will be applied. Default value is
         None.
        :paramtype language: str
        :keyword script: Script tag identifying the script used by the input text.
         If a script isn't specified, the default script of the language will be assumed. Default value
         is None.
        :paramtype script: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: list of BreakSentenceItem
        :rtype: list[~azure.ai.translation.text.models.BreakSentenceItem]
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
                        "sentLen": [
                            0  # An integer array representing the lengths of the
                              sentences in the input text. The length of the array is the number of
                              sentences, and the values are the length of each sentence. Required.
                        ],
                        "detectedLanguage": {
                            "language": "str",  # A string representing the code of the
                              detected language. Required.
                            "score": 0.0  # A float value indicating the confidence in
                              the result. The score is between zero and one and a low score indicates a
                              low confidence. Required.
                        }
                    }
                ]
        """

    @overload
    def find_sentence_boundaries(
        self,
        body: List[_models.InputTextItem],
        *,
        client_trace_id: Optional[str] = None,
        language: Optional[str] = None,
        script: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.BreakSentenceItem]:
        # pylint: disable=line-too-long
        """Find Sentence Boundaries.

        Find Sentence Boundaries.

        :param body: Defines the content of the request. Required.
        :type body: list[~azure.ai.translation.text.models.InputTextItem]
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword language: Language tag identifying the language of the input text.
         If a code isn't specified, automatic language detection will be applied. Default value is
         None.
        :paramtype language: str
        :keyword script: Script tag identifying the script used by the input text.
         If a script isn't specified, the default script of the language will be assumed. Default value
         is None.
        :paramtype script: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: list of BreakSentenceItem
        :rtype: list[~azure.ai.translation.text.models.BreakSentenceItem]
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
                        "sentLen": [
                            0  # An integer array representing the lengths of the
                              sentences in the input text. The length of the array is the number of
                              sentences, and the values are the length of each sentence. Required.
                        ],
                        "detectedLanguage": {
                            "language": "str",  # A string representing the code of the
                              detected language. Required.
                            "score": 0.0  # A float value indicating the confidence in
                              the result. The score is between zero and one and a low score indicates a
                              low confidence. Required.
                        }
                    }
                ]
        """

    @overload
    def find_sentence_boundaries(
        self,
        body: IO[bytes],
        *,
        client_trace_id: Optional[str] = None,
        language: Optional[str] = None,
        script: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.BreakSentenceItem]:
        # pylint: disable=line-too-long
        """Find Sentence Boundaries.

        Find Sentence Boundaries.

        :param body: Defines the content of the request. Required.
        :type body: IO[bytes]
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword language: Language tag identifying the language of the input text.
         If a code isn't specified, automatic language detection will be applied. Default value is
         None.
        :paramtype language: str
        :keyword script: Script tag identifying the script used by the input text.
         If a script isn't specified, the default script of the language will be assumed. Default value
         is None.
        :paramtype script: str
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: list of BreakSentenceItem
        :rtype: list[~azure.ai.translation.text.models.BreakSentenceItem]
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == [
                    {
                        "sentLen": [
                            0  # An integer array representing the lengths of the
                              sentences in the input text. The length of the array is the number of
                              sentences, and the values are the length of each sentence. Required.
                        ],
                        "detectedLanguage": {
                            "language": "str",  # A string representing the code of the
                              detected language. Required.
                            "score": 0.0  # A float value indicating the confidence in
                              the result. The score is between zero and one and a low score indicates a
                              low confidence. Required.
                        }
                    }
                ]
        """

    def find_sentence_boundaries(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        body: Union[List[str], List[_models.InputTextItem], IO[bytes]],
        *,
        client_trace_id: Optional[str] = None,
        language: Optional[str] = None,
        script: Optional[str] = None,
        **kwargs: Any
    ) -> List[_models.BreakSentenceItem]:
        request_body: Union[List[_models.InputTextItem], IO[bytes]]
        if isinstance(body, list) and all(isinstance(item, str) for item in body):
            input_text_items: List[_models.InputTextItem] = []
            for text in body:
                input_text_items.append(_models.InputTextItem(text=cast(str, text)))
            request_body = input_text_items

        else:
            request_body = cast(Union[List[_models.InputTextItem], IO[bytes]], body)

        return super().find_sentence_boundaries(
            body=request_body, language=language, script=script, client_trace_id=client_trace_id, **kwargs
        )

    @overload
    def lookup_dictionary_entries(
        self,
        body: List[str],
        *,
        from_language: str,
        to_language: str,
        client_trace_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.DictionaryLookupItem]:
        # pylint: disable=line-too-long
        """Lookup Dictionary Entries.

        Lookup Dictionary Entries.

        :param body: Defines the content of the request. Required.
        :type body: list[str]
        :keyword from_language: Specifies the language of the input text.
         The source language must be one of the supported languages included in the dictionary scope.
         Required.
        :paramtype from_language: str
        :keyword to_language: Specifies the language of the output text.
         The target language must be one of the supported languages included in the dictionary scope.
         Required.
        :paramtype to_language: str
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: list of DictionaryLookupItem
        :rtype: list[~azure.ai.translation.text.models.DictionaryLookupItem]
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
                        "displaySource": "str",  # A string giving the source term in a form
                          best suited for end-user display. For example, if the input is "JOHN", the
                          display form will reflect the usual spelling of the name: "John". Required.
                        "normalizedSource": "str",  # A string giving the normalized form of
                          the source term. For example, if the request is "JOHN", the normalized form
                          will be "john". The content of this field becomes the input to lookup
                          examples. Required.
                        "translations": [
                            {
                                "backTranslations": [
                                    {
                                        "displayText": "str",  # A string
                                          giving the source term that is a back-translation of the
                                          target in a form best suited for end-user display. Required.
                                        "frequencyCount": 0,  # An integer
                                          representing the frequency of this translation pair in the
                                          data. The main purpose of this field is to provide a user
                                          interface with a means to sort back-translations so the most
                                          frequent terms are first. Required.
                                        "normalizedText": "str",  # A string
                                          giving the normalized form of the source term that is a
                                          back-translation of the target. This value should be used as
                                          input to lookup examples. Required.
                                        "numExamples": 0  # An integer
                                          representing the number of examples that are available for
                                          this translation pair. Actual examples must be retrieved with
                                          a separate call to lookup examples. The number is mostly
                                          intended to facilitate display in a UX. For example, a user
                                          interface may add a hyperlink to the back-translation if the
                                          number of examples is greater than zero and show the
                                          back-translation as plain text if there are no examples. Note
                                          that the actual number of examples returned by a call to
                                          lookup examples may be less than numExamples, because
                                          additional filtering may be applied on the fly to remove
                                          "bad" examples. Required.
                                    }
                                ],
                                "score": 0.0,  # A value between 0.0 and 1.0
                                  which represents the "confidence"  (or perhaps more accurately,
                                  "probability in the training data") of that translation pair.  The
                                  sum of confidence scores for one source word may or may not sum to
                                  1.0. Required.
                                "displayTarget": "str",  # A string giving the term
                                  in the target language and in a form best suited for end-user
                                  display. Generally, this will only differ from the normalizedTarget
                                  in terms of capitalization. For example, a proper noun like "Juan"
                                  will have normalizedTarget = "juan" and displayTarget = "Juan".
                                  Required.
                                "normalizedTarget": "str",  # A string giving the
                                  normalized form of this term in the target language. This value
                                  should be used as input to lookup examples. Required.
                                "posTag": "str",  # A string associating this term
                                  with a part-of-speech tag. Required.
                                "prefixWord": "str"  # A string giving the word to
                                  display as a prefix of the translation. Currently, this is the
                                  gendered determiner of nouns, in languages that have gendered
                                  determiners. For example, the prefix of the Spanish word "mosca" is
                                  "la", since "mosca" is a feminine noun in Spanish.  This is only
                                  dependent on the translation, and not on the source.  If there is no
                                  prefix, it will be the empty string. Required.
                            }
                        ]
                    }
                ]
        """

    @overload
    def lookup_dictionary_entries(
        self,
        body: List[_models.InputTextItem],
        *,
        from_language: str,
        to_language: str,
        client_trace_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.DictionaryLookupItem]:
        # pylint: disable=line-too-long
        """Lookup Dictionary Entries.

        Lookup Dictionary Entries.

        :param body: Defines the content of the request. Required.
        :type body: list[~azure.ai.translation.text.models.InputTextItem]
        :keyword from_language: Specifies the language of the input text.
         The source language must be one of the supported languages included in the dictionary scope.
         Required.
        :paramtype from_language: str
        :keyword to_language: Specifies the language of the output text.
         The target language must be one of the supported languages included in the dictionary scope.
         Required.
        :paramtype to_language: str
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: list of DictionaryLookupItem
        :rtype: list[~azure.ai.translation.text.models.DictionaryLookupItem]
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
                        "displaySource": "str",  # A string giving the source term in a form
                          best suited for end-user display. For example, if the input is "JOHN", the
                          display form will reflect the usual spelling of the name: "John". Required.
                        "normalizedSource": "str",  # A string giving the normalized form of
                          the source term. For example, if the request is "JOHN", the normalized form
                          will be "john". The content of this field becomes the input to lookup
                          examples. Required.
                        "translations": [
                            {
                                "backTranslations": [
                                    {
                                        "displayText": "str",  # A string
                                          giving the source term that is a back-translation of the
                                          target in a form best suited for end-user display. Required.
                                        "frequencyCount": 0,  # An integer
                                          representing the frequency of this translation pair in the
                                          data. The main purpose of this field is to provide a user
                                          interface with a means to sort back-translations so the most
                                          frequent terms are first. Required.
                                        "normalizedText": "str",  # A string
                                          giving the normalized form of the source term that is a
                                          back-translation of the target. This value should be used as
                                          input to lookup examples. Required.
                                        "numExamples": 0  # An integer
                                          representing the number of examples that are available for
                                          this translation pair. Actual examples must be retrieved with
                                          a separate call to lookup examples. The number is mostly
                                          intended to facilitate display in a UX. For example, a user
                                          interface may add a hyperlink to the back-translation if the
                                          number of examples is greater than zero and show the
                                          back-translation as plain text if there are no examples. Note
                                          that the actual number of examples returned by a call to
                                          lookup examples may be less than numExamples, because
                                          additional filtering may be applied on the fly to remove
                                          "bad" examples. Required.
                                    }
                                ],
                                "score": 0.0,  # A value between 0.0 and 1.0
                                  which represents the "confidence"  (or perhaps more accurately,
                                  "probability in the training data") of that translation pair.  The
                                  sum of confidence scores for one source word may or may not sum to
                                  1.0. Required.
                                "displayTarget": "str",  # A string giving the term
                                  in the target language and in a form best suited for end-user
                                  display. Generally, this will only differ from the normalizedTarget
                                  in terms of capitalization. For example, a proper noun like "Juan"
                                  will have normalizedTarget = "juan" and displayTarget = "Juan".
                                  Required.
                                "normalizedTarget": "str",  # A string giving the
                                  normalized form of this term in the target language. This value
                                  should be used as input to lookup examples. Required.
                                "posTag": "str",  # A string associating this term
                                  with a part-of-speech tag. Required.
                                "prefixWord": "str"  # A string giving the word to
                                  display as a prefix of the translation. Currently, this is the
                                  gendered determiner of nouns, in languages that have gendered
                                  determiners. For example, the prefix of the Spanish word "mosca" is
                                  "la", since "mosca" is a feminine noun in Spanish.  This is only
                                  dependent on the translation, and not on the source.  If there is no
                                  prefix, it will be the empty string. Required.
                            }
                        ]
                    }
                ]
        """

    @overload
    def lookup_dictionary_entries(
        self,
        body: IO[bytes],
        *,
        from_language: str,
        to_language: str,
        client_trace_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> List[_models.DictionaryLookupItem]:
        # pylint: disable=line-too-long
        """Lookup Dictionary Entries.

        Lookup Dictionary Entries.

        :param body: Defines the content of the request. Required.
        :type body: IO[bytes]
        :keyword from_language: Specifies the language of the input text.
         The source language must be one of the supported languages included in the dictionary scope.
         Required.
        :paramtype from_language: str
        :keyword to_language: Specifies the language of the output text.
         The target language must be one of the supported languages included in the dictionary scope.
         Required.
        :paramtype to_language: str
        :keyword client_trace_id: A client-generated GUID to uniquely identify the request. Default
         value is None.
        :paramtype client_trace_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: list of DictionaryLookupItem
        :rtype: list[~azure.ai.translation.text.models.DictionaryLookupItem]
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == [
                    {
                        "displaySource": "str",  # A string giving the source term in a form
                          best suited for end-user display. For example, if the input is "JOHN", the
                          display form will reflect the usual spelling of the name: "John". Required.
                        "normalizedSource": "str",  # A string giving the normalized form of
                          the source term. For example, if the request is "JOHN", the normalized form
                          will be "john". The content of this field becomes the input to lookup
                          examples. Required.
                        "translations": [
                            {
                                "backTranslations": [
                                    {
                                        "displayText": "str",  # A string
                                          giving the source term that is a back-translation of the
                                          target in a form best suited for end-user display. Required.
                                        "frequencyCount": 0,  # An integer
                                          representing the frequency of this translation pair in the
                                          data. The main purpose of this field is to provide a user
                                          interface with a means to sort back-translations so the most
                                          frequent terms are first. Required.
                                        "normalizedText": "str",  # A string
                                          giving the normalized form of the source term that is a
                                          back-translation of the target. This value should be used as
                                          input to lookup examples. Required.
                                        "numExamples": 0  # An integer
                                          representing the number of examples that are available for
                                          this translation pair. Actual examples must be retrieved with
                                          a separate call to lookup examples. The number is mostly
                                          intended to facilitate display in a UX. For example, a user
                                          interface may add a hyperlink to the back-translation if the
                                          number of examples is greater than zero and show the
                                          back-translation as plain text if there are no examples. Note
                                          that the actual number of examples returned by a call to
                                          lookup examples may be less than numExamples, because
                                          additional filtering may be applied on the fly to remove
                                          "bad" examples. Required.
                                    }
                                ],
                                "score": 0.0,  # A value between 0.0 and 1.0
                                  which represents the "confidence"  (or perhaps more accurately,
                                  "probability in the training data") of that translation pair.  The
                                  sum of confidence scores for one source word may or may not sum to
                                  1.0. Required.
                                "displayTarget": "str",  # A string giving the term
                                  in the target language and in a form best suited for end-user
                                  display. Generally, this will only differ from the normalizedTarget
                                  in terms of capitalization. For example, a proper noun like "Juan"
                                  will have normalizedTarget = "juan" and displayTarget = "Juan".
                                  Required.
                                "normalizedTarget": "str",  # A string giving the
                                  normalized form of this term in the target language. This value
                                  should be used as input to lookup examples. Required.
                                "posTag": "str",  # A string associating this term
                                  with a part-of-speech tag. Required.
                                "prefixWord": "str"  # A string giving the word to
                                  display as a prefix of the translation. Currently, this is the
                                  gendered determiner of nouns, in languages that have gendered
                                  determiners. For example, the prefix of the Spanish word "mosca" is
                                  "la", since "mosca" is a feminine noun in Spanish.  This is only
                                  dependent on the translation, and not on the source.  If there is no
                                  prefix, it will be the empty string. Required.
                            }
                        ]
                    }
                ]
        """

    def lookup_dictionary_entries(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        body: Union[List[str], List[_models.InputTextItem], IO[bytes]],
        *,
        from_language: str,
        to_language: str,
        client_trace_id: Optional[str] = None,
        **kwargs: Any
    ) -> List[_models.DictionaryLookupItem]:
        request_body: Union[List[_models.InputTextItem], IO[bytes]]
        if isinstance(body, list) and all(isinstance(item, str) for item in body):
            input_text_items: List[_models.InputTextItem] = []
            for text in body:
                input_text_items.append(_models.InputTextItem(text=cast(str, text)))
            request_body = input_text_items
        else:
            request_body = cast(Union[List[_models.InputTextItem], IO[bytes]], body)

        return super().lookup_dictionary_entries(
            body=request_body,
            from_language=from_language,
            to_language=to_language,
            client_trace_id=client_trace_id,
            **kwargs
        )


__all__: List[str] = [
    "TextTranslationClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
