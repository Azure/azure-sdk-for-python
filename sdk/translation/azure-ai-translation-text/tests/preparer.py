# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from devtools_testutils import EnvironmentVariableLoader

TextTranslationPreparer = functools.partial(
    EnvironmentVariableLoader,
    "translation",
    text_translation_endpoint="https://fakeEndpoint.cognitive.microsofttranslator.com",
    text_translation_custom_endpoint="https://fakeCustomEndpoint.cognitiveservices.azure.com",
    text_translation_custom_apikey="fakeapikey",
    text_translation_apikey="fakeapikey",
    text_translation_region="fakeregion",
    text_translation_resource_id="fakeResourceId",
)
