# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Regenerate golden wire fixtures from the CURRENTLY-INSTALLED azure.ai.ml.

USAGE — capture goldens from production-proven ``main`` code:

    # in a checkout/worktree of main, with main's azure.ai.ml importable
    cd sdk/ml/azure-ai-ml/tests/smoke_serialization
    python generate_goldens.py

The goldens represent the OLD (pre-migration) wire and are the source of truth. NEVER regenerate them
from a migration branch — that would make the equivalence check circular and meaningless. Only
regenerate from main, or from a commit whose wire is independently known-correct.
"""
import sys

import os

from azure.ai.ml._utils.utils import AZUREML_PRIVATE_FEATURES_ENV_VAR

# Capture goldens with the same feature gate the tests use (see conftest._enable_private_preview),
# so ImportJob and other private-preview entities serialize identically at capture and at assert time.
os.environ[AZUREML_PRIVATE_FEATURES_ENV_VAR] = "true"

from _builders import (
    COMMAND_JOB_BUILDERS,
    FINETUNING_BUILDERS,
    IMPORT_JOB_BUILDERS,
    SCHEDULE_BUILDERS,
    SPARK_JOB_BUILDERS,
    SWEEP_JOB_BUILDERS,
)
from _wire import save_golden, serialize_wire


def main():
    """Capture every builder's wire into goldens/<name>.json."""
    all_builders = {}
    all_builders.update(COMMAND_JOB_BUILDERS)
    all_builders.update(SWEEP_JOB_BUILDERS)
    all_builders.update(SPARK_JOB_BUILDERS)
    all_builders.update(IMPORT_JOB_BUILDERS)
    all_builders.update(SCHEDULE_BUILDERS)
    all_builders.update(FINETUNING_BUILDERS)

    for name in sorted(all_builders):
        entity = all_builders[name]()
        wire = serialize_wire(entity._to_rest_object())
        save_golden(name, wire)
        print("wrote golden:", name)

    print("done: {0} golden(s)".format(len(all_builders)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
