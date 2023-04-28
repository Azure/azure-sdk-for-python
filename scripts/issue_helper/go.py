from common import Common

_GO_OWNER = {'ArcturusZhang', 'lirenhe', 'Alancere', 'github-actions[bot]'}
_GO_REPO = 'Azure/azure-sdk-for-go'
_FILE_OUT_NAME_GO = 'sdk_issue_go.md'


def go_process() -> None:
    instance = Common(_GO_OWNER, _GO_REPO, _FILE_OUT_NAME_GO)
    instance.run()
