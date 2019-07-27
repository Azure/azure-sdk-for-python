import subprocess

def test_run_pylint():
    argv = [
        'pylint', '--rcfile', '../../../pylintrc', 'azure.core'
    ]

    result = subprocess.check_call(argv)

def test_run_black():
    argv = [
        'black', 'azure', '--check'
    ]

    result = subprocess.check_call(argv)

def test_mypy():
    argv = [
        'mypy', 'azure/core'
    ]
    result = subprocess.check_call(argv)