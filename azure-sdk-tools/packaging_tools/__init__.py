import logging
from pathlib import Path
from typing import Dict, Any

from jinja2 import Template, PackageLoader, Environment

_LOGGER = logging.getLogger(__name__)

_CWD = Path(__file__).resolve().parent
_TEMPLATE_PATH = _CWD / "template"

# Example of configuration loaded from a package
_CONFIG = {
    "package_name": "azure-mgmt-scheduler",
    "package_pprint_name": "Scheduler Management",
    "package_doc_id": "scheduler",
    "is_stable": True
}

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

    # Return result
    return result

def build_packaging(package_name, output_folder):
    _LOGGER.info("Building template %s", package_name)

    env = Environment(
        loader=PackageLoader('packaging_tools', 'templates'),
        keep_trailing_newline=True
    )
    conf = build_config(_CONFIG)

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