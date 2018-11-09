import os
import sys

from github import Github, GithubException

LABEL_COLOUR = "e99695"


def get_repo(repo_name):
    con = Github(os.environ["GH_TOKEN"])
    repo = con.get_repo(repo_name)
    repo.name  # Force checking if repo exists, otherwise "get_repo" does nothing
    return repo


def create_label(repo, label):
    print(f"Adding label {label}")
    try:
        repo.create_label(label, LABEL_COLOUR)
        print(f"-> Created label {label}")
    except GithubException as err:
        err_code = err.data['errors'][0].get('code', '')
        if err.status == 422 and err_code == "already_exists":
            print(f"-> Label {label} already exists")
            return
        raise

def do(repo_name, label_filepath):
    print(f"Getting repo {repo_name}")
    repo = get_repo(repo_name)

    print("Adding labels to repo")
    with open(label_filepath, "r") as fd:
        for label in fd.read().splitlines():
            create_label(repo, label)


if __name__ == "__main__":
    do(sys.argv[1], sys.argv[2])