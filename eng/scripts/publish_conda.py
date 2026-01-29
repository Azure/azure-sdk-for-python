"""
Publish conda packages to Anaconda.org.

Usage:
    python publish_conda.py --package-dir ./conda --user Microsoft
    python publish_conda.py --package-dir ./conda --user Microsoft --dry-run
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from ci_tools.logging import logger, configure_logging


def verify_authentication() -> bool:
    """Verify that the Anaconda API token is valid."""
    if not os.environ.get("ANACONDA_API_TOKEN"):
        logger.error("ANACONDA_API_TOKEN environment variable is not set")
        return False

    result = subprocess.run(
        ["anaconda", "whoami"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.error("Invalid or expired Anaconda API token")
        logger.error(result.stderr)
        return False

    logger.info("Anaconda authentication successful")
    logger.info(result.stdout.strip())
    return True


def find_packages(package_dir: Path) -> list[Path]:
    """Find all built conda artifacts in the given directory."""
    packages = []
    for pattern in ["**/*.tar.bz2", "**/*.conda"]:
        packages.extend(package_dir.glob(pattern))
    return sorted(packages)


def upload_package(
    package_path: Path,
    user: str,
    max_retries: int = 3,
    retry_delay: float = 5.0,
    dry_run: bool = False,
) -> bool:
    """
    Upload a single package to Anaconda.org with retry logic.

    Returns True if successful, False otherwise.
    """
    for attempt in range(1, max_retries + 1):
        logger.info(
            f"Uploading {package_path.name} (attempt {attempt}/{max_retries})..."
        )

        if dry_run:
            logger.info(f"[DRY RUN] Would upload: {package_path}")
            return True

        # result = subprocess.run(
        #     [
        #         "anaconda",
        #         "upload",
        #         "--user",
        #         user,
        #         "--skip-existing",
        #         str(package_path),
        #         "--private",  # TODO remove after testing is complete
        #     ],
        #     capture_output=True,
        #     text=True,
        # )

        # if result.returncode == 0:
        #     logger.info(f"Successfully uploaded {package_path.name}")
        #     if result.stdout:
        #         logger.debug(result.stdout)
        #     return True

        # logger.warning(f"Attempt {attempt} failed: {result.stderr.strip()}")

        # if attempt < max_retries:
        #     logger.info(f"Retrying in {retry_delay} seconds...")
        #     time.sleep(retry_delay)

    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Publish conda packages to Anaconda.org"
    )
    parser.add_argument(
        "--package-dir",
        type=Path,
        required=True,
        help="Directory containing conda packages to upload",
    )
    parser.add_argument(
        "--user",
        type=str,
        required=True,
        help="Anaconda.org username or organization to upload to",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List packages that would be uploaded without actually uploading",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum number of upload retries per package (default: 3)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()
    configure_logging(args)

    if args.dry_run:
        logger.info("=== DRY RUN MODE - No packages will be uploaded ===")

    # Verify authentication
    if not verify_authentication():
        return 1

    # Find packages
    if not args.package_dir.exists():
        logger.error(f"Package directory does not exist: {args.package_dir}")
        return 1

    packages = find_packages(args.package_dir)

    if not packages:
        logger.error(f"No conda packages found in {args.package_dir}")
        return 1

    logger.info(f"Found {len(packages)} packages to upload:")
    for pkg in packages:
        logger.info(f"  - {pkg.name}")

    # Upload packages
    failed = []
    for package in packages:
        success = upload_package(
            package,
            user=args.user,
            max_retries=args.max_retries,
            dry_run=args.dry_run,
        )
        if not success:
            failed.append(package.name)

    # Report results
    if failed:
        logger.error(f"Failed to upload {len(failed)} package(s):")
        for name in failed:
            logger.error(f"  - {name}")
        return 1

    logger.info(f"Successfully uploaded all {len(packages)} packages!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
