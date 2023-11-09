# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Functions for interacting with Git."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import git

from azure.ai.resources.index._utils.azureml import get_secret_from_workspace
from azure.ai.resources.index._utils.logging import get_logger

logger = get_logger("utils.git")
git_logger = get_logger("git_clone")


class GitCloneProgress(git.remote.RemoteProgress):
    """A progress handler for git clone operations."""

    def update(self, op_code, cur_count, max_count=None, message=""):
        """Update the progress of the git clone operation."""
        if message:
            git_logger.info(message.strip())

        if op_code & git.remote.RemoteProgress.BEGIN:
            git_logger.info("Begin clone")
        elif op_code & git.remote.RemoteProgress.END:
            git_logger.info("Clone complete")
        elif op_code & git.remote.RemoteProgress.COUNTING:
            git_logger.info("Received %d/%d objects" % (cur_count, max_count))


@dataclass
class GitRepoBranch:
    """A git repository and branch."""

    git_url: str
    branch_name: Optional[str] = None


def parse_git_url(git_url: str) -> GitRepoBranch:
    """Parse a git url into a GitRepoBranch."""
    import re

    git_repo_pattern = re.compile(r"(.*\.git$)|(https:\/\/github\.com.*)\/blob\/(.*)|(https:\/\/github\.com.*(?!git)$)")
    match = git_repo_pattern.match(git_url)
    if match is None:
        # Try the original to see if git likes it
        return GitRepoBranch(git_url=git_url)
    elif match.group(1) is not None:
        # Has .git suffix, leave as is
        return GitRepoBranch(git_url=match.group(0))
    elif match.group(2) is not None:
        # Missing .git suffix, and references a specific branch
        return GitRepoBranch(git_url=f"{match.group(2)}.git", branch_name=match.group(3))
    elif match.group(4) is not None:
        # Missing .git suffix, and references the default branch
        return GitRepoBranch(git_url=f"{match.group(4)}.git")

    raise RuntimeError("git_url regex matched but none of the groups matched?")


def clone_repo(git_url: str, local_path: Path, branch: Optional[str] = None, authentication: Optional[dict] = None):
    """Clone a git repository to a local path, optionally checking out a branch."""
    logger.info(f"Cloning {git_url} to {local_path}")

    git_repo_branch = parse_git_url(git_url)
    if branch is not None:
        git_repo_branch.branch_name = branch

    if authentication is not None:
        git_repo_branch.git_url = git_repo_branch.git_url.replace("https://", f'https://{authentication["username"]}:{authentication["password"]}@')

    logger.info(f"Cloning with depth={1 if git_repo_branch.branch_name is None else None}")
    try:
        repo = git.Repo.clone_from(git_repo_branch.git_url, local_path, progress=GitCloneProgress(), depth=1 if git_repo_branch.branch_name is None else None)
    except git.exc.GitError as e:
        logger.error(f"Failed to clone to {local_path}\ngit stdout: {e.stdout}\ngit stderr: {e.stderr}")

        raise e
    except Exception as e:
        logger.error(f"Failed to clone to {local_path}: {e}")

        raise e
    if git_repo_branch.branch_name is not None and git_repo_branch.branch_name != "":
        logger.info("fetch --all")
        repo.git.fetch("--all")
        logger.info(f"checkout {git_repo_branch.branch_name}")
        repo.git.checkout(git_repo_branch.branch_name)

    logger.info(f'Cloned branch "{repo.active_branch}" at commit: {repo.head.commit.hexsha}')


def get_keyvault_authentication(authentication_key_prefix: str):
    """Get the username and password for a keyvault authentication key""."""
    username = get_secret_from_workspace(f"{authentication_key_prefix}-USER")
    password = get_secret_from_workspace(f"{authentication_key_prefix}-PASS")
    return {"username": username, "password": password}
