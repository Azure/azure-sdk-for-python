import json
import logging
from pathlib import Path
import sys


_LOGGER = logging.getLogger(__name__)

_TAG_PREFIX = """### Tag: package-{api_version}-only

These settings apply only when `--tag=package-{api_version}-only` is specified on the command line.

```yaml $(tag) == 'package-{api_version}-only'
input-file:"""
_TAG_SUFFIX = "```\n\n"

_BATCH_PREFIX = """```yaml $(python) && $(multiapi)
batch:"""
_BATCH_SUFFIX = "```\n\n"

_PY_NAMESPACE = """### Tag: package-{api_version}-only and python

These settings apply only when `--tag=package-{api_version}-only --python` is specified on the command line.
Please also specify `--python-sdks-folder=<path to the root directory of your azure-sdk-for-python clone>`.

``` yaml $(tag) == 'package-{api_version}-only' && $(python)
python:
  namespace: $(python-base-namespace).{ns}
  output-folder: $(python-sdks-folder)/$(python-base-folder)/{ns}
```
"""

def get_api_versions(root):

    api_versions = {}
    prefixes_per_path = {}

    rp_folders = root.glob("Microsoft.*")
    for rp_folder in rp_folders:
        _LOGGER.info(f"Parsing folder {rp_folder}")
        for preview_stable in rp_folder.iterdir():
            _LOGGER.info(f"Currently in {preview_stable}")
            for api_version in preview_stable.iterdir():
                _LOGGER.info(f"Currently in {api_version}")
                for swagger in api_version.glob("*.json"):
                    prefixes_per_path[swagger] = parse_swagger(swagger)
                    api_versions.setdefault(api_version.name, []).append(swagger.relative_to(root).as_posix())

    # Try to detect when it's problematic. That's tough, the following logic is definitely
    # not handling all the touch parts yet...

    # 1- If a file declare several prefixes, let's warning
    for swagger_path, prefixed_used in prefixes_per_path.items():
        if len(prefixed_used) == 1:
            _LOGGER.info(f"File {swagger_path} uses only one prefix: {prefixed_used}")
        else:
            _LOGGER.warn(f"File {swagger_path} uses several prefixes: {prefixed_used}")


    # Let's print
    print_tags(api_versions)
    print_batch(api_versions)
    print_python_namespace(api_versions)

def print_tags(api_versions):
    for api_version in sorted(api_versions.keys(), reverse=True):
        swagger_files = api_versions[api_version]
        print(_TAG_PREFIX.format(api_version=api_version))
        for swagger_file in swagger_files:
            print("- {}".format(swagger_file))
        print(_TAG_SUFFIX)


def print_batch(api_versions):
    print(_BATCH_PREFIX)
    for api_version in sorted(api_versions.keys(), reverse=True):
        print(f"  - tag: package-{api_version}-only")
    print(_BATCH_SUFFIX)

def print_python_namespace(api_versions):
    for api_version in sorted(api_versions.keys(), reverse=True):
        swagger_files = api_versions[api_version]
        print(_PY_NAMESPACE.format(
            api_version=api_version,
            ns="v"+api_version.replace("-", "_"))
        )

def parse_swagger(swagger_path):
    _LOGGER.info(f"Parsing {swagger_path}")
    with swagger_path.open() as swagger:
        parsed_swagger = json.load(swagger)

    api_version = parsed_swagger["info"]["version"]

    operations = operation_finder(parsed_swagger)

    prefixed_used = {op.split("_")[0] for op in operations if "_" in op}
    return prefixed_used

def operation_finder(swagger_root):
    result = set()
    for key, node in swagger_root.items():
        if key == "definitions":  # Skipping some node
            return result
        if key == "operationId":
            result.add(node)
            # Can skip it now, only one operationId per node
            return result
        if isinstance(node, dict):
            result |= operation_finder(node)
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG if "--debug" in sys.argv else logging.WARNING)

    root = Path(__file__).parent

    root = Path(sys.argv[1]).relative_to(root)

    _LOGGER.info(f"My root: {root}")
    get_api_versions(root)
