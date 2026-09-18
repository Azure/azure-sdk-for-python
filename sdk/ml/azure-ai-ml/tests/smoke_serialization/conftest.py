# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Local pytest config that ISOLATES this folder from the parent ``tests/conftest.py``.

The parent ``tests/conftest.py`` imports ``devtools_testutils`` and other live-test machinery. These
smoke tests are pure-offline and must not pull that in. Having a ``pytest.ini`` here makes this folder
the pytest rootdir when invoked from inside it, so pytest only collects conftests from here down.
"""
import os

import pytest

from azure.ai.ml._utils.utils import AZUREML_PRIVATE_FEATURES_ENV_VAR


@pytest.fixture(autouse=True, scope="session")
def _enable_private_preview():
    """Enable private-preview features for the whole smoke session.

    Some entities (e.g. ImportJob) only serialize when private-preview is enabled. The goldens are
    captured from main with this same flag set (see ``generate_goldens.py``), so the comparison stays
    valid: both sides see the identical feature gate, and any wire delta is a real regression.
    """
    previous = os.environ.get(AZUREML_PRIVATE_FEATURES_ENV_VAR)
    os.environ[AZUREML_PRIVATE_FEATURES_ENV_VAR] = "true"
    yield
    if previous is None:
        os.environ.pop(AZUREML_PRIVATE_FEATURES_ENV_VAR, None)
    else:
        os.environ[AZUREML_PRIVATE_FEATURES_ENV_VAR] = previous
