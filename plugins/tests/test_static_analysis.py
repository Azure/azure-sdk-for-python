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
        if subprocess.getstatusoutput(argv)[0] == 16 or subprocess.getstatusoutput(argv)[0] == 30:
            raise PylintError

