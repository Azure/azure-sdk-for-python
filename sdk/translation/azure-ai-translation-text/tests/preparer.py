# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import functools
from devtools_testutils import PowerShellPreparer

TextTranslationPreparer = functools.partial(
    PowerShellPreparer, 
    'text_translation',
    text_translation_endpoint="https://fakeEndpoint.cognitive.microsofttranslator.com",
    text_translation_custom_endpoint="https://fakeCustomEndpoint.cognitiveservices.azure.com",
    text_translation_apikey="fakeapikey",
    text_translation_region="fakeregion",
)