"""Github tools.
"""
from contextlib import contextmanager
import logging
import os
from pathlib import Path
import shutil
import stat
from subprocess import CalledProcessError
import traceback
from urllib.parse import urlsplit, urlunsplit

from github import Github, GithubException
from git import Repo

from .git_tools import (
    clone_to_path as _git_clone_to_path,
    checkout_with_fetch
)

_LOGGER = logging.getLogger(__name__)

class ExceptionContext:  # pylint: disable=too-few-public-methods
    def __init__(self):
        self.comment = None

@contextmanager
def exception_to_github(github_obj_to_comment, summary=""):
    """If any exception comes, log them in the given Github obj.
    """
    context = ExceptionContext()
    try:
        yield context
    except Exception:  # pylint: disable=broad-except
        if summary:
            summary = ": ({})".format(summary)
        error_type = "an unknown error"
        try:
            raise
        except CalledProcessError as err:
            error_type = "a Subprocess error"
            content = "Command: {}\n".format(err.cmd)
            content += "Finished with return code {}\n".format(err.returncode)
            if err.output:
                content += "and output:\n```shell\n{}\n```".format(err.output)
            else:
                content += "and no output"
        except Exception:  # pylint: disable=broad-except
            content = "```python\n{}\n```".format(traceback.format_exc())
        response = "<details><summary>Encountered {}{}</summary><p>\n\n".format(
            error_type,
            summary
        )
        response += content
        response += "\n\n</p></details>"
        context.comment = create_comment(github_obj_to_comment, response)

def user_from_token(gh_token):
    """Get user login from GitHub token"""
    github_con = Github(gh_token)
    return github_con.get_user()

def create_comment(github_object, body):
    """Create a comment, whatever the object is a PR, a commit or an issue.
    """
    try:
        return github_object.create_issue_comment(body)  # It's a PR
    except AttributeError:
        return github_object.create_comment(body)   # It's a commit/issue

def get_comments(github_object):
    """Get a list of comments, whater the object is a PR, a commit or an issue.
    """
    try:
        return github_object.get_issue_comments()  # It's a PR
    except AttributeError:
        return github_object.get_comments()   # It's a commit/issue

def get_files(github_object):
    """Get files from a PR or a commit.
    """
    try:
        return github_object.get_files() # Try as a PR object
    except AttributeError:
        return github_object.files # Try as a commit object

def configure_user(gh_token, repo):
    """git config --global user.email "you@example.com"
       git config --global user.name "Your Name"
    """
    user = user_from_token(gh_token)
    repo.git.config('user.email', user.email or 'adxpysdk@microsoft.com')
    repo.git.config('user.name', user.name or 'SwaggerToSDK Automation')

def get_full_sdk_id(gh_token, sdk_git_id):
    """If the SDK git id is incomplete, try to complete it with user login"""
    if not '/' in sdk_git_id:
        login = user_from_token(gh_token).login
        return '{}/{}'.format(login, sdk_git_id)
    return sdk_git_id

def sync_fork(gh_token, github_repo_id, repo, push=True):
    """Sync the current branch in this fork against the direct parent on Github"""
    if not gh_token:
        _LOGGER.warning('Skipping the upstream repo sync, no token')
        return
    _LOGGER.info('Check if repo has to be sync with upstream')
    github_con = Github(gh_token)
    github_repo = github_con.get_repo(github_repo_id)

    if not github_repo.parent:
        _LOGGER.warning('This repo has no upstream')
        return

    upstream_url = 'https://github.com/{}.git'.format(github_repo.parent.full_name)
    upstream = repo.create_remote('upstream', url=upstream_url)
    upstream.fetch()
    active_branch_name = repo.active_branch.name
    if not active_branch_name in repo.remotes.upstream.refs:
        _LOGGER.info('Upstream has no branch %s to merge from', active_branch_name)
        return
    else:
        _LOGGER.info('Merge from upstream')
    msg = repo.git.rebase('upstream/{}'.format(repo.active_branch.name))
    _LOGGER.debug(msg)
    if push:
        msg = repo.git.push()
        _LOGGER.debug(msg)

