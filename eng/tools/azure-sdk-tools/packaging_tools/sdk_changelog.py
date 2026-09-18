import argparse
from functools import partial
import json
import logging
import multiprocessing
import os
from pathlib import Path
import re
import sys
import time

from typing import Any, Optional
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


def is_first_release(last_version: str) -> bool:
    # if last_version is empty, it means this is the first release
    return not bool(last_version)


def is_valid_changelog_content(content: str) -> bool:
    for changelog_kind in ["Features Added", "Breaking Changes", "Bugs Fixed", "Other Changes"]:
        if f"### {changelog_kind}" in content:
            return True
    return False


def is_arm_sdk(package_name: str) -> bool:
    return package_name.startswith("azure-mgmt-")


# CHANGELOG.md is embedded into the package long_description (see setup.py template), so an
# unbounded changelog bloats the PyPI metadata. Trimming uses a high-water/low-water pattern:
# trimming is *triggered* when the file exceeds CHANGELOG_SIZE_LIMIT_BYTES, but when it runs the
# file is cut down toward CHANGELOG_TRIM_TARGET_BYTES (half the limit). Trimming to a lower
# target leaves headroom so the file does not immediately exceed the limit again on the next
# release, avoiding a churny re-trim of the CHANGELOG on almost every generation. At least
# CHANGELOG_MIN_KEEP_ENTRIES newest entries are always retained for usefulness (unless even that
# many entries would exceed the hard size limit, in which case as many as fit are kept).
CHANGELOG_SIZE_LIMIT_BYTES = 128 * 1024
CHANGELOG_TRIM_TARGET_BYTES = CHANGELOG_SIZE_LIMIT_BYTES // 2
CHANGELOG_MIN_KEEP_ENTRIES = 4
_TRIM_NOTE_PREFIX = "> Changelog entries prior to"
_VERSION_HEADER_RE = re.compile(r"^##\s+\d+\.\d+")


