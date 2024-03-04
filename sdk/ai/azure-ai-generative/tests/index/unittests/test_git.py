import pytest
from azure.ai.generative.index._utils.git import GitRepoBranch, parse_git_url


@pytest.mark.parametrize("git_url_and_result", [
    ("https://github.com/org/repo/blob/master", GitRepoBranch(git_url="https://github.com/org/repo.git", branch_name="master")),
    ("https://github.com/MicrosoftDocs/azure-docs", GitRepoBranch(git_url="https://github.com/MicrosoftDocs/azure-docs.git")),
    ("https://github.com/MicrosoftDocs/azure-docs.git", GitRepoBranch(git_url="https://github.com/MicrosoftDocs/azure-docs.git")),
    ("https://msdata.visualstudio.com/DefaultCollection/Vienna/_git/AzureMlCli", GitRepoBranch(git_url="https://msdata.visualstudio.com/DefaultCollection/Vienna/_git/AzureMlCli"))
])
def test_parse_git_url(git_url_and_result):
    assert parse_git_url(git_url_and_result[0]) == git_url_and_result[1]