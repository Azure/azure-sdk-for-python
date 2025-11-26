import re
import time
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
from .package_utils import (
    modify_file,
)
from .sdk_changelog import get_changelog_content, is_valid_changelog_content, is_arm_sdk, log_failed_message

logging.basicConfig(
    stream=sys.stdout,
    format="[%(levelname)s] %(message)s",
)
_LOGGER = logging.getLogger(__name__)


def is_valid_date_format(date_string: str) -> bool:
    """
    Validate if a date string has the format 'YYYY-MM-DD'.

    Args:
        date_string: The date string to validate

    Returns:
        True if the date string matches 'YYYY-MM-DD' format, False otherwise
    """
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def is_valid_version_format(version_string: str) -> bool:
    """
    Validate if a version string has the format 'X.Y.Z' or 'X.Y.ZbN'.
    """
    pattern = r"^\d+\.\d+\.\d+(b\d+)?$"
    return re.match(pattern, version_string) is not None


def current_date_str() -> str:
    """Get the current date as a string in 'YYYY-MM-DD' format."""
    result = time.strftime("%Y-%m-%d", time.localtime())
    _LOGGER.info(f"Using current date '{result}' as release date")
    return result


def preview_version_plus(preview_label: str, last_version: str) -> str:
    num = last_version.split(preview_label)
    num[1] = str(int(num[1]) + 1)
    return f"{num[0]}{preview_label}{num[1]}"


def stable_version_plus(changelog: str, last_version: str):
    has_breaking = "### Breaking Changes" in changelog
    has_fix = "### Bugs Fixed" in changelog

    num = last_version.split(".")
    if has_breaking:
        return f"{int(num[0]) + 1}.0.0"
    if has_fix:
        return f"{num[0]}.{num[1]}.{int(num[2]) + 1}"
    return f"{num[0]}.{int(num[1]) + 1}.0"


def calculate_next_version_proc(changelog_content: str, last_version: str, tag_is_stable: bool) -> str:
    if last_version == "":
        return "1.0.0b1"

    preview_version = "rc" in last_version or "b" in last_version
    #                                           |   preview tag                     | stable tag
    # preview version(1.0.0rc1/1.0.0b1)         | 1.0.0rc2(track1)/1.0.0b2(track2)  |  1.0.0
    # stable  version (1.0.0) (breaking change) | 2.0.0rc1(track1)/2.0.0b1(track2)  |  2.0.0
    # stable  version (1.0.0) (feature)         | 1.1.0rc1(track1)/1.1.0b1(track2)  |  1.1.0
    # stable  version (1.0.0) (bugfix)          | 1.0.1rc1(track1)/1.0.1b1(track2)  |  1.0.1
    preview_label = "b"
    if preview_version and not tag_is_stable:
        next_version = preview_version_plus(preview_label, last_version)
    elif preview_version and tag_is_stable:
        next_version = last_version.split(preview_label)[0]
    elif not preview_version and not tag_is_stable:
        next_version = stable_version_plus(changelog_content, last_version) + preview_label + "1"
    else:
        next_version = stable_version_plus(changelog_content, last_version)

    return next_version


def main(
    package_path: Path,
    *,
    release_type: Optional[str] = None,
    version: Optional[str] = None,
    release_date: Optional[str] = None,
    package_result: dict = {},
):
    package_name = package_path.name

    if package_result:
        # Use existing package_result values if provided
        changelog_content = package_result.get("changelog", {}).get("content", "")
        last_version = package_result.get("version", "")
        tag_is_stable = package_result.get("tagIsStable", False)
        release_date = package_result.get("targetReleaseDate") or current_date_str()
    else:
        # validate version format
        if version and not is_valid_version_format(version):
            _LOGGER.warning(f"Invalid version format: '{version}'. Expected format: 'X.Y.Z' or 'X.Y.ZbN'")
            version = None

        # Validate release_date format if provided
        if release_date and not is_valid_date_format(release_date):
            _LOGGER.warning(f"Invalid release date format: '{release_date}'. Expected format: 'YYYY-MM-DD'")
            release_date = None

        # validate release_type
        if release_type and release_type not in ["stable", "beta"]:
            _LOGGER.warning(f"Invalid release type: '{release_type}'. Expected 'stable' or 'beta'")
            release_type = None

        if release_date is None:
            release_date = current_date_str()

        if release_type is None:
            release_type = "beta"

        # calculate version if needed
        changelog_content, last_version = get_changelog_content(package_path, package_result, enable_changelog=True)
        tag_is_stable = release_type == "stable"

    if version is None and not is_valid_changelog_content(changelog_content) and is_arm_sdk(package_path.name):
        # When package_result is provided, it means this function is called in pipeline and we should not log error
        enable_log_error = not bool(package_result)
        log_failed_message(
            f"Changelog content for {package_name} seems invalid and we cannot calculate the next version based on it. "
            f"But we will stil update _version.py and CHANGELOG.md so that you could know where to update manually.",
            enable_log_error,
        )

    if version is None:
        version = calculate_next_version_proc(changelog_content, last_version, tag_is_stable)

    if package_result:
        package_result["version"] = version

    # edit _version.py
    version_files = list(package_path.rglob("**/_version.py"))

    def edit_version_file(content: list[str]):
        for i in range(0, len(content)):
            if content[i].find("VERSION") > -1:
                content[i] = f'VERSION = "{version}"\n'
                break

    for file in version_files:
        modify_file(str(file), edit_version_file)

    # edit CHANGELOG.md
    changelog_path = package_path / "CHANGELOG.md"
    if not changelog_path.exists():
        _LOGGER.info(f"CHANGELOG.md does not exist in {package_name}, so skip editing version for it.")
        return

    unchanged = True

    def edit_changelog_file(content: list[str]):
        nonlocal unchanged
        version_line = f"## {version} ({release_date})\n"
        for i in range(0, len(content)):
            if re.match(r"^## \d+\.\d+\.\d+(b\d+)?", content[i]):
                content[i] = version_line
                unchanged = False
                _LOGGER.info(f"Updated version line in CHANGELOG.md to: {version_line.strip()}")
                break

    modify_file(str(changelog_path), edit_changelog_file)
    if unchanged:
        _LOGGER.warning(f"No version line found in {changelog_path} to update.")


def generate_main():
    """Main method for command-line execution"""

    parser = argparse.ArgumentParser(
        description="Update version for Azure SDK package.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--package-path", dest="package_path", required=True, help="Absolute path to the package directory"
    )

    parser.add_argument(
        "--release-type",
        dest="release_type",
        choices=["stable", "beta"],
        default=None,
        help="Release type: 'stable' or 'beta' (optional)",
    )

    parser.add_argument(
        "--version", dest="version", default=None, help="Version string to set (e.g. '1.0.0b2' or '1.0.0') (optional)"
    )

    parser.add_argument(
        "--release-date", dest="release_date", default=None, help="Release date string (e.g. '2025-05-01') (optional)"
    )

    parser.add_argument("--debug", dest="debug", action="store_true", help="Verbosity in DEBUG mode")

    args = parser.parse_args()

    # Set up logging level
    main_logger = logging.getLogger()
    logging.basicConfig()
    main_logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    # Validate package path exists
    package_path = Path(args.package_path)
    if not package_path.exists():
        _LOGGER.error(f"Package path does not exist: {args.package_path}")
        sys.exit(1)

    if not package_path.is_dir():
        _LOGGER.error(f"Package path is not a directory: {args.package_path}")
        sys.exit(1)

    # Call the main function
    try:
        main(
            package_path=package_path.absolute(),
            release_type=args.release_type,
            version=args.version,
            release_date=args.release_date,
        )
        _LOGGER.info("Version update completed successfully")
    except Exception as e:
        _LOGGER.error(f"Failed to update version: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    generate_main()
