# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Regenerate expected-wire baselines from the CURRENTLY-INSTALLED azure.ai.ml.

USAGE — capture baselines from production-proven ``main`` code:

    # in a checkout/worktree of main, with main's azure.ai.ml importable
    cd sdk/ml/azure-ai-ml/tests/smoke_serialization
    python regenerate_expected_wire.py

The baselines represent the known-correct (pre-migration) wire and are the source of truth. NEVER
regenerate them from a migration branch — that would make the equivalence check circular and
meaningless. Only regenerate from main, or from a commit whose wire is independently known-correct.

Builders are auto-discovered from every ``_builders*.py`` module (see ``_registry.all_builders``), so
adding a new family module requires no edit here.
"""
import os
import sys

from azure.ai.ml._utils.utils import AZUREML_PRIVATE_FEATURES_ENV_VAR

# Capture baselines with the same feature gate the tests use (see conftest._enable_private_preview),
# so ImportJob and other private-preview entities serialize identically at capture and at assert time.
os.environ[AZUREML_PRIVATE_FEATURES_ENV_VAR] = "true"

from _registry import all_builders
from _wire import save_expected_wire, serialize_wire


def main():
    """Capture every builder's wire into expected_wire/<case_name>.json."""
    builders = all_builders()
    failures = []
    for name in sorted(builders):
        try:
            wire = serialize_wire(builders[name]()._to_rest_object())
            save_expected_wire(name, wire)
            print("wrote baseline:", name)
        except Exception as exc:  # noqa: BLE001 - report all, fail at end
            failures.append((name, type(exc).__name__ + ": " + str(exc)[:200]))

    print("done: {0} baseline(s)".format(len(builders) - len(failures)))
    if failures:
        print("FAILURES ({0}):".format(len(failures)))
        for name, msg in failures:
            print("  FAIL", name, "->", msg)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
