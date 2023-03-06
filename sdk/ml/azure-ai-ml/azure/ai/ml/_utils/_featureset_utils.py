# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
from typing import Dict

from .utils import load_yaml


def read_featureset_metadata_contents(*, path: str) -> Dict:
    metadata_path = str(Path(path, "FeaturesetSpec"))
    return load_yaml(metadata_path)
