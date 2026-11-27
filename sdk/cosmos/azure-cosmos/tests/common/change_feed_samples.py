# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Lets tests import the change feed samples so they can check the samples still work.

Why this helper is needed: as soon as a sample file is imported, it reads the
account settings (host, key, database and container names) from a ``config``
module. Tests do not have a real account, so a plain import would fail. This
helper gives the sample placeholder settings, so the sample's functions can
be imported and called on a test container.
"""

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace


def load_change_feed_sample(asynchronous, monkeypatch):
    """Import ``samples/change_feed_management.py``, or its async version, and return it.

    The placeholder settings are only used while the sample is imported and
    are removed afterwards. The sample's ``if __name__ == "__main__"`` block
    does not run, so nothing is sent to the service.

    Example::

        sample = load_change_feed_sample(asynchronous=False, monkeypatch=monkeypatch)
        sample.read_change_feed_with_continuation(container)
    """
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
