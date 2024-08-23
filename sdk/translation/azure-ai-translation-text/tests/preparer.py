# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from devtools_testutils import EnvironmentVariableLoader

TextTranslationPreparer = functools.partial(
    EnvironmentVariableLoader,
    "translation",
    translation_text_endpoint="https://fakeEndpoint.cognitive.microsofttranslator.com",
    translation_text_custom_endpoint="https://fakeCustomEndpoint.cognitiveservices.azure.com",
    translation_text_custom_apikey="fakeapikey",
    translation_text_apikey="fakeapikey",
    translation_text_region="fakeregion",
    translation_text_resource_id="fakeResourceId",
)
