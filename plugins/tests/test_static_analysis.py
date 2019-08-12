import subprocess

class PylintError(BaseException):
    pass

def test_run_pylint():
    try:
        argv = [
            'pylint', '../../sdk/core/azure-core/azure/core'
        ]

        result = subprocess.check_call(argv)
    except subprocess.CalledProcessError:
        raise PylintError
        # if subprocess.getstatusoutput(argv)[0] in [16, 28, 30]:
        #     raise PylintError

