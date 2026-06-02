#!/usr/bin/env python

from __future__ import annotations

import sys
from pathlib import Path

from common import GENERATE_API_SCRIPT, env_path, read_lines, run


def main() -> int:
    packages_file = env_path("API_MD_PACKAGES_FILE", ".artifacts/affected_package_dirs.txt")
    packages = read_lines(packages_file)
    if not packages:
        return 0

    for pkg_dir in packages:
        package_name = Path(pkg_dir).name
        print(f"Generating API.md for {package_name}")
        run([sys.executable, str(GENERATE_API_SCRIPT), package_name])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
