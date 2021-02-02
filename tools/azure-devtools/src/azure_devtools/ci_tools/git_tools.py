"""Pure git tools for managing local folder Git.
"""
import logging

from git import Repo, GitCommandError

_LOGGER = logging.getLogger(__name__)

def checkout_and_create_branch(repo, name):
    """Checkout branch. Create it if necessary"""
    local_branch = repo.branches[name] if name in repo.branches else None
    if not local_branch:
        if name in repo.remotes.origin.refs:
            # If origin branch exists but not local, git.checkout is the fatest way
            # to create local branch with origin link automatically
            msg = repo.git.checkout(name)
            _LOGGER.debug(msg)
            return
        # Create local branch, will be link to origin later
        local_branch = repo.create_head(name)
    local_branch.checkout()

def checkout_create_push_branch(repo, name):
    """Checkout this branch. Create it if necessary, and push it to origin.
    """
    try:
        repo.git.checkout(name)
        _LOGGER.info("Checkout %s success", name)
    except GitCommandError:
        _LOGGER.info("Checkout %s was impossible (branch does not exist). Creating it and push it.", name)
        checkout_and_create_branch(repo, name)
        repo.git.push('origin', name, set_upstream=True)


def do_commit(repo, message_template, branch_name, hexsha):
    "Do a commit if modified/untracked files"
    repo.git.add(repo.working_tree_dir)

    if not repo.git.diff(staged=True):
        _LOGGER.warning('No modified files in this Autorest run')
        return False

    checkout_and_create_branch(repo, branch_name)
    msg = message_template.format(hexsha=hexsha)
    commit = repo.index.commit(msg)
    _LOGGER.info("Commit done: %s", msg)
    return commit.hexsha

def get_repo_hexsha(git_folder):
    """Get the SHA1 of the current repo"""
    repo = Repo(str(git_folder))
    if repo.bare:
        not_git_hexsha = "notgitrepo"
        _LOGGER.warning("Not a git repo, SHA1 used will be: %s", not_git_hexsha)
        return not_git_hexsha
    hexsha = repo.head.commit.hexsha
    _LOGGER.info("Found REST API repo SHA1: %s", hexsha)
    return hexsha

def checkout_with_fetch(git_folder, refspec, repository="origin"):
    """Fetch the refspec, and checkout FETCH_HEAD.
    Beware that you will ne in detached head mode.
    """
    _LOGGER.info("Trying to fetch and checkout %s", refspec)
    repo = Repo(str(git_folder))
    repo.git.fetch(repository, refspec)  # FETCH_HEAD should be set
    repo.git.checkout("FETCH_HEAD")
    _LOGGER.info("Fetch and checkout success for %s", refspec)

def clone_to_path(https_authenticated_url, folder, branch_or_commit=None):
    """Clone the given URL to the folder.

    :param str branch_or_commit: If specified, switch to this branch. Branch must exist.
    """
    _LOGGER.info("Cloning repo")
    repo = Repo.clone_from(https_authenticated_url, str(folder))
    # Do NOT clone and set branch at the same time, since we allow branch to be a SHA1
    # And you can't clone a SHA1
    if branch_or_commit:
        _LOGGER.info("Checkout branch_or_commit %s", branch_or_commit)
        repo.git.checkout(branch_or_commit)

    _LOGGER.info("Clone success")

def get_files_in_commit(git_folder, commit_id="HEAD"):
    """List of files in HEAD commit.
    """
    repo = Repo(str(git_folder))
    output = repo.git.diff("--name-only", commit_id+"^", commit_id)
    return output.splitlines()

def get_diff_file_list(git_folder):
    """List of unstaged files.
    """
    repo = Repo(str(git_folder))
    output = repo.git.diff("--name-only")
    return output.splitlines()
	
def get_add_diff_file_list(git_folder):
    """List of new files.
    """
    repo = Repo(str(git_folder))
    repo.git.add("sdk")
    output = repo.git.diff("HEAD", "--name-only")
    return output.splitlines()
