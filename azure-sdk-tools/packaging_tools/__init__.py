import logging
from pathlib import Path
from typing import Dict, Any

from jinja2 import Template, PackageLoader, Environment
from .conf import read_conf, build_default_conf, CONF_NAME

_LOGGER = logging.getLogger(__name__)

_CWD = Path(__file__).resolve().parent
_TEMPLATE_PATH = _CWD / "template"

def build_config(config : Dict[str, Any]) -> Dict[str, str]:
    """Will build the actual config for Jinja2, based on SDK config.
    """
    result = config.copy()
    # Manage the classifier stable/beta
    is_stable = result.pop("is_stable", False)
    if is_stable:
        result["classifier"] = "Development Status :: 5 - Production/Stable"
    else:
        result["classifier"] = "Development Status :: 4 - Beta"
    # Manage the nspkg
    package_name = result["package_name"]
    result["package_nspkg"] = package_name[:package_name.rindex('-')]+"-nspkg"
    # ARM?
    result['is_arm'] = result.pop("is_arm", True)

    # Return result
    return result

def build_packaging(package_name: str, output_folder: str, build_conf: bool = False) -> None:
    _LOGGER.info("Building template %s", package_name)
    package_folder = Path(output_folder) / Path(package_name)

    if build_conf:
        build_default_conf(package_folder, package_name)

    conf = read_conf(package_folder)
    if not conf:
        raise ValueError("Create a {} file before calling this script".format(package_folder / CONF_NAME))

    env = Environment(
        loader=PackageLoader('packaging_tools', 'templates'),
        keep_trailing_newline=True
    )
    conf = build_config(conf)

    for template_name in env.list_templates():
        future_filepath = Path(output_folder) / package_name / template_name

        # Might decide to make it more generic one day
        if template_name == "HISTORY.rst" and future_filepath.exists():
            _LOGGER.info("Skipping HISTORY.txt template, since a previous one was found")
            # Never overwirte the ChangeLog
            continue

        template = env.get_template(template_name)
        result = template.render(**conf)

        with open(Path(output_folder) / package_name / template_name, "w") as fd:
            fd.write(result)

    _LOGGER.info("Template done %s", package_name)