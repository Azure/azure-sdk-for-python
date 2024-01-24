import os


def discover_repo_root(input_repo: str = None):
    """
    Resolves the root of the repository given a current working directory. This function should be used if a target repo argument is not provided.
    If the value of input_repo has value, that will supplant the path ascension logic.
    """

    if input_repo is not None:
        if os.path.exists(input_repo):
            return input_repo

    current_dir: str = os.getcwd()

    while current_dir is not None and not (os.path.dirname(current_dir) == current_dir):
        if os.path.exists(os.path.join(current_dir, ".git")):
            return current_dir
        else:
            current_dir = os.path.dirname(current_dir)

    raise Exception(
        "Commands invoked against azure-sdk-tooling should either be run from within the repo directory or provide --repo_root argument that directs at one."
    )


def get_artifact_directory(input_directory: str = None) -> str:
    """
    Resolves the root of an artifact directory that the \"sdk_build\" action will output to!
    """
    if input_directory is not None:
        if not os.path.exists(input_directory):
            os.makedirs(input_directory)
        return input_directory
    return os.getenv("SDK_ARTIFACT_DIRECTORY", os.path.join(discover_repo_root(), ".artifacts"))


def get_log_directory(input_directory: str = None) -> str:
    """
    Resolves the location of the log directory.
    """
    if input_directory is not None:
        if not os.path.exists(input_directory):
            os.makedirs(input_directory)
        return input_directory
    return os.getenv("SDK_LOG_DIRECTORY", os.path.join(discover_repo_root(), ".logs"))


def in_ci() -> int:
    # TF_BUILD is set to `true` on azure devops agents, returns 1
    # CI is set to `true` on github actions agents, return 2
    # 0 otherwise
    if os.getenv("TF_BUILD", None):
        return 1

    if os.getenv("CI", None):
        return 2

    return 0


def in_public() -> int:
    # Returns 3 if the build originates from a pull request
    # 0 otherwise
    if os.getenv("BUILD_REASON") == "PullRequest" or os.getenv("GITHUB_EVENT_NAME") == "pull_request":
        return 3

    return 0


DEV_BUILD_IDENTIFIER = os.getenv("SDK_DEV_BUILD_IDENTIFIER", "a")
DEFAULT_BUILD_ID = os.getenv("GITHUB_RUN_ID", os.getenv("BUILD.BUILDID", os.getenv("SDK_BUILD_ID", "20220101.1")))
