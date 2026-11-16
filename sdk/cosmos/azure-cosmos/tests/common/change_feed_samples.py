# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Load change-feed samples without using account configuration or running setup."""

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace


def load_change_feed_sample(asynchronous, monkeypatch):
    suffix = "_async" if asynchronous else ""
    path = Path(__file__).resolve().parents[2] / "samples" / f"change_feed_management{suffix}.py"
    spec = importlib.util.spec_from_file_location(f"change_feed_sample{suffix}", path)
    sample = importlib.util.module_from_spec(spec)
    with monkeypatch.context() as context:
        context.setitem(sys.modules, "config", SimpleNamespace(settings={
            "host": "https://localhost:8081/",
            "master_key": "",
            "database_id": "",
            "container_id": "",
        }))
        spec.loader.exec_module(sample)
    return sample
