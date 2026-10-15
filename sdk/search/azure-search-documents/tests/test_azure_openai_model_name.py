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
        "legacy,current,wire_value",
        [
            ("GPT_5_MINI", "GPT5_MINI", "gpt-5-mini"),
            ("GPT_5_NANO", "GPT5_NANO", "gpt-5-nano"),
            ("GPT_5_4_MINI", "GPT5_4_MINI", "gpt-5.4-mini"),
            ("GPT_5_4_NANO", "GPT5_4_NANO", "gpt-5.4-nano"),
        ],
    )
    def test_legacy_names_alias_current_members_and_preserve_wire_values(self, legacy, current, wire_value):
        member = AzureOpenAIModelName[legacy]

        assert member is AzureOpenAIModelName[current]
        assert member.value == wire_value
        parameters = AzureOpenAIVectorizerParameters(model_name=member)
        assert parameters.as_dict()["modelName"] == wire_value
        assert AzureOpenAIModelName(member.value) is member

    @pytest.mark.parametrize(
        "member,wire_value",
        [
            (AzureOpenAIModelName.GPT54, "gpt-5.4"),
            (AzureOpenAIModelName.GPT55, "gpt-5.5"),
            (AzureOpenAIModelName.GPT56_SOL, "gpt-5.6-sol"),
            (AzureOpenAIModelName.GPT56_TERRA, "gpt-5.6-terra"),
            (AzureOpenAIModelName.GPT56_LUNA, "gpt-5.6-luna"),
        ],
    )
    def test_generated_model_names_preserve_enum_type_and_wire_values(
        self, member: AzureOpenAIModelName, wire_value: str
    ) -> None:
        assert isinstance(member, (str, AzureOpenAIModelName))
        assert member.value == wire_value
        assert AzureOpenAIModelName(wire_value) is member
        assert AzureOpenAIModelName[member.name.lower()] is member
        assert getattr(AzureOpenAIModelName, member.name.lower()) is member
        assert AzureOpenAIVectorizerParameters(model_name=member).as_dict()["modelName"] == wire_value

    def test_compatibility_enum_preserves_all_generated_members(self):
        assert GeneratedAzureOpenAIModelName.__members__.keys() <= AzureOpenAIModelName.__members__.keys()
        assert set(AzureOpenAIModelName) == set(GeneratedAzureOpenAIModelName)
        for name, member in GeneratedAzureOpenAIModelName.__members__.items():
            assert AzureOpenAIModelName[name].value == member.value
