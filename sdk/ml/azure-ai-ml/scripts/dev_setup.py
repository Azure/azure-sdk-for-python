# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import shutil
import subprocess

PACKAGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REPO_ROOT = os.path.abspath(os.path.join(PACKAGE_ROOT, '..', "..", ".."))


def copy_pre_commit_hook():
    src_pth = os.path.join(PACKAGE_ROOT, "scripts", "templates", "pre-commit-config.yaml")
    dst_pth = os.path.join(REPO_ROOT, ".pre-commit-config.yaml")
    print("Copying files from {} to {}".format(src_pth, dst_pth))
    shutil.copy(
        src_pth,
        dst_pth
    )


def enable_pre_commit_hook():
    print("Enabling pre-commit hook")

    subprocess.run(["pre-commit", "install"], check=True)
    subprocess.run(["pre-commit", "run", "--all-files"], check=True)


def __main__():
    copy_pre_commit_hook()
    enable_pre_commit_hook()


if __name__ == "__main__":
    __main__()
