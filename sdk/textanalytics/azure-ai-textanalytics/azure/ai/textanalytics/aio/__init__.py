# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._text_analytics_client_async import TextAnalyticsClient
from ._lro_async import (
    AsyncAnalyzeHealthcareEntitiesLROPoller,
    AsyncAnalyzeActionsLROPoller,
    AsyncTextAnalysisLROPoller,
)

__all__ = [
    "TextAnalyticsClient",
    "AsyncAnalyzeHealthcareEntitiesLROPoller",
    "AsyncAnalyzeActionsLROPoller",
    "AsyncTextAnalysisLROPoller",
]
