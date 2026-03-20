import os
import tempfile
import shutil
from unittest.mock import patch

from ci_tools.build import discover_targeted_packages, build_packages, build

from azpysdk.main import build_parser
from azpysdk.build_tests import build_tests
from azpysdk.create_samples import create_samples

repo_root = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
integration_folder = os.path.join(os.path.dirname(__file__), "integration")
pyproject_folder = os.path.join(integration_folder, "scenarios", "pyproject_build_config")
pyproject_file = os.path.join(integration_folder, "scenarios", "pyproject_build_config", "pyproject.toml")


def test_build_core():
    assert callable(build)


def test_discover_targeted_packages():
    assert callable(discover_targeted_packages)


def test_build_packages():
    assert callable(build_packages)


# ---------------------------------------------------------------------------
# build_tests subcommand tests
# ---------------------------------------------------------------------------

def test_build_tests_registers_subcommand():
    parser = build_parser()
    # verify that "build-tests" is a recognised subcommand
    args = parser.parse_args(["build-tests"])
    assert args.command == "build-tests"


def test_build_tests_no_op_on_missing_target():
    checker = build_tests()
    with patch.object(checker, "get_targeted_directories", return_value=[]):
        import argparse
        args = argparse.Namespace(command="build-tests", isolate=False, target="**", service=None)
        result = checker.run(args)
    assert result == 0


# ---------------------------------------------------------------------------
# create_samples subcommand tests
# ---------------------------------------------------------------------------

def test_create_samples_registers_subcommand():
    parser = build_parser()
    args = parser.parse_args(["create-samples"])
    assert args.command == "create-samples"


def _make_fake_parsed_setup(tmp_dir: str):
    """Return a minimal object that looks like a ParsedSetup."""
    class _FakeParsed:
        folder = tmp_dir
        name = "azure-fake-package"
    return _FakeParsed()


def test_create_samples_creates_scaffold():
    tmp_dir = tempfile.mkdtemp()
    try:
        checker = create_samples()
        fake = _make_fake_parsed_setup(tmp_dir)
        with patch.object(checker, "get_targeted_directories", return_value=[fake]):
            import argparse
            args = argparse.Namespace(
                command="create-samples",
                isolate=False,
                target="**",
                service=None,
                output_dir=None,
            )
            result = checker.run(args)

        assert result == 0
        samples_dir = os.path.join(tmp_dir, "samples")
        assert os.path.isdir(samples_dir)
        assert os.path.isfile(os.path.join(samples_dir, "README.md"))
        assert os.path.isfile(os.path.join(samples_dir, "sample_hello_world.py"))

        with open(os.path.join(samples_dir, "README.md")) as f:
            content = f.read()
        assert "azure-fake-package" in content
        assert "azpysdk generate" in content
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_create_samples_skips_existing_files():
    tmp_dir = tempfile.mkdtemp()
    try:
        samples_dir = os.path.join(tmp_dir, "samples")
        os.makedirs(samples_dir, exist_ok=True)
        readme_path = os.path.join(samples_dir, "README.md")
        original_content = "# My custom README\n"
        with open(readme_path, "w") as f:
            f.write(original_content)

        checker = create_samples()
        fake = _make_fake_parsed_setup(tmp_dir)
        with patch.object(checker, "get_targeted_directories", return_value=[fake]):
            import argparse
            args = argparse.Namespace(
                command="create-samples",
                isolate=False,
                target="**",
                service=None,
                output_dir=None,
            )
            result = checker.run(args)

        assert result == 0
        with open(readme_path) as f:
            assert f.read() == original_content
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

