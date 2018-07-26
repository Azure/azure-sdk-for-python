import logging
from pathlib import Path
from typing import Dict, Any

import pytoml as toml

_LOGGER = logging.getLogger(__name__)

CONF_NAME = "sdk_packaging.toml"
_SECTION = "packaging"

# Default conf
_CONFIG = {
    "package_name": "packagename",
    "package_pprint_name": "MyService Management",
    "package_doc_id": "",
    "is_stable": False,
    "is_arm": True
}

def read_conf(folder: Path) -> Dict[str, Any]:
    conf_path = folder / CONF_NAME
    if not conf_path.exists():
        return {}

    with open(conf_path, "rb") as fd:
        return toml.load(fd)[_SECTION]

def build_default_conf(folder: Path, package_name: str) -> None:
    conf_path = folder / CONF_NAME
    if conf_path.exists():
        _LOGGER.info("Skipping default conf since the file exists")
        return

    _LOGGER.info("Build default conf for %s", package_name)
    conf = {_SECTION: _CONFIG.copy()}
    conf[_SECTION]["package_name"] = package_name

    with open(conf_path, "w") as fd:
        toml.dump(conf, fd)
