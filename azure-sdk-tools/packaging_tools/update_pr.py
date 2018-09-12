import argparse
import logging
import os
from pathlib import Path
import tempfile

from azure_devtools.ci_tools.git_tools import (
    do_commit,
)
from azure_devtools.ci_tools.github_tools import (
    manage_git_folder,
    configure_user
)

from git import Repo
from github import Github

from . import build_packaging_by_package_name


_LOGGER = logging.getLogger(__name__)


def update_pr(gh_token, repo_id, pr_number):
    from github import Github
    con = Github(gh_token)
    repo = con.get_repo(repo_id)
    sdk_pr = repo.get_pull(pr_number)
    # "get_files" of Github only download the first 300 files. Might not be enough.
    package_names = {f.filename.split('/')[0] for f in sdk_pr.get_files() if f.filename.startswith("azure")}

    # Get PR branch to push
    head_repo = sdk_pr.head.repo.full_name
    head_branch = sdk_pr.head.ref
    branched_index = "{}@{}".format(head_repo, head_branch)

    with tempfile.TemporaryDirectory() as temp_dir, \
            manage_git_folder(gh_token, Path(temp_dir) / Path("sdk"), branched_index) as sdk_folder:

        sdk_repo = Repo(str(sdk_folder))
        configure_user(gh_token, sdk_repo)

        for package_name in package_names:
            # Rebuild packaging
            build_packaging_by_package_name(package_name, sdk_folder, build_conf=True)
            # Commit that
            do_commit(
                sdk_repo,
                "Packaging update of {}".format(package_name),
                head_branch,
                None # Unused
            )
        # Push all commits at once
        sdk_repo.git.push('origin', head_branch, set_upstream=True)

def update_pr_main():
    """Main method"""

    parser = argparse.ArgumentParser(
        description='Build package.',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--pr-number', '-p',
                        dest='pr_number', type=int, required=True,
                        help='PR number')
    parser.add_argument('--repo', '-r',
                        dest='repo_id', default="Azure/azure-sdk-for-python",
                        help='Repo id. [default: %(default)s]')
    parser.add_argument("-v", "--verbose",
                        dest="verbose", action="store_true",
                        help="Verbosity in INFO mode")
    parser.add_argument("--debug",
                        dest="debug", action="store_true",
                        help="Verbosity in DEBUG mode")

    args = parser.parse_args()
    main_logger = logging.getLogger()
    if args.verbose or args.debug:
        logging.basicConfig()
        main_logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    update_pr(
        os.environ.get("GH_TOKEN", None),
        args.repo_id,
        int(args.pr_number),
    )

if __name__ == "__main__":
    update_pr_main()
