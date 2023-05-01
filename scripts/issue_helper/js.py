from common import Common

_JS_OWNER = {'colawwj', 'qiaozha', 'lirenhe', 'MaryGao', 'github-actions[bot]'}
_JS_REPO = 'Azure/azure-sdk-for-js'
_FILE_OUT_NAME_JS = 'sdk_issue_js.md'


def js_process() -> None:
    instance = Common(_JS_OWNER, _JS_REPO, _FILE_OUT_NAME_JS)
    instance.run()