def trim_changelog_if_needed(
    package_path: Path,
    size_limit: int = CHANGELOG_SIZE_LIMIT_BYTES,
    trim_target: Optional[int] = None,
) -> bool:
    """Drop the oldest CHANGELOG.md entries when the file grows too large.

    The CHANGELOG is concatenated into the package ``long_description`` uploaded to PyPI, so it
    must not grow without bound. Trimming is triggered when ``CHANGELOG.md`` exceeds
    ``size_limit`` bytes; when it runs, the file is cut down toward ``trim_target`` bytes
    (defaults to half of ``size_limit``) by keeping the ``# Release History`` header plus the
    newest version entries, removing older entries completely, and appending a note pointing to
    PyPI for the full history. Cutting toward the lower target (rather than just under the limit)
    leaves headroom so the file does not immediately exceed the limit again on the next release.

    At least ``CHANGELOG_MIN_KEEP_ENTRIES`` newest entries are always kept for usefulness, even if
    that exceeds ``trim_target`` -- unless keeping that many would exceed the hard ``size_limit``,
    in which case only as many newest entries as fit under ``size_limit`` are kept (at least one).

    Returns True if the file was trimmed, False otherwise.
    """
    changelog_path = package_path / "CHANGELOG.md"
    if not changelog_path.exists():
        return False
    # Use the normalized (LF) UTF-8 byte length rather than stat().st_size: on Windows the file
    # is stored with CRLF line endings, so st_size would over-count relative to the LF content the
    # pipeline (Linux) actually ships, causing inconsistent trigger behavior across platforms.
    if len(changelog_path.read_text(encoding="utf-8").encode("utf-8")) <= size_limit:
        return False

    if trim_target is None:
        trim_target = size_limit // 2

    package_name = package_path.name
    trimmed = False

    def byte_len(lines: list[str]) -> int:
        return sum(len(line.encode("utf-8")) for line in lines)

    def trim_proc(content: list[str]):
        nonlocal trimmed
        version_indices = [i for i, line in enumerate(content) if _VERSION_HEADER_RE.match(line)]
        # main() inserts 0.0.0 as an unreleased placeholder; keep it, but don't use it as the
        # cutoff version in the trim note.
        trimmable_version_indices = [i for i in version_indices if content[i].split()[1] != "0.0.0"]
        # Nothing to trim if there is at most one entry. Return before mutating content so an
        # existing trim note is preserved on this no-op path (modify_file always writes content
        # back). The note is appended after all version headers and never matches the version
        # header regex, so its presence does not affect version_indices.
        if len(trimmable_version_indices) < 2:
            return

        # Remove any previous trim note so repeated runs don't accumulate duplicates. It lives
        # after all version headers, so version_indices computed above stay valid.
        content[:] = [line for line in content if not line.startswith(_TRIM_NOTE_PREFIX)]

        # Boundaries of each version section; the header (before the first entry) is always kept.
        n = len(trimmable_version_indices)
        bounds = trimmable_version_indices + [len(content)]
        header_bytes = byte_len(content[: trimmable_version_indices[0]])
        seg_bytes = [byte_len(content[bounds[j] : bounds[j + 1]]) for j in range(n)]
        # Reserve room for the note line so the trimmed file stays under the target/limit.
        note_reserve = 256

        # Keep the newest entries whose cumulative size fits under the target (always keep >= 1).
        keep_count = 1
        total = header_bytes + seg_bytes[0]
        for j in range(1, n):
            if total + seg_bytes[j] + note_reserve > trim_target:
                break
            total += seg_bytes[j]
            keep_count = j + 1

        # Always keep at least CHANGELOG_MIN_KEEP_ENTRIES for usefulness, even past the target...
        keep_count = min(n, max(keep_count, CHANGELOG_MIN_KEEP_ENTRIES))
        # ...but never exceed the hard size limit: drop the oldest kept entries until it fits.
        while keep_count > 1 and header_bytes + sum(seg_bytes[:keep_count]) + note_reserve > size_limit:
            keep_count -= 1

        # Everything already fits (should not happen once the file is over the limit, but guard).
        if keep_count >= n:
            return

        oldest_kept = content[trimmable_version_indices[keep_count - 1]].split()[1]
        note = (
            f"{_TRIM_NOTE_PREFIX} {oldest_kept} were removed to reduce file size. "
            f"See https://pypi.org/project/{package_name}/{oldest_kept}/ for the older history.\n"
        )
        del content[trimmable_version_indices[keep_count] :]
        # Ensure a blank line separates the last kept entry from the note.
        if content and content[-1].strip():
            content.append("\n")
        content.append(note)
        trimmed = True

    modify_file(str(changelog_path), trim_proc)
    if trimmed:
        _LOGGER.info(f"Trimmed CHANGELOG.md for {package_name} down to under {trim_target} bytes.")
    return trimmed


def execute_func_with_timeout(func, timeout: int = 900) -> Any:
    """Execute function with timeout.

    On timeout, the worker pool is forcefully terminated to prevent orphaned
    child processes from continuing to run.
    """
    pool = multiprocessing.Pool(processes=1)
    try:
        result = pool.apply_async(func)
        return result.get(timeout)
    except multiprocessing.TimeoutError:
        pool.terminate()
        pool.join()
        raise
    finally:
        pool.terminate()
        pool.join()


