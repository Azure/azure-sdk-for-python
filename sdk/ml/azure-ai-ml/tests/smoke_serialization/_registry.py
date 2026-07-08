# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Auto-discovery of all builder registries in the smoke suite.

Every ``_builders*.py`` module in this folder may expose one or more module-level dicts whose name
ends in ``_BUILDERS`` (mapping ``case_name -> zero-arg builder``). ``all_builders()`` collects them
all, so the generator and any aggregate test never need editing when a new family module is added.
"""
import glob
import importlib
import os

_THIS_DIR = os.path.dirname(__file__)


def all_builders():
    """Return a merged ``{case_name: builder}`` dict across every ``_builders*.py`` module.

    :return: Merged mapping of case name to zero-arg builder callable.
    :rtype: dict
    :raises RuntimeError: if two modules define the same case name (case names must be globally unique).
    """
    merged = {}
    for path in sorted(glob.glob(os.path.join(_THIS_DIR, "_builders*.py"))):
        mod_name = os.path.splitext(os.path.basename(path))[0]
        module = importlib.import_module(mod_name)
        for attr in dir(module):
            if attr.endswith("_BUILDERS"):
                registry = getattr(module, attr)
                if isinstance(registry, dict):
                    for case_name, builder in registry.items():
                        if case_name in merged:
                            raise RuntimeError("Duplicate smoke case name '{0}' (in {1})".format(case_name, mod_name))
                        merged[case_name] = builder
    return merged
