#!/usr/bin/env python

from __future__ import annotations

from common import append_github_output, env_path, require_env, run, write_lines, REPO_ROOT


def main() -> int:
    base_ref = require_env("API_MD_BASE_REF")
    packages_file = env_path("API_MD_PACKAGES_FILE", ".artifacts/affected_package_dirs.txt")
    changed_file = env_path("API_MD_CHANGED_FILE", ".artifacts/changed_package_dirs.txt")

    run(["git", "fetch", "--no-tags", "--depth=1", "origin", base_ref])
    diff = run(["git", "diff", "--name-only", f"origin/{base_ref}...HEAD"], capture=True).stdout

    changed_dirs: set[str] = set()
    for file_path in diff.splitlines():
        parts = file_path.strip().split("/")
        if len(parts) < 3 or parts[0] != "sdk":
            continue
        changed_dirs.add("/".join(parts[:3]))

    write_lines(changed_file, sorted(changed_dirs))

    affected: list[str] = []
    for package_dir in sorted(changed_dirs):
        pkg_path = REPO_ROOT / package_dir
        if (pkg_path / "pyproject.toml").exists() or (pkg_path / "setup.py").exists():
            affected.append(package_dir)

    write_lines(packages_file, affected)
    append_github_output("count", len(affected))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
