# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Functions for interacting with AzureML."""
from typing import Dict, List

from azure.ai.generative.index._utils.logging import get_logger

logger = get_logger(__name__)


def get_workspace_from_environment():
    """Get the workspace from the run context if running in Azure, otherwise return None."""
    from azureml.core import Run

    run = Run.get_context()
    if hasattr(run, "experiment"):
        # We are running in Azure
        return run.experiment.workspace
    else:
        return None


def get_secret_from_workspace(name: str, workspace=None) -> str:
    """Get a secret from the workspace if running in Azure, otherwise get it from the environment."""
    secrets = get_secrets_from_workspace([name], workspace)
    return secrets[name]


def get_secrets_from_workspace(names: List[str], workspace=None) -> Dict[str, str]:
    """Get a secret from the workspace if running in Azure, otherwise get it from the environment."""
    import os

    ws = get_workspace_from_environment() if workspace is None else workspace
    if ws:
        keyvault = ws.get_default_keyvault()
        secrets = keyvault.get_secrets(names)
        logger.info("Run context and secrets retrieved", extra={"print": True})
    else:
        secrets = {}
        for name in names:
            secrets[name] = os.environ.get(name, os.environ.get(name.replace("-", "_")))

    return secrets
