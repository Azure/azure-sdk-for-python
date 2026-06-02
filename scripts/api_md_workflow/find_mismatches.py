#!/usr/bin/env python

from __future__ import annotations

from pathlib import Path

from common import append_github_output, env_path, read_lines, run, write_lines


def main() -> int:
    packages_file = env_path("API_MD_PACKAGES_FILE", ".artifacts/affected_package_dirs.txt")
    out_file = env_path("API_MD_MISMATCHES_FILE", ".artifacts/mismatched_api_files.txt")
    packages = read_lines(packages_file)

    mismatches: list[str] = []
    for pkg_dir in packages:
        api_file = f"{pkg_dir}/API.md"
        api_path = Path(api_file)

        # Enforce that each affected package has a committed API.md file.
        if not api_path.is_file():
            mismatches.append(api_file)
            continue

        tracked_result = run(["git", "ls-files", "--error-unmatch", "--", api_file], check=False)
        if tracked_result.returncode != 0:
            mismatches.append(api_file)
            continue

        diff_result = run(["git", "diff", "--quiet", "--", api_file], check=False)
        if diff_result.returncode != 0:
            mismatches.append(api_file)

    write_lines(out_file, mismatches)
    append_github_output("mismatch_count", len(mismatches))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
