# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import functools
from devtools_testutils import PowerShellPreparer

TextTranslationPreparer = functools.partial(
    PowerShellPreparer, 
    'texttranslation',
    texttranslation_endpoint="https://fakeEndpoint.cognitive.microsofttranslator.com",
    texttranslation_apikey="fakeapikey",
    texttranslation_region="fakeregion",
)