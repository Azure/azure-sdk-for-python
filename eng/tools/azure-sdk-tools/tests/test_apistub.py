import argparse
import os
import sys
import pytest

from unittest.mock import patch, MagicMock

from azpysdk.apistub import apistub, get_package_wheel_path, get_cross_language_mapping_path


# ── get_package_wheel_path() ─────────────────────────────────────────────


class TestGetPackageWheelPath:
    """Test the prebuilt-wheel lookup, wheel-in-source-dir, and fallback logic."""

    @patch("azpysdk.apistub.ParsedSetup")
    @patch("azpysdk.apistub.find_whl")
    def test_prebuilt_dir_returns_wheel(self, mock_find_whl, mock_parsed, tmp_path, monkeypatch):
        """When PREBUILT_WHEEL_DIR is set and a wheel is found there, return its full path."""
        prebuilt = str(tmp_path / "prebuilt")
        os.makedirs(prebuilt, exist_ok=True)
        monkeypatch.setenv("PREBUILT_WHEEL_DIR", prebuilt)

        mock_parsed.from_path.return_value = MagicMock(name="azure-core", version="1.0.0")
        mock_find_whl.return_value = "azure_core-1.0.0-py3-none-any.whl"

        result = get_package_wheel_path("/some/pkg")
        assert result == os.path.join(prebuilt, "azure_core-1.0.0-py3-none-any.whl")

    @patch("azpysdk.apistub.ParsedSetup")
    @patch("azpysdk.apistub.find_whl")
    def test_prebuilt_dir_raises_when_no_wheel(self, mock_find_whl, mock_parsed, tmp_path, monkeypatch):
        """When PREBUILT_WHEEL_DIR is set but no matching wheel is found, raise FileNotFoundError."""
        prebuilt = str(tmp_path / "prebuilt")
        os.makedirs(prebuilt, exist_ok=True)
        monkeypatch.setenv("PREBUILT_WHEEL_DIR", prebuilt)

        mock_parsed.from_path.return_value = MagicMock(name="azure-core", version="1.0.0")
        mock_find_whl.return_value = None

        with pytest.raises(FileNotFoundError, match="No prebuilt wheel found"):
            get_package_wheel_path("/some/pkg")

    @patch("azpysdk.apistub.ParsedSetup")
    @patch("azpysdk.apistub.find_whl")
    def test_no_prebuilt_dir_returns_found_whl(self, mock_find_whl, mock_parsed, monkeypatch):
        """Without PREBUILT_WHEEL_DIR, return wheel found in pkg_root."""
        monkeypatch.delenv("PREBUILT_WHEEL_DIR", raising=False)

        mock_parsed.from_path.return_value = MagicMock(name="azure-core", version="1.0.0")
        mock_find_whl.return_value = "azure_core-1.0.0-py3-none-any.whl"

        result = get_package_wheel_path("/my/pkg")
        assert result == "azure_core-1.0.0-py3-none-any.whl"

    @patch("azpysdk.apistub.ParsedSetup")
    @patch("azpysdk.apistub.find_whl")
    def test_no_prebuilt_dir_falls_back_to_pkg_root(self, mock_find_whl, mock_parsed, monkeypatch):
        """Without PREBUILT_WHEEL_DIR and no wheel found, fall back to pkg_root path."""
        monkeypatch.delenv("PREBUILT_WHEEL_DIR", raising=False)

        mock_parsed.from_path.return_value = MagicMock(name="azure-core", version="1.0.0")
        mock_find_whl.return_value = None

        result = get_package_wheel_path("/my/pkg")
        assert result == "/my/pkg"


# ── run() output directory logic ─────────────────────────────────────────


