# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
Script to regenerate restclient from TypeSpec definitions.

Usage:
    python regenerate_restclient.py -a v2025_10_01_preview --spec-repo C:\\Repos\\azure-rest-api-specs
    python regenerate_restclient.py -a v2025_10_01_preview --spec-repo C:\\Repos\\azure-rest-api-specs -v

This script:
1. Compiles TypeSpec from azure-rest-api-specs repo
2. Generates Python SDK to a temp directory
3. Copies only the restclient folder to the target location
4. Fixes known TypeSpec emitter bugs (duplicate api_version)
5. Cleans up temp directory
"""

import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from argparse import ArgumentParser
from pathlib import Path
from platform import system

module_logger = logging.getLogger(__name__)

# Paths relative to the spec repo
TYPESPEC_PROJECT_PATH = "specification/machinelearningservices/MachineLearningServices.Management"
RESTCLIENT_RELATIVE_PATH = "sdk/ml/azure-ai-ml/azure/ai/ml/_restclient"


class Color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def _run_command(
    commands,
    cwd=None,
    stderr=subprocess.STDOUT,
    shell=False,
    env=None,
    stream_stdout=True,
    throw_on_retcode=True,
    logger=None,
):
    if logger is None:
        logger = module_logger

    if cwd is None:
        cwd = os.getcwd()

    t0 = time.perf_counter()
    try:
        logger.debug("Executing %s in %s", commands, cwd)
        out = ""
        with subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=stderr, cwd=cwd, shell=shell, env=env) as p:
            for line in p.stdout:
                line = line.decode("utf-8").rstrip()
                if line and line.strip():
                    logger.debug(line)
                    if stream_stdout:
                        sys.stdout.write(line)
                        sys.stdout.write("\n")
                    out += line
                    out += "\n"
            p.communicate()
            retcode = p.poll()
            if throw_on_retcode:
                if retcode:
                    raise subprocess.CalledProcessError(retcode, p.args, output=out, stderr=p.stderr)
        return retcode, out
    finally:
        t1 = time.perf_counter()
        logger.debug("Execution took %ss for %s in %s", t1 - t0, commands, cwd)


def run_command(
    commands, cwd=None, stderr=subprocess.STDOUT, shell=False, stream_stdout=True, throw_on_retcode=True, logger=None
):
    _, out = _run_command(
        commands,
        cwd=cwd,
        stderr=stderr,
        shell=shell,
        stream_stdout=stream_stdout,
        throw_on_retcode=throw_on_retcode,
        logger=logger,
    )
    return out


def print_blue(message):
    print(Color.BLUE + message + Color.END)


def print_green(message):
    print(Color.GREEN + message + Color.END)


def print_yellow(message):
    print(Color.YELLOW + message + Color.END)


def print_red(message):
    print(Color.RED + message + Color.END)


def step_banner(step_num, message):
    """Print a step banner for visibility."""
    print()
    print(Color.CYAN + "=" * 60 + Color.END)
    print(Color.CYAN + f"STEP {step_num}: {message}" + Color.END)
    print(Color.CYAN + "=" * 60 + Color.END)


def fix_duplicate_api_version(file_path: Path, verbose: bool = False) -> int:
    """
    Fix the TypeSpec Python emitter bug that generates duplicate api_version parameters.
    See: https://github.com/microsoft/typespec/issues/9384

    Returns the number of duplicates fixed.
    """
    if not file_path.exists():
        return 0

    content = file_path.read_text(encoding="utf-8")

    # Pattern to find consecutive duplicate api_version lines
    pattern = r"(\s+api_version=self\._config\.api_version,\r?\n)\s+api_version=self\._config\.api_version,"

    # Count matches before fixing
    matches = re.findall(pattern, content)
    count = len(matches)

    if count > 0:
        fixed_content = re.sub(pattern, r"\1", content)
        file_path.write_text(fixed_content, encoding="utf-8")
        if verbose:
            print_yellow(f"  Fixed {count} duplicate api_version occurrences in {file_path.name}")

    return count


def regenerate_restclient(api_version: str, spec_repo: Path, verbose: bool = False):
    """
    Regenerate restclient from TypeSpec definitions.

    Args:
        api_version: The API version to generate (e.g., "v2025_10_01_preview")
        spec_repo: Path to the azure-rest-api-specs repository
        verbose: Whether to show verbose output
    """
    # Normalize api_version format (support both v2025_10_01_preview and v2025-10-01-preview)
    api_version_normalized = api_version.lower().replace("-", "_")
    if not api_version_normalized.startswith("v"):
        api_version_normalized = "v" + api_version_normalized

    # Paths
    typespec_project_dir = spec_repo / TYPESPEC_PROJECT_PATH
    tspconfig_path = typespec_project_dir / "tspconfig.yaml"
    main_tsp_path = typespec_project_dir / "main.tsp"

    # Get the script's directory to find the restclient path
    script_dir = Path(__file__).parent.absolute()
    sdk_package_dir = script_dir.parent  # azure-ai-ml directory
    restclient_base_path = sdk_package_dir / "azure" / "ai" / "ml" / "_restclient"
    target_restclient_path = restclient_base_path / api_version_normalized

    command_args = {"shell": system() == "Windows", "stream_stdout": verbose}

    # =========================================================================
    # STEP 1: Validate inputs
    # =========================================================================
    step_banner(1, "Validating inputs")

    print_blue(f"  API Version: {api_version_normalized}")
    print_blue(f"  Spec repo: {spec_repo}")
    print_blue(f"  TypeSpec project: {typespec_project_dir}")
    print_blue(f"  Target restclient path: {target_restclient_path}")

    if not spec_repo.exists():
        print_red(f"ERROR: Spec repo not found at {spec_repo}")
        print_yellow("Please clone azure-rest-api-specs or specify --spec-repo path")
        sys.exit(1)

    if not tspconfig_path.exists():
        print_red(f"ERROR: tspconfig.yaml not found at {tspconfig_path}")
        sys.exit(1)

    if not main_tsp_path.exists():
        print_red(f"ERROR: main.tsp not found at {main_tsp_path}")
        sys.exit(1)

    print_green("  ✓ All inputs validated")

    # =========================================================================
    # STEP 2: Create temp directory for generation
    # =========================================================================
    step_banner(2, "Creating temp directory")

    temp_dir = Path(tempfile.mkdtemp(prefix="azure_sdk_gen_"))
    print_blue(f"  Temp directory: {temp_dir}")
    print_green("  ✓ Temp directory created")

    try:
        # =====================================================================
        # STEP 3: Run TypeSpec compilation
        # =====================================================================
        step_banner(3, "Running TypeSpec compilation")

        print_blue(f"  Working directory: {typespec_project_dir}")
        print_blue(f"  Output directory: {temp_dir}")

        # Build the tsp compile command
        commands = [
            "npx",
            "tsp",
            "compile",
            "main.tsp",
            "--emit",
            "@azure-tools/typespec-python",
            "--output-dir",
            str(temp_dir),
        ]

        print_blue(f"  Command: {' '.join(commands)}")
        print()

        run_command(
            commands,
            cwd=str(typespec_project_dir),
            throw_on_retcode=True,
            **command_args,
        )

        print_green("  ✓ TypeSpec compilation completed")

        # =====================================================================
        # STEP 4: Find the generated restclient folder
        # =====================================================================
        step_banner(4, "Finding generated restclient")

        # The TypeSpec emitter generates to: {output-dir}/{service-dir}/...
        # Based on tspconfig.yaml, service-dir is "sdk/ml/azure-ai-ml"
        generated_restclient_base = temp_dir / RESTCLIENT_RELATIVE_PATH

        print_blue(f"  Looking in: {generated_restclient_base}")

        if not generated_restclient_base.exists():
            print_red(f"ERROR: Generated restclient path not found: {generated_restclient_base}")
            print_yellow("  Listing temp directory contents:")
            for item in temp_dir.rglob("*"):
                if item.is_dir():
                    print(f"    [DIR] {item.relative_to(temp_dir)}")
            sys.exit(1)

        # Find the version folder
        generated_version_path = generated_restclient_base / api_version_normalized

        if not generated_version_path.exists():
            print_yellow(f"  Version folder {api_version_normalized} not found")
            print_yellow("  Available folders in restclient directory:")
            for item in generated_restclient_base.iterdir():
                if item.is_dir():
                    print(f"    - {item.name}")

            # Try to find any version folder
            version_folders = [d for d in generated_restclient_base.iterdir() if d.is_dir() and d.name.startswith("v")]
            if len(version_folders) == 1:
                generated_version_path = version_folders[0]
                print_yellow(f"  Using found version folder: {generated_version_path.name}")
            else:
                print_red("ERROR: Could not determine which version folder to use")
                sys.exit(1)

        print_green(f"  ✓ Found generated restclient at: {generated_version_path}")

        # =====================================================================
        # STEP 5: Fix TypeSpec emitter bugs
        # =====================================================================
        step_banner(5, "Fixing TypeSpec emitter bugs")

        total_fixes = 0

        # Fix duplicate api_version in sync operations
        sync_ops_path = generated_version_path / "operations" / "_operations.py"
        total_fixes += fix_duplicate_api_version(sync_ops_path, verbose)

        # Fix duplicate api_version in async operations
        async_ops_path = generated_version_path / "aio" / "operations" / "_operations.py"
        total_fixes += fix_duplicate_api_version(async_ops_path, verbose)

        if total_fixes > 0:
            print_green(f"  ✓ Fixed {total_fixes} total duplicate api_version occurrences")
        else:
            print_green("  ✓ No duplicate api_version bugs found (may be fixed in newer emitter)")

        # =====================================================================
        # STEP 6: Copy restclient to target location
        # =====================================================================
        step_banner(6, "Copying restclient to target location")

        print_blue(f"  Source: {generated_version_path}")
        print_blue(f"  Target: {target_restclient_path}")

        # Remove existing target if it exists
        if target_restclient_path.exists():
            print_yellow(f"  Removing existing directory: {target_restclient_path}")
            shutil.rmtree(target_restclient_path)

        # Copy the generated restclient
        shutil.copytree(generated_version_path, target_restclient_path)

        print_green(f"  ✓ Restclient copied to {target_restclient_path}")

        # =====================================================================
        # STEP 7: Summary
        # =====================================================================
        step_banner(7, "Summary")

        # Count files
        py_files = list(target_restclient_path.rglob("*.py"))
        print_green(f"  ✓ Generated {len(py_files)} Python files")
        print_green(f"  ✓ Restclient location: {target_restclient_path}")
        print()
        print_green("  ✓ Regeneration completed successfully!")
        print()
        print_blue("  Next steps:")
        print_blue("    1. Review the generated code")
        print_blue("    3. Commit the changes")

    finally:
        # =====================================================================
        # Cleanup temp directory
        # =====================================================================
        print()
        print_blue(f"  Cleaning up temp directory: {temp_dir}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        print_green("  ✓ Temp directory cleaned up")


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Regenerate restclient from TypeSpec definitions",
        epilog="Example: python regenerate_restclient.py -a v2025_10_01_preview --spec-repo C:\\Repos\\azure-rest-api-specs -v",
    )

    parser.add_argument(
        "-a",
        "--api-version",
        required=True,
        help=(
            "Specifies which API version to generate (e.g., v2025_10_01_preview).\n"
            "This should match a version defined in the TypeSpec project."
        ),
    )
    parser.add_argument(
        "--spec-repo",
        type=Path,
        required=True,
        help="Path to the azure-rest-api-specs repository (e.g., C:\\Repos\\azure-rest-api-specs)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", required=False, help="Turn on verbose output")

    args = parser.parse_args()

    regenerate_restclient(args.api_version, args.spec_repo, args.verbose)
