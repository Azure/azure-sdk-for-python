# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import sys
from typing import List

__all__: List[str] = []  # Add all objects you want publicly available to users at this package level

# Models used only as internal request/response envelopes by the patched
# translate/transliterate methods. Users interact with simpler inputs
# (List[str], List[TranslateInputItem], List[InputTextItem], JSON, IO[bytes])
# and receive unwrapped List[TranslatedTextItem]/List[TransliteratedText]
# results, so these envelope types should not be part of the public surface.
_INTERNAL_MODELS = {
    "TranslateBody",
    "TransliterateBody",
    "TranslationResult",
    "TransliterateResult",
}


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
    # Remove internal envelope models from the public ``__all__`` of the
    # models package. The names remain importable for internal use (the
    # generated operations still reference them via ``_models.<Name>``),
    # but they are excluded from ``from ... import *``, Sphinx autodoc,
    # and APIView's public-surface analysis.
    package_name = __package__ or __name__.rsplit(".", 1)[0]
    mod = sys.modules[package_name]
    current_all = getattr(mod, "__all__", None)
    if current_all is not None:
        setattr(mod, "__all__", [n for n in current_all if n not in _INTERNAL_MODELS])
