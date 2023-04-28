from common import Common

_JAVA_OWNER = {'weidongxu-microsoft', 'haolingdong-msft', 'XiaofeiCao', 'github-actions[bot]'}
_JAVA_REPO = 'Azure/azure-sdk-for-java'
_FILE_OUT_NAME_JAVA = 'sdk_issue_java.md'


def java_process() -> None:
    instance = Common(_JAVA_OWNER, _JAVA_REPO, _FILE_OUT_NAME_JAVA)
    instance.run()
