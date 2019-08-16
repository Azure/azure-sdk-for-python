import subprocess

class PylintError(BaseException):
    pass

def test_run_pylint():
    try:
        argv = [
            'pylint', '--rcfile="../../../pylintrc"', '../../../sdk/core/azure-core/azure/core'
        ]

        result = subprocess.check_call(argv)
    except subprocess.CalledProcessError:
        raise PylintError

