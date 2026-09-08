import importlib.util
import os

import pytest

# warm_cfs_feed.py is a standalone script under eng/scripts, not an installed
# module, so load it by path. Its imports (ci_tools, packaging) are available
# because these tests run with azure-sdk-tools installed.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
_SCRIPT_PATH = os.path.join(_REPO_ROOT, "eng", "scripts", "warm_cfs_feed.py")

_spec = importlib.util.spec_from_file_location("warm_cfs_feed", _SCRIPT_PATH)
warm_cfs_feed = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(warm_cfs_feed)


def test_abi_for_python():
    assert warm_cfs_feed._abi_for_python("3.12") == "cp312"
    assert warm_cfs_feed._abi_for_python("3.9") == "cp39"


def test_parse_csv_option_defaults_and_override():
    assert warm_cfs_feed._parse_csv_option(None, ["3.10", "3.11"]) == ["3.10", "3.11"]
    assert warm_cfs_feed._parse_csv_option("3.12, 3.13 ,", ["x"]) == ["3.12", "3.13"]


def test_classify_downloaded_separates_universal_from_binary(tmp_path):
    for filename in [
        "mypy-1.19.1-cp312-cp312-win_amd64.whl",  # platform-specific wheel
        "cryptography-44.0.3-cp39-abi3-manylinux2014_x86_64.whl",  # platform-specific wheel
        "six-1.16.0-py2.py3-none-any.whl",  # universal wheel
        "jsondiff-1.2.0.tar.gz",  # sdist only
        "not-a-package.txt",  # ignored
    ]:
        (tmp_path / filename).write_text("", encoding="utf-8")

    universal, needs_cross_target = warm_cfs_feed.classify_downloaded(str(tmp_path))

    assert ("six", "1.16.0") in universal
    assert ("six", "1.16.0") not in needs_cross_target
    assert ("mypy", "1.19.1") in needs_cross_target
    assert ("cryptography", "44.0.3") in needs_cross_target
    assert ("jsondiff", "1.2.0") in needs_cross_target


def test_classify_downloaded_universal_wins_over_sdist(tmp_path):
    # A package that ships both a universal wheel and an sdist is fully covered.
    (tmp_path / "click-8.1.7-py3-none-any.whl").write_text("", encoding="utf-8")
    (tmp_path / "click-8.1.7.tar.gz").write_text("", encoding="utf-8")

    universal, needs_cross_target = warm_cfs_feed.classify_downloaded(str(tmp_path))

    assert ("click", "8.1.7") in universal
    assert ("click", "8.1.7") not in needs_cross_target
