# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for backward-compatible Azure OpenAI model name aliases."""

import pytest

from azure.search.documents.indexes.models import AzureOpenAIModelName, AzureOpenAIVectorizerParameters
from azure.search.documents.indexes.models._enums import AzureOpenAIModelName as GeneratedAzureOpenAIModelName


class TestAzureOpenAIModelName:
    @pytest.mark.parametrize(
        "legacy,current",
        [
            ("GPT_5_MINI", "GPT5_MINI"),
            ("GPT_5_NANO", "GPT5_NANO"),
            ("GPT_5_4_MINI", "GPT5_4_MINI"),
            ("GPT_5_4_NANO", "GPT5_4_NANO"),
        ],
    )
    def test_legacy_names_alias_current_members_and_preserve_wire_values(self, legacy, current):
        member = AzureOpenAIModelName[legacy]

        assert member is AzureOpenAIModelName[current]
        parameters = AzureOpenAIVectorizerParameters(model_name=member)
        assert parameters.as_dict()["modelName"] == GeneratedAzureOpenAIModelName[current].value
        assert AzureOpenAIModelName(member.value) is member

    def test_compatibility_enum_preserves_all_generated_members(self):
        assert GeneratedAzureOpenAIModelName.__members__.keys() <= AzureOpenAIModelName.__members__.keys()
        assert set(AzureOpenAIModelName) == set(GeneratedAzureOpenAIModelName)
