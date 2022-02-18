from common import Common

_PYTHON_OWNER = {'msyyc', 'BigCat20196', 'Wzb123456789', 'kazrael2119'}
_PYTHON_REPO = 'Azure/azure-sdk-for-python'
_FILE_OUT_NAME_PYTHON = 'sdk_issue_python.md'

def python_process() -> None:
    instance = Common(_PYTHON_OWNER, _PYTHON_REPO, _FILE_OUT_NAME_PYTHON)
    instance.run()