def get_changelog_content(
    package_path: Path, package_result: dict, enable_changelog: bool, timeout: int = 900
) -> tuple[str, str]:
    """Generate changelog content for the given package path.
    Args:
        package_path (Path): The path to the package directory.
        package_result (dict): The package result dictionary to store changelog info.
        enable_changelog (bool): Flag to enable or disable changelog generation.
        timeout (int): Timeout in seconds for changelog generation. Defaults to 900.
    Returns:
        tuple[str, str]: A tuple containing the generated markdown content and the last version.
    NOTE:
    1. for data-plane packages, changelog generation is skipped and a placeholder message is returned.
    2. for management-plane packages, changelog is always "### Other Changes\n\n  - Initial version" if it's the first release.
    """

    package_name = package_path.name

    if not is_arm_sdk(package_name):
        _LOGGER.info(f"Skip changelog generation for data-plane package: {package_name}")
        md_output = "skip changelog generation for data-plane package and please add changelog manually."
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
            prefolder=str(package_path.parent),
        )

        try:
            if enable_changelog:
                md_output = execute_func_with_timeout(change_log_func, timeout)
            else:
                md_output = "skip changelog generation"
        except multiprocessing.TimeoutError:
            md_output = "change log generation was timeout!!! You need to write it manually!!!"
        except Exception as e:
            md_output = "change log generation failed!!! You need to write it manually!!!"
            _LOGGER.warning(f"Exception occurred during changelog generation for {package_name}: {str(e)}")
        finally:
            for file in ["stable.json", "current.json"]:
                file_path = package_path / file
                if file_path.exists():
                    os.remove(file_path)
                    _LOGGER.info(f"Remove {file_path} which is temp file to generate changelog.")

    return md_output, last_version


def log_failed_message(message: str, enable_log_error: bool):
    if enable_log_error:
        _LOGGER.error(message)
    else:
        _LOGGER.warning(message)


def main(
    package_path: Path,
    *,
    enable_changelog: bool = True,
    package_result: dict = {},
    timeout: int = 900,
    output_json: Optional[Path] = None,
):
    """Generate SDK changes for a package.

    By default the generated changelog is written into ``CHANGELOG.md``. When
    ``output_json`` is provided, run in SDK change detector mode instead: write
    {"changes": ..., "hasBreakingChange": ...} to that
    file and do NOT modify ``CHANGELOG.md``.
    """

    package_name = package_path.name
    # When package_result is provided, it means this function is called in pipeline and we should not log error
    enable_log_error = not bool(package_result)

    # Changelog generation
    try:
        changelog_generation_start_time = time.time()
        md_output, last_version = get_changelog_content(package_path, package_result, enable_changelog, timeout=timeout)
        _LOGGER.info(f"changelog generation cost time: {int(time.time() - changelog_generation_start_time)} seconds")
        if package_result:
            package_result["changelog"] = {
                "content": md_output,
                "hasBreakingChange": "Breaking Changes" in md_output,
                "breakingChangeItems": extract_breaking_change(md_output),
            }
            package_result["version"] = last_version

        _LOGGER.info(f"[PACKAGE]({package_name})[CHANGELOG]:{md_output}")

        # SDK change detector mode: write JSON result and skip editing CHANGELOG.md
        if output_json is not None:
            result = {
                "changes": md_output,
                "hasBreakingChange": "Breaking Changes" in md_output,
            }
            output_json = Path(output_json)
            output_json.parent.mkdir(parents=True, exist_ok=True)
            with open(output_json, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            _LOGGER.info(f"[PACKAGE]({package_name})[SDK CHANGES] written to {output_json}: {json.dumps(result)}")
            return

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

        # Keep CHANGELOG.md from growing unbounded, since it is embedded into the PyPI long_description.
        trim_changelog_if_needed(package_path)

    except Exception as e:
        log_failed_message(f"Fail to generate changelog for {package_name}: {str(e)}", enable_log_error)
    else:
        if is_arm_sdk(package_name) and not is_valid_changelog_content(md_output):
            log_failed_message(
                f"Generated changelog content for {package_name} seems invalid. "
                f"And we still update CHANGELOG.md so that you could know where to update manually.",
                enable_log_error,
            )


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
    parser.add_argument(
        "--output-json",
        required=False,
        default=None,
        help=(
            "Path to a JSON output file. When provided, run in SDK change detector mode: "
            'generate the SDK changes, write {"changes": ..., "hasBreakingChange": ...} to this '
            "file and do NOT modify CHANGELOG.md. When omitted, update CHANGELOG.md as usual."
        ),
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=900,
        help="Timeout in seconds for changelog generation (default: 900).",
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

    output_json = Path(args.output_json) if args.output_json else None
    main(package_path, timeout=args.timeout, output_json=output_json)


if __name__ == "__main__":
    generate_main()