def get_or_create_pull(github_repo, title, body, head, base, *, none_if_no_commit=False):
    """Try to create the PR. If the PR exists, try to find it instead. Raises otherwise.

    You should always use the complete head syntax "org:branch", since the syntax is required
    in case of listing.

    if "none_if_no_commit" is set, return None instead of raising exception if the problem
    is that head and base are the same.
    """
    try: # Try to create or get a PR
        return github_repo.create_pull(
            title=title,
            body=body,
            head=head,
            base=base
        )
    except GithubException as err:
        err_message = err.data['errors'][0].get('message', '')
        if err.status == 422 and err_message.startswith('A pull request already exists'):
            _LOGGER.info('PR already exists, get this PR')
            return list(github_repo.get_pulls(
                head=head,
                base=base
            ))[0]
        elif none_if_no_commit and err.status == 422 and err_message.startswith('No commits between'):
            _LOGGER.info('No PR possible since head %s and base %s are the same',
                         head,
                         base)
            return None
        else:
            _LOGGER.warning("Unable to create PR:\n%s", err.data)
            raise
    except Exception as err:
        response = traceback.format_exc()
        _LOGGER.warning("Unable to create PR:\n%s", response)
        raise

def clone_to_path(gh_token, folder, sdk_git_id, branch_or_commit=None, *, pr_number=None):
    """Clone the given repo_id to the folder.

    If PR number is specified fetch the magic branches
    pull/<id>/head or pull/<id>/merge from Github. "merge" is tried first, and fallback to "head".
    Beware that pr_number implies detached head, and then no push is possible.

    If branch is specified, checkout this branch or commit finally.

    :param str branch_or_commit: If specified, switch to this branch/commit.
    :param int pr_number: PR number.
    """
    _LOGGER.info("Clone SDK repository %s", sdk_git_id)
    url_parsing = urlsplit(sdk_git_id)
    sdk_git_id = url_parsing.path
    if sdk_git_id.startswith("/"):
        sdk_git_id = sdk_git_id[1:]

    credentials_part = ''
    if gh_token:
        login = user_from_token(gh_token).login
        credentials_part = '{user}:{token}@'.format(
            user=login,
            token=gh_token
        )
    else:
        _LOGGER.warning('Will clone the repo without writing credentials')

    https_authenticated_url = 'https://{credentials}github.com/{sdk_git_id}.git'.format(
        credentials=credentials_part,
        sdk_git_id=sdk_git_id
    )
    # Clone the repo
    _git_clone_to_path(https_authenticated_url, folder)
    # If this is a PR, do some fetch to improve the number of SHA1 available
    if pr_number:
        try:
            checkout_with_fetch(folder, "pull/{}/merge".format(pr_number))
            return
        except Exception:  # pylint: disable=broad-except
            pass  # Assume "merge" doesn't exist anymore, fetch "head"
        checkout_with_fetch(folder, "pull/{}/head".format(pr_number))
    # If there is SHA1, checkout it. If PR number was given, SHA1 could be inside that PR.
    if branch_or_commit:
        repo = Repo(str(folder))
        repo.git.checkout(branch_or_commit)

def do_pr(gh_token, sdk_git_id, sdk_pr_target_repo_id, branch_name, base_branch, pr_body=""):  # pylint: disable=too-many-arguments
    "Do the PR"
    if not gh_token:
        _LOGGER.info('Skipping the PR, no token found')
        return None
    if not sdk_pr_target_repo_id:
        _LOGGER.info('Skipping the PR, no target repo id')
        return None

    github_con = Github(gh_token)
    sdk_pr_target_repo = github_con.get_repo(sdk_pr_target_repo_id)

    if '/' in sdk_git_id:
        sdk_git_owner = sdk_git_id.split('/')[0]
        _LOGGER.info("Do the PR from %s", sdk_git_owner)
        head_name = "{}:{}".format(sdk_git_owner, branch_name)
    else:
        head_name = branch_name
        sdk_git_repo = github_con.get_repo(sdk_git_id)
        sdk_git_owner = sdk_git_repo.owner.login

    try:
        github_pr = sdk_pr_target_repo.create_pull(
            title='Automatic PR from {}'.format(branch_name),
            body=pr_body,
            head=head_name,
            base=base_branch
        )
    except GithubException as err:
        if err.status == 422 and err.data['errors'][0].get('message', '').startswith('A pull request already exists'):
            matching_pulls = sdk_pr_target_repo.get_pulls(base=base_branch, head=sdk_git_owner+":"+head_name)
            matching_pull = matching_pulls[0]
            _LOGGER.info('PR already exists: %s', matching_pull.html_url)
            return matching_pull
        raise
    _LOGGER.info("Made PR %s", github_pr.html_url)
    return github_pr