class TestRunOutputDirectory:
    """Verify that dest_dir controls where the output token path ends up."""

    def _make_args(self, dest_dir=None, generate_md=False):
        return argparse.Namespace(
            target=".",
            isolate=False,
            command="apistub",
            service=None,
            dest_dir=dest_dir,
            generate_md=generate_md,
        )

    @patch(
        "azpysdk.apistub.REPO_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    )
    @patch("azpysdk.apistub.MAX_PYTHON_VERSION", (99, 99))
    @patch("azpysdk.apistub.get_cross_language_mapping_path", return_value=None)
    @patch("azpysdk.apistub.get_package_wheel_path", return_value="/fake/pkg.whl")
    @patch("azpysdk.apistub.create_package_and_install")
    @patch("azpysdk.apistub.install_into_venv")
    @patch("azpysdk.apistub.set_envvar_defaults")
    def test_dest_dir_creates_package_subfolder(
        self, _env, _install, _create, _get_whl, _get_mapping, tmp_path, monkeypatch
    ):
        """When --dest-dir is given, output should go to <dest_dir>/<package_name>/."""
        monkeypatch.chdir(os.getcwd())
        dest = tmp_path / "output"
        dest.mkdir()

        stub = apistub()
        staging = str(tmp_path / "staging")
        os.makedirs(staging, exist_ok=True)
        fake_parsed = MagicMock()
        fake_parsed.folder = str(tmp_path)
        fake_parsed.name = "azure-core"

        def fake_apistub_run(exe, cmds, **kwargs):
            # Simulate apistub generating the token JSON
            out_idx = cmds.index("--out-path")
            out_dir = cmds[out_idx + 1]
            os.makedirs(out_dir, exist_ok=True)
            open(os.path.join(out_dir, "azure-core_python.json"), "w").close()

        def fake_pwsh(cmd, **kwargs):
            # Simulate pwsh generating api.md
            out_idx = cmd.index("-OutputPath")
            out_dir = cmd[out_idx + 1]
            open(os.path.join(out_dir, "api.md"), "w").close()
            return MagicMock(returncode=0)

        with patch.object(stub, "get_targeted_directories", return_value=[fake_parsed]), patch.object(
            stub, "get_executable", return_value=(sys.executable, staging)
        ), patch.object(stub, "install_dev_reqs"), patch.object(stub, "pip_freeze"), patch.object(
            stub, "run_venv_command", side_effect=fake_apistub_run
        ), patch(
            "azpysdk.apistub.run", side_effect=fake_pwsh
        ):

            stub.run(self._make_args(dest_dir=str(dest), generate_md=True))

        expected_out = os.path.join(str(dest), "azure-core")
        assert os.path.isdir(expected_out)
        assert os.path.exists(os.path.join(expected_out, "api.md"))
        assert os.path.exists(os.path.join(expected_out, "azure-core_python.json"))

    @patch(
        "azpysdk.apistub.REPO_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    )
    @patch("azpysdk.apistub.MAX_PYTHON_VERSION", (99, 99))
    @patch("azpysdk.apistub.get_cross_language_mapping_path", return_value=None)
    @patch("azpysdk.apistub.get_package_wheel_path", return_value="/fake/pkg.whl")
    @patch("azpysdk.apistub.create_package_and_install")
    @patch("azpysdk.apistub.install_into_venv")
    @patch("azpysdk.apistub.set_envvar_defaults")
    def test_no_dest_dir_uses_staging(self, _env, _install, _create, _get_whl, _get_mapping, tmp_path, monkeypatch):
        """When --dest-dir is not given, output path should be the staging directory."""
        monkeypatch.chdir(os.getcwd())
        stub = apistub()
        staging = str(tmp_path / "staging")
        os.makedirs(staging, exist_ok=True)
        fake_parsed = MagicMock()
        fake_parsed.folder = str(tmp_path)
        fake_parsed.name = "azure-core"

        captured_cmds = []

        def fake_apistub_run(exe, cmds, **kwargs):
            captured_cmds.append(cmds)
            # Simulate apistub generating the token JSON
            out_idx = cmds.index("--out-path")
            out_dir = cmds[out_idx + 1]
            open(os.path.join(out_dir, "azure-core_python.json"), "w").close()

        def fake_pwsh(cmd, **kwargs):
            out_idx = cmd.index("-OutputPath")
            out_dir = cmd[out_idx + 1]
            open(os.path.join(out_dir, "api.md"), "w").close()
            return MagicMock(returncode=0)

        with patch.object(stub, "get_targeted_directories", return_value=[fake_parsed]), patch.object(
            stub, "get_executable", return_value=(sys.executable, staging)
        ), patch.object(stub, "install_dev_reqs"), patch.object(stub, "pip_freeze"), patch.object(
            stub, "run_venv_command", side_effect=fake_apistub_run
        ), patch(
            "azpysdk.apistub.run", side_effect=fake_pwsh
        ):

            stub.run(self._make_args(dest_dir=None, generate_md=True))

        # The --out-path passed to apistub should be the staging directory
        assert len(captured_cmds) == 1
        cmds = captured_cmds[0]
        out_idx = cmds.index("--out-path")
        assert cmds[out_idx + 1] == os.path.abspath(staging)
        assert os.path.exists(os.path.join(staging, "api.md"))
        assert os.path.exists(os.path.join(staging, "azure-core_python.json"))
