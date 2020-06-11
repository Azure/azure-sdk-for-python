# -*- coding: utf-8 -*-
"""
Knowledge base of all built-in formatters.
"""

from __future__ import  absolute_import
from behave.formatter import _registry


# -----------------------------------------------------------------------------
# DATA:
# -----------------------------------------------------------------------------
# SCHEMA: formatter.name, formatter.class(_name)
_BUILTIN_FORMATS = [
    # pylint: disable=bad-whitespace
    ("plain",   "behave.formatter.plain:PlainFormatter"),
    ("pretty",  "behave.formatter.pretty:PrettyFormatter"),
    ("json",    "behave.formatter.json:JSONFormatter"),
    ("json.pretty", "behave.formatter.json:PrettyJSONFormatter"),
    ("null",      "behave.formatter.null:NullFormatter"),
    ("progress",  "behave.formatter.progress:ScenarioProgressFormatter"),
    ("progress2", "behave.formatter.progress:StepProgressFormatter"),
    ("progress3", "behave.formatter.progress:ScenarioStepProgressFormatter"),
    ("rerun",     "behave.formatter.rerun:RerunFormatter"),
    ("tags",          "behave.formatter.tags:TagsFormatter"),
    ("tags.location", "behave.formatter.tags:TagsLocationFormatter"),
    ("steps",         "behave.formatter.steps:StepsFormatter"),
    ("steps.doc",     "behave.formatter.steps:StepsDocFormatter"),
    ("steps.catalog", "behave.formatter.steps:StepsCatalogFormatter"),
    ("steps.usage",   "behave.formatter.steps:StepsUsageFormatter"),
    ("sphinx.steps",  "behave.formatter.sphinx_steps:SphinxStepsFormatter"),
]

# -----------------------------------------------------------------------------
# FUNCTIONS:
# -----------------------------------------------------------------------------
def setup_formatters():
    """Register all built-in formatters (lazy-loaded)."""
    _registry.register_formats(_BUILTIN_FORMATS)
