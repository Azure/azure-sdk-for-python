# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Compatibility tests for the public scoring-function base."""

from azure.search.documents.indexes.models import ScoringFunction

from _capabilities import require_capability


class TestScoringFunction:
    def test_scoring_function_preserves_field_name_and_boost(self):
        function = ScoringFunction(type="magnitude", field_name="rating", boost=2.0)
        assert function.field_name == "rating"
        assert function.boost == 2.0
        assert function.as_dict() == {"type": "magnitude", "fieldName": "rating", "boost": 2.0}

    def test_scoring_function_compatibility_does_not_add_fields_to_random(self):
        require_capability("azure.search.documents.indexes.models.RandomScoringFunction")
        from azure.search.documents.indexes.models import RandomScoringFunction, RandomScoringParameters

        function = RandomScoringFunction(parameters=RandomScoringParameters(seed_parameter="seed"))
        assert isinstance(function, ScoringFunction)
        assert function.as_dict() == {"type": "random", "random": {"seedParameter": "seed"}}

    def test_scoring_function_derived_models_preserve_public_inheritance_and_deserialization(self):
        from azure.search.documents.indexes.models import MagnitudeScoringFunction, ScoringProfile

        profile = ScoringProfile(
            {
                "name": "rating",
                "functions": [
                    {
                        "type": "magnitude",
                        "fieldName": "rating",
                        "boost": 2.0,
                        "magnitude": {"boostingRangeStart": 0, "boostingRangeEnd": 5},
                    }
                ],
            }
        )
        function = profile.functions[0]
        assert isinstance(function, MagnitudeScoringFunction)
        assert isinstance(function, ScoringFunction)
        assert function.field_name == "rating"
        assert function.boost == 2.0
