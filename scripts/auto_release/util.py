from pathlib import Path


def _find_certificate():
    devcert_path = Path('eng/common/testproxy/dotnet-devcert.crt')
    with open(devcert_path, 'r') as fr:
        return fr.read()


def add_certificate():
    certification = _find_certificate()
    cacert_path = Path('../venv-sdk/lib/python3.8/site-packages/certifi/cacert.pem')
    with open(cacert_path, 'a+') as f:
        f.seek(0, 0)
        f.write(certification)
