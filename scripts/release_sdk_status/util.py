import os
from pathlib import Path


def _find_certificate():
    print("*** path:", os.getcwd())
    devcert_path = Path('eng/common/testproxy/dotnet-devcert.crt')
    with open(devcert_path, 'r') as fr:
        return fr.read()


def add_certificate(file: str):
    certification = _find_certificate()
    with open(file, 'a+') as f:
        f.seek(0, 0)
        f.write(certification)
