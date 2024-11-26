# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum


class SupportedLanguages(Enum):
    """Supported languages for evaluation, using ISO standard language codes.

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_simulate.py
            :start-after: [START supported_languages]
            :end-before: [END supported_languages]
            :language: python
            :dedent: 8
            :caption: Run the AdversarialSimulator with Simplified Chinese language support for evaluation.
    """

    Spanish = "es"
    Italian = "it"
    French = "fr"
    German = "de"
    SimplifiedChinese = "zh-cn"
    Portuguese = "pt"
    Japanese = "ja"
    English = "en"
