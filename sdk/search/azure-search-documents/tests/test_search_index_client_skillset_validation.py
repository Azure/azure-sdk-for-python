# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from azure.search.documents.indexes.models import(
    EntityRecognitionSkill,
    EntityRecognitionSkillVersion,
    SentimentSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
)


def test_entity_recogntion_skill_validation():
    with pytest.raises(ValueError) as err:
        s1 = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                    outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizationsV1")],
                                    model_version="1")
    assert 'model_version' in str(err)

    with pytest.raises(ValueError) as err:
        s2 = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                    outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizationsV3")],
                                    skill_version=EntityRecognitionSkillVersion.V3,
                                    include_typeless_entities=True)
    assert 'include_typeless_entities' in str(err)


def test_sentiment_skill_validation():
    with pytest.raises(ValueError) as err:
        skill = SentimentSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                               outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizationsV1")],
                               include_opinion_mining=True,
                               model_version="1")
    assert 'model_version' in str(err)
    assert 'include_opinion_mining' in str(err)
