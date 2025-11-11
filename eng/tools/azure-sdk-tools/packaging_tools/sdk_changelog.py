import argparse
from functools import partial
import logging
import multiprocessing
import os
from pathlib import Path
import sys
import time

from typing import Any
from .package_utils import (
    change_log_generate,
    extract_breaking_change,
    get_version_info,
    modify_file,
)
from .generate_utils import (
    judge_tag_preview,
)

logging.basicConfig(stream=sys.stdout, format="[%(levelname)s] %(message)s")
_LOGGER = logging.getLogger(__name__)


def execute_func_with_timeout(func, timeout: int = 900) -> Any:
    """Execute function with timeout"""
    return multiprocessing.Pool(processes=1).apply_async(func).get(timeout)


def get_changelog_content(package_path: Path, package_result: dict, enable_changelog: bool) -> tuple[str, str]:

    package_name = package_path.name
    folder_name = package_path.parent.name

    if not package_name.startswith("azure-mgmt-"):
        _LOGGER.info(f"Skip changelog generation for data-plane package: {package_name}")
        md_output = "skip changelog generation for data-plane package"
        last_version, _ = get_version_info(package_name)
    else:
        tag_is_stable = package_result.get("tagIsStable")
        if tag_is_stable is None:
            tag_is_stable = not judge_tag_preview(str(package_path), package_name)
        last_version, last_stable_release = get_version_info(package_name, tag_is_stable)

        change_log_func = partial(
            change_log_generate,
            package_name,
            last_version,
            tag_is_stable,
            last_stable_release=last_stable_release,
            prefolder=folder_name,
        )

        try:
            if enable_changelog:
                md_output = execute_func_with_timeout(change_log_func)
            else:
                md_output = "skip changelog generation"
        except multiprocessing.TimeoutError:
            md_output = "change log generation was timeout!!! You need to write it manually!!!"
        except:
            md_output = "change log generation failed!!! You need to write it manually!!!"
        finally:
            for file in ["stable.json", "current.json"]:
                file_path = package_path / file
                if file_path.exists():
                    os.remove(file_path)
                    _LOGGER.info(f"Remove {file_path} which is temp file to generate changelog.")

    return md_output, last_version


def main(package_path: Path, *, enable_changelog: bool = True, package_result: dict = {}):

    package_name = package_path.name

    # Changelog generation
    try:
        changelog_generation_start_time = time.time()
        md_output, last_version = get_changelog_content(package_path, package_result, enable_changelog)
        _LOGGER.info(f"changelog generation cost time: {int(time.time() - changelog_generation_start_time)} seconds")
        if package_result:
            package_result["changelog"] = {
                "content": md_output,
                "hasBreakingChange": "Breaking Changes" in md_output,
                "breakingChangeItems": extract_breaking_change(md_output),
            }
            package_result["version"] = last_version

        _LOGGER.info(f"[PACKAGE]({package_name})[CHANGELOG]:{md_output}")

        # edit CHANGELOG.md with generated content
        version_line = "## 0.0.0 (UnReleased)\n\n"

        def edit_changelog_proc(content: list[str]):
            if last_version:
                if md_output:
                    content[1:1] = [
                        "\n",
                        version_line,
                        md_output,
                        "\n",
                    ]
                else:
                    content[1:1] = [
                        "\n",
                        version_line,
                        "tool can't generate changelog for this release, please update manually.",
                        "\n",
                    ]
            else:
                content.clear()
                content.extend(
                    [
                        "# Release History\n\n",
                        version_line,
                        "### Other Changes\n\n",
                        "  - Initial version",
                    ]
                )

        modify_file(str(package_path / "CHANGELOG.md"), edit_changelog_proc)

    except Exception as e:
        # When package_result is provided, it means this function is called in pipeline and we should not raise error
        log_func = _LOGGER.warning if package_result else _LOGGER.error
        log_func(f"Fail to generate changelog for {package_name}: {str(e)}")


def generate_main():
    """Entry point similar to sdk_generator but focused on changelog operations.

    Usage:
        sdk_changelog --package-path <ABSOLUTE_PATH>
    """
    parser = argparse.ArgumentParser(
        description="Generate or update changelog content for an existing Azure SDK package.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--package-path",
        required=True,
        help="Absolute path to the package directory (e.g. c:/azure-sdk-for-python/sdk/<service>/<package_name>).",
    )
    parser.add_argument("--debug", dest="debug", action="store_true", help="Enable DEBUG logging")

    args = parser.parse_args()
    main_logger = logging.getLogger()
    logging.basicConfig()
    main_logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    package_path = Path(args.package_path)
    if not package_path.exists():
        raise ValueError(f"Provided --package-path does not exist: {args.package_path}")
    if not package_path.is_dir():
        raise ValueError(f"Provided --package-path is not a directory: {args.package_path}")
    if not package_path.is_absolute():
        raise ValueError("--package-path must be an absolute path")

    main(package_path)


if __name__ == "__main__":
    generate_main()
