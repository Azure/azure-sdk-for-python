"""Bootstrap Python package installers before installing other dependencies."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Optional


PIP_VERSION = "26.2.2"
UV_VERSION = "0.13.4"
PIP_WHEEL_SHA256 = "fd7f4dfa8190e014013b9f08f3e973f4e4c26ffd179a204895533a7254813a70"

_INSPECT = """
import json
import sys
from importlib.metadata import PackageNotFoundError, version
try:
    installed = version(sys.argv[1])
except PackageNotFoundError:
    installed = None
print(json.dumps({"python": list(sys.version_info[:2]), "version": installed}))
"""


def _at_least(installed: Optional[str], required: str) -> bool:
    if installed is None:
        return False
    match = re.fullmatch(r"(\d+)\.(\d+)(?:\.(\d+))?", installed)
    if match is None:
        return False
    return tuple(int(part or 0) for part in match.groups()) >= tuple(int(part) for part in required.split("."))


def _inspect(python_executable: str, distribution: str) -> dict:
    return json.loads(subprocess.check_output([python_executable, "-c", _INSPECT, distribution], text=True))


def ensure_pip(python_executable: str = sys.executable) -> None:
    """Upgrade missing or older pip, including in newly seeded or reused environments."""
    installed = _inspect(python_executable, "pip")
    if installed["python"] < [3, 10]:
        raise RuntimeError(f"pip {PIP_VERSION} requires Python 3.10 or newer: {python_executable}")
    if not _at_least(installed["version"], PIP_VERSION):
        if installed["version"] is None:
            subprocess.check_call([python_executable, "-m", "ensurepip", "--upgrade"])
        # Verify the wheel even when the bootstrap pip's certificate bundle is outdated.
        # Use the configured index/find-links rather than bypassing isolated feeds.
        with tempfile.TemporaryDirectory(prefix="pip-bootstrap-") as directory:
            requirements = Path(directory) / "requirements.txt"
            requirements.write_text(f"pip=={PIP_VERSION} --hash=sha256:{PIP_WHEEL_SHA256}\n", encoding="ascii")
            subprocess.check_call(
                [
                    python_executable,
                    "-m",
                    "pip",
                    "--disable-pip-version-check",
                    "install",
                    "--upgrade",
                    "--only-binary=:all:",
                    "--no-deps",
                    "--require-hashes",
                    "-r",
                    str(requirements),
                ]
            )
        installed = _inspect(python_executable, "pip")
        if not _at_least(installed["version"], PIP_VERSION):
            raise RuntimeError(f"Expected pip >= {PIP_VERSION} in {python_executable}, found {installed['version']}")
    print(f"{python_executable}: pip {installed['version']}", flush=True)


def ensure_uv(python_executable: str = sys.executable) -> None:
    """Install the current pinned uv using an already secured pip."""
    ensure_pip(python_executable)
    installed = _inspect(python_executable, "uv")
    if not _at_least(installed["version"], UV_VERSION):
        subprocess.check_call([python_executable, "-m", "pip", "install", "--upgrade", f"uv=={UV_VERSION}"])
        installed = _inspect(python_executable, "uv")
        if not _at_least(installed["version"], UV_VERSION):
            raise RuntimeError(f"Expected uv >= {UV_VERSION} in {python_executable}, found {installed['version']}")
    subprocess.check_call([python_executable, "-m", "uv", "--version"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", default=sys.executable, help="Python executable of the target environment.")
    parser.add_argument("--uv", action="store_true", help="Bootstrap uv as well as pip.")
    args = parser.parse_args()
    if args.uv:
        ensure_uv(args.python)
    else:
        ensure_pip(args.python)


if __name__ == "__main__":
    main()