def remove_readonly(func, path, _):
    "Clear the readonly bit and reattempt the removal"
    os.chmod(path, stat.S_IWRITE)
    func(path)

@contextmanager
def manage_git_folder(gh_token, temp_dir, git_id, *, pr_number=None):
    """Context manager to avoid readonly problem while cleanup the temp dir.

    If PR number is given, use magic branches "pull" from Github.
    """
    _LOGGER.debug("Git ID %s", git_id)
    if Path(git_id).exists():
        yield git_id
        return  # Do not erase a local folder, just skip here

    # Clone the specific branch
    split_git_id = git_id.split("@")
    branch = split_git_id[1] if len(split_git_id) > 1 else None
    clone_to_path(gh_token, temp_dir, split_git_id[0], branch_or_commit=branch, pr_number=pr_number)
    try:
        yield temp_dir
        # Pre-cleanup for Windows http://bugs.python.org/issue26660
    finally:
        _LOGGER.debug("Preclean Rest folder")
        shutil.rmtree(temp_dir, onerror=remove_readonly)


class GithubLink:
    def __init__(self, gitid, link_type, branch_or_commit, path, token=None):  # pylint: disable=too-many-arguments
        self.gitid = gitid
        self.link_type = link_type
        self.branch_or_commit = branch_or_commit
        self.path = path
        self.token = token

    @classmethod
    def from_string(cls, github_url):
        parsed = urlsplit(github_url)
        netloc = parsed.netloc
        if "@" in netloc:
            token, netloc = netloc.split("@")
        else:
            token = None

        split_path = parsed.path.split("/")
        split_path.pop(0)  # First is always empty
        gitid = split_path.pop(0) + "/" + split_path.pop(0)
        link_type = split_path.pop(0) if netloc != "raw.githubusercontent.com" else "raw"
        branch_or_commit = split_path.pop(0)
        path = "/".join(split_path)
        return cls(gitid, link_type, branch_or_commit, path, token)

    def __repr__(self):
        if self.link_type == "raw":
            netloc = "raw.githubusercontent.com"
            path = "/".join(["", self.gitid, self.branch_or_commit, self.path])
            # If raw and token, needs to be passed with "Authorization: token <token>", so nothing to do here
        else:
            netloc = "github.com" if not self.token else self.token + "@github.com"
            path = "/".join(["", self.gitid, self.link_type, self.branch_or_commit, self.path])
        return urlunsplit(("https", netloc, path, '', ''))

    def as_raw_link(self):
        """Returns a GithubLink to a raw content.
        """
        if self.link_type == "raw":
            return self # Can be discussed if we need an hard copy, or fail
        if self.link_type != "blob":
            raise ValueError("Cannot get a download link from a tree link")
        return self.__class__(
            self.gitid,
            "raw",
            self.branch_or_commit,
            self.path,
            self.token
        )

class DashboardCommentableObject:  # pylint: disable=too-few-public-methods
    def __init__(self, issue_or_pr, header):
        self._issue_or_pr = issue_or_pr
        self._header = header

    def create_comment(self, text):
        """Mimic issue API, so we can use it everywhere.
        Return dashboard comment.
        """
        return DashboardComment.get_or_create(self._issue_or_pr, self._header, text)

class DashboardComment:
    def __init__(self, github_comment, header):
        self.github_comment = github_comment
        self._header = header

    @classmethod
    def get_or_create(cls, issue, header, text=None):
        """Get or create the dashboard comment in this issue.
        """
        for comment in get_comments(issue):
            try:
                if comment.body.splitlines()[0] == header:
                    obj = cls(comment, header)
                    break
            except IndexError: # The comment body is empty
                pass
        # Hooooooo, no dashboard comment, let's create one
        else:
            comment = create_comment(issue, header)
            obj = cls(comment, header)
        if text:
            obj.edit(text)
        return obj

    def edit(self, text):
        self.github_comment.edit(self._header+"\n"+text)

    @property
    def body(self):
        return self.github_comment.body[len(self._header+"\n"):]

    def delete(self):
        self.github_comment.delete()
