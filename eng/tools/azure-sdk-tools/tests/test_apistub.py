import argparse
import os
import pathlib
import subprocess
import sys
import pytest

from subprocess import CalledProcessError
from unittest.mock import patch, MagicMock

from azpysdk.apistub import apistub, get_package_wheel_path, get_cross_language_mapping_path


def _build_parser():
    parser = argparse.ArgumentParser(prog="azpysdk")
    subparsers = parser.add_subparsers(title="commands", dest="command")
    apistub().register(subparsers)
    return parser


class TestApistubRegistration:
    def test_generate_from_pypi_flag_sets_version(self):
        parser = _build_parser()

        args = parser.parse_args(["apistub", "--generate-from-pypi", "1.0.0"])

        assert args.command == "apistub"
        assert args.generate_from_pypi == "1.0.0"


class TestApiViewMetadata:
    def test_package_version_is_written(self, tmp_path):
        api_markdown = tmp_path / "api.md"
        api_markdown.write_text(
            "# Package is parsed using apiview-stub-generator(version:0.3.31), Python version: 3.12.9\n" "API body\n",
            encoding="utf-8",
        )
        metadata_script = pathlib.Path(__file__).parents[3] / "scripts" / "extract_apiview_metadata.py"

        subprocess.run(
            [
                sys.executable,
                str(metadata_script),
                "--api-markdown-path",
                str(api_markdown),
                "--package-version",
                "1.35.0",
            ],
            check=True,
        )

        metadata = (tmp_path / "api.metadata.yml").read_text(encoding="utf-8")
        assert "packageVersion: 1.35.0\n" in metadata


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
    def test_no_prebuilt_dir_returns_staging_whl(self, mock_find_whl, mock_parsed, monkeypatch):
        monkeypatch.delenv("PREBUILT_WHEEL_DIR", raising=False)
        mock_parsed.from_path.return_value.name = "azure-core"
        mock_parsed.from_path.return_value.version = "1.0.0"
        mock_find_whl.return_value = "azure_core-1.0.0-py3-none-any.whl"

        result = get_package_wheel_path("/my/pkg", "/staging")

        assert result == os.path.join("/staging", "azure_core-1.0.0-py3-none-any.whl")
        mock_find_whl.assert_called_once_with("/staging", "azure-core", "1.0.0")

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
    """Verify apistub output directory behavior."""

    def _make_args(
        self,
        token_file=False,
        isolate=False,
        install_deps=False,
        dest_dir=None,
        generate_from_pypi=None,
    ):
        return argparse.Namespace(
            target=".",
            isolate=isolate,
            command="apistub",
            service=None,
            token_file=token_file,
            install_deps=install_deps,
            dest_dir=dest_dir,
            generate_from_pypi=generate_from_pypi,
        )

    @patch(
        "azpysdk.apistub.REPO_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    )
    @patch("azpysdk.apistub.get_cross_language_mapping_path", return_value=None)
    @patch("azpysdk.apistub.get_package_wheel_path", return_value="/fake/pkg.whl")
    @patch("azpysdk.apistub.create_package_and_install")
    @patch("azpysdk.apistub.install_into_venv")
    @patch("azpysdk.apistub.set_envvar_defaults")
    def test_isolate_does_not_install_dependencies(
        self, _env, install_into_venv, _create, _get_whl, _get_mapping, tmp_path, monkeypatch
    ):
        """When only --isolate is passed, apistub should not install dependencies."""
        monkeypatch.chdir(os.getcwd())
        stub = apistub()
        staging = str(tmp_path / "staging")
        os.makedirs(staging, exist_ok=True)
        fake_parsed = MagicMock()
        fake_parsed.folder = str(tmp_path)
        fake_parsed.name = "azure-core"

        with patch.object(stub, "get_targeted_directories", return_value=[fake_parsed]), patch.object(
            stub, "get_executable", return_value=(sys.executable, staging)
        ), patch.object(stub, "install_dev_reqs") as install_dev_reqs, patch.object(
            stub, "pip_freeze"
        ) as pip_freeze, patch.object(
            stub, "run_venv_command"
        ):
            stub.run(self._make_args(isolate=True, token_file=True))

        install_dev_reqs.assert_not_called()
        install_into_venv.assert_not_called()
        pip_freeze.assert_not_called()

    @patch(
        "azpysdk.apistub.REPO_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    )
    @patch("azpysdk.apistub.get_cross_language_mapping_path", return_value=None)
    @patch("azpysdk.apistub.get_package_wheel_path", return_value="/fake/pkg.whl")
    @patch("azpysdk.apistub.create_package_and_install")
    @patch("azpysdk.apistub.install_into_venv")
    @patch("azpysdk.apistub.set_envvar_defaults")
    def test_install_deps_installs_dependencies(
        self, _env, install_into_venv, _create, _get_whl, _get_mapping, tmp_path, monkeypatch
    ):
        """When --install-deps is passed, apistub should install target package dev requirements."""
        monkeypatch.chdir(os.getcwd())
        stub = apistub()
        staging = str(tmp_path / "staging")
        os.makedirs(staging, exist_ok=True)
        fake_parsed = MagicMock()
        fake_parsed.folder = str(tmp_path)
        fake_parsed.name = "azure-core"

        with patch.object(stub, "get_targeted_directories", return_value=[fake_parsed]), patch.object(
            stub, "get_executable", return_value=(sys.executable, staging)
        ), patch.object(stub, "install_dev_reqs") as install_dev_reqs, patch.object(
            stub, "pip_freeze"
        ) as pip_freeze, patch.object(
            stub, "run_venv_command"
        ):
            args = self._make_args(install_deps=True, token_file=True)
            stub.run(args)

        install_dev_reqs.assert_called_once_with(sys.executable, args, str(tmp_path))
        install_into_venv.assert_not_called()
        pip_freeze.assert_called_once_with(sys.executable)

    @patch("azpysdk.apistub.logger.error")
    @patch("azpysdk.apistub.set_envvar_defaults")
    def test_runtime_error_installing_apiview_dependencies_returns_one(self, _env, logger_error, tmp_path, monkeypatch):
        """When APIView dependency install raises RuntimeError, run() should log and return 1."""
        monkeypatch.chdir(os.getcwd())
        stub = apistub()
        staging = str(tmp_path / "staging")
        os.makedirs(staging, exist_ok=True)
        fake_parsed = MagicMock()
        fake_parsed.folder = str(tmp_path)
        fake_parsed.name = "azure-core"

        with patch.object(stub, "get_targeted_directories", return_value=[fake_parsed]), patch.object(
            stub, "get_executable", return_value=(sys.executable, staging)
        ), patch.object(stub, "ensure_apistub_dependencies", side_effect=RuntimeError("401 auth error")):
            result = stub.run(self._make_args())

        assert result == 1
        logger_error.assert_called_once_with("Failed to install APIView dependencies: 401 auth error")

    @patch(
        "azpysdk.apistub.REPO_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    )
    @patch("azpysdk.apistub.install_into_venv")
    def test_apistub_dependencies_are_skipped_when_installed(self, install_into_venv, tmp_path):
        """When apistub is already importable, APIView requirements should not be reinstalled."""
        stub = apistub()

        with patch.object(stub, "run_venv_command") as run_venv_command:
            stub.ensure_apistub_dependencies(sys.executable, str(tmp_path), str(tmp_path))

        run_venv_command.assert_called_once_with(
            sys.executable, ["-c", "import apistub"], cwd=str(tmp_path), check=True
        )
        install_into_venv.assert_not_called()

    @patch(
        "azpysdk.apistub.REPO_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    )
    @patch("azpysdk.apistub.install_into_venv")
    def test_missing_apistub_installs_apiview_requirements(self, install_into_venv, tmp_path):
        """When apistub is missing, APIView requirements should be installed once."""
        stub = apistub()
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

        with patch.object(
            stub,
            "run_venv_command",
            side_effect=CalledProcessError(1, [sys.executable, "-c", "import apistub"]),
        ):
            stub.ensure_apistub_dependencies(sys.executable, str(tmp_path), str(tmp_path))

        install_into_venv.assert_called_once()
        assert install_into_venv.call_args.args[0] == sys.executable
        assert install_into_venv.call_args.args[1][0:2] == [
            "-r",
            os.path.join(repo_root, "eng", "apiview_reqs.txt"),
        ]
        assert install_into_venv.call_args.args[2] == str(tmp_path)

    @patch(
        "azpysdk.apistub.REPO_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    )
    @patch("azpysdk.apistub.get_cross_language_mapping_path", return_value=None)
    @patch("azpysdk.apistub.get_package_wheel_path", return_value="/fake/pkg.whl")
    @patch("azpysdk.apistub.create_package_and_install")
    @patch("azpysdk.apistub.install_into_venv")
    @patch("azpysdk.apistub.set_envvar_defaults")
    def test_outputs_use_package_directory(
        self, _env, _install, _create, _get_whl, _get_mapping, tmp_path, monkeypatch
    ):
        """Output should go to the package directory."""
        monkeypatch.chdir(os.getcwd())
        stub = apistub()
        staging = str(tmp_path / "staging")
        os.makedirs(staging, exist_ok=True)
        fake_parsed = MagicMock()
        fake_parsed.folder = str(tmp_path)
        fake_parsed.name = "azure-core"
        fake_parsed.version = "1.35.0"

        captured_cmds = []
        metadata_cmd = None

        def fake_apistub_run(exe, cmds, **kwargs):
            captured_cmds.append(cmds)
            out_idx = cmds.index("--out-path")
            out_dir = cmds[out_idx + 1]
            open(os.path.join(out_dir, "azure-core_python.json"), "w").close()

        def fake_pwsh(cmd, **kwargs):
            nonlocal metadata_cmd
            output_arg = "--output-path" if "extract_apiview_metadata.py" in cmd[1] else "-OutputPath"
            out_idx = cmd.index(output_arg)
            out_dir = cmd[out_idx + 1]
            if "extract_apiview_metadata.py" in cmd[1]:
                metadata_cmd = cmd
                open(os.path.join(out_dir, "api.metadata.yml"), "w").close()
            else:
                open(os.path.join(out_dir, "api.md"), "w").close()
            return MagicMock(returncode=0)

        with patch.object(stub, "get_targeted_directories", return_value=[fake_parsed]), patch.object(
            stub, "get_executable", return_value=(sys.executable, staging)
        ), patch.object(stub, "install_dev_reqs"), patch.object(stub, "pip_freeze"), patch.object(
            stub, "ensure_apistub_dependencies"
        ), patch.object(
            stub, "run_venv_command", side_effect=fake_apistub_run
        ), patch(
            "azpysdk.apistub.run", side_effect=fake_pwsh
        ):

            stub.run(self._make_args())

        # The --out-path passed to apistub should be the package directory
        assert len(captured_cmds) == 1
        cmds = captured_cmds[0]
        out_idx = cmds.index("--out-path")
        assert cmds[out_idx + 1] == os.path.abspath(str(tmp_path))
        assert os.path.exists(os.path.join(str(tmp_path), "api.md"))
        assert os.path.exists(os.path.join(str(tmp_path), "api.metadata.yml"))
        assert os.path.exists(os.path.join(str(tmp_path), "azure-core_python.json"))
        assert metadata_cmd is not None
        version_idx = metadata_cmd.index("--package-version")
        assert metadata_cmd[version_idx + 1] == "1.35.0"

    @patch(
        "azpysdk.apistub.REPO_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    )
    @patch("azpysdk.apistub.get_cross_language_mapping_path", return_value=None)
    @patch("azpysdk.apistub.get_package_wheel_path", return_value="/fake/pkg.whl")
    @patch("azpysdk.apistub.create_package_and_install")
    @patch("azpysdk.apistub.install_into_venv")
    @patch("azpysdk.apistub.set_envvar_defaults")
    def test_outputs_use_custom_destination_directory(
        self, _env, _install, _create, _get_whl, _get_mapping, tmp_path, monkeypatch
    ):
        """When --dest-dir is passed, generated files should go to that directory."""
        monkeypatch.chdir(os.getcwd())
        stub = apistub()
        staging = str(tmp_path / "staging")
        dest_dir = tmp_path / "artifacts"
        os.makedirs(staging, exist_ok=True)
        fake_parsed = MagicMock()
        fake_parsed.folder = str(tmp_path)
        fake_parsed.name = "azure-core"

        captured_cmds = []

        def fake_apistub_run(exe, cmds, **kwargs):
            captured_cmds.append(cmds)
            out_idx = cmds.index("--out-path")
            out_dir = cmds[out_idx + 1]
            open(os.path.join(out_dir, "azure-core_python.json"), "w").close()

        def fake_pwsh(cmd, **kwargs):
            output_arg = "--output-path" if "extract_apiview_metadata.py" in cmd[1] else "-OutputPath"
            out_idx = cmd.index(output_arg)
            out_dir = cmd[out_idx + 1]
            output_file = "api.metadata.yml" if "extract_apiview_metadata.py" in cmd[1] else "api.md"
            open(os.path.join(out_dir, output_file), "w").close()
            return MagicMock(returncode=0)

        with patch.object(stub, "get_targeted_directories", return_value=[fake_parsed]), patch.object(
            stub, "get_executable", return_value=(sys.executable, staging)
        ), patch.object(stub, "install_dev_reqs"), patch.object(stub, "pip_freeze"), patch.object(
            stub, "ensure_apistub_dependencies"
        ), patch.object(
            stub, "run_venv_command", side_effect=fake_apistub_run
        ), patch(
            "azpysdk.apistub.run", side_effect=fake_pwsh
        ):
            stub.run(self._make_args(dest_dir=str(dest_dir)))

        assert len(captured_cmds) == 1
        cmds = captured_cmds[0]
        out_idx = cmds.index("--out-path")
        assert cmds[out_idx + 1] == os.path.abspath(str(dest_dir))
        assert os.path.exists(os.path.join(str(dest_dir), "api.md"))
        assert os.path.exists(os.path.join(str(dest_dir), "azure-core_python.json"))

    @patch(
        "azpysdk.apistub.REPO_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    )
    @patch("azpysdk.apistub.get_cross_language_mapping_path", return_value=None)
    @patch("azpysdk.apistub.get_package_wheel_path", return_value="/fake/pkg.whl")
    @patch("azpysdk.apistub.create_package_and_install")
    @patch("azpysdk.apistub.install_into_venv")
    @patch("azpysdk.apistub.set_envvar_defaults")
    def test_default_generation_adds_skip_pylint(
        self, _env, _install, _create, _get_whl, _get_mapping, tmp_path, monkeypatch
    ):
        """By default, markdown generation should add --skip-pylint to the cmds."""
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
            # Create the token JSON so the markdown generation branch can proceed
            out_idx = cmds.index("--out-path")
            out_dir = cmds[out_idx + 1]
            os.makedirs(out_dir, exist_ok=True)
            open(os.path.join(out_dir, "azure-core_python.json"), "w").close()

        def fake_pwsh(cmd, **kwargs):
            return MagicMock(returncode=0, stdout=None)

        with patch.object(stub, "get_targeted_directories", return_value=[fake_parsed]), patch.object(
            stub, "get_executable", return_value=(sys.executable, staging)
        ), patch.object(stub, "install_dev_reqs"), patch.object(stub, "pip_freeze"), patch.object(
            stub, "ensure_apistub_dependencies"
        ), patch.object(
            stub, "run_venv_command", side_effect=fake_apistub_run
        ), patch(
            "azpysdk.apistub.run", side_effect=fake_pwsh
        ):
            stub.run(self._make_args())

        assert len(captured_cmds) == 1
        assert "--skip-pylint" in captured_cmds[0]

    @patch(
        "azpysdk.apistub.REPO_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    )
    @patch("azpysdk.apistub.get_cross_language_mapping_path", return_value=None)
    @patch("azpysdk.apistub.get_package_wheel_path", return_value="/fake/pkg.whl")
    @patch("azpysdk.apistub.create_package_and_install")
    @patch("azpysdk.apistub.install_into_venv")
    @patch("azpysdk.apistub.set_envvar_defaults")
    def test_token_file_omits_skip_pylint_and_markdown_generation(
        self, _env, _install, _create, _get_whl, _get_mapping, tmp_path, monkeypatch
    ):
        """When --token-file is passed, only the raw token file should be generated."""
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
            out_idx = cmds.index("--out-path")
            out_dir = cmds[out_idx + 1]
            open(os.path.join(out_dir, "azure-core_python.json"), "w").close()

        with patch.object(stub, "get_targeted_directories", return_value=[fake_parsed]), patch.object(
            stub, "get_executable", return_value=(sys.executable, staging)
        ), patch.object(stub, "install_dev_reqs"), patch.object(stub, "pip_freeze"), patch.object(
            stub, "ensure_apistub_dependencies"
        ), patch.object(
            stub, "run_venv_command", side_effect=fake_apistub_run
        ), patch(
            "azpysdk.apistub.run"
        ) as pwsh_run:
            stub.run(self._make_args(token_file=True))

        assert len(captured_cmds) == 1
        assert "--skip-pylint" not in captured_cmds[0]
        assert os.path.exists(os.path.join(str(tmp_path), "azure-core_python.json"))
        pwsh_run.assert_not_called()

    @patch(
        "azpysdk.apistub.REPO_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    )
    @patch("azpysdk.apistub.get_cross_language_mapping_path", return_value=None)
    @patch("azpysdk.apistub.create_package_and_install")
    @patch("azpysdk.apistub.install_into_venv")
    @patch("azpysdk.apistub.set_envvar_defaults")
    def test_pypi_version_downloads_wheel_instead_of_building(
        self, _env, _install, create_package_and_install, _get_mapping, tmp_path, monkeypatch
    ):
        """When a PyPI version is passed, the wheel is downloaded from PyPI and local build is skipped."""
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
            out_idx = cmds.index("--out-path")
            out_dir = cmds[out_idx + 1]
            open(os.path.join(out_dir, "azure-core_python.json"), "w").close()

        with patch.object(stub, "get_targeted_directories", return_value=[fake_parsed]), patch.object(
            stub, "get_executable", return_value=(sys.executable, staging)
        ), patch.object(stub, "install_dev_reqs"), patch.object(stub, "pip_freeze"), patch.object(
            stub, "ensure_apistub_dependencies"
        ), patch.object(
            stub, "download_pypi_wheel", return_value="/fake/azure_core-1.0.0-py3-none-any.whl"
        ) as download_pypi_wheel, patch.object(
            stub, "run_venv_command", side_effect=fake_apistub_run
        ):
            stub.run(self._make_args(token_file=True, generate_from_pypi="1.0.0"))

        download_pypi_wheel.assert_called_once_with(sys.executable, "azure-core", "1.0.0", staging)
        create_package_and_install.assert_not_called()
        assert len(captured_cmds) == 1
        pkg_idx = captured_cmds[0].index("--pkg-path")
        assert captured_cmds[0][pkg_idx + 1] == os.path.abspath("/fake/azure_core-1.0.0-py3-none-any.whl")

    @patch("azpysdk.apistub.find_whl", return_value="azure_core-1.0.0-py3-none-any.whl")
    def test_download_pypi_wheel_runs_pip_download(self, _find_whl, tmp_path):
        """download_pypi_wheel should pip download the wheel and return its path."""
        stub = apistub()
        staging = str(tmp_path)

        with patch.object(stub, "run_venv_command") as run_venv_command:
            result = stub.download_pypi_wheel(sys.executable, "azure-core", "1.0.0", staging)

        run_venv_command.assert_called_once()
        cmds = run_venv_command.call_args.args[1]
        assert cmds[0:4] == ["-m", "pip", "download", "azure-core==1.0.0"]
        assert "--no-deps" in cmds
        assert (
            "--index-url=https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/"
            in cmds
        )
        assert run_venv_command.call_args.kwargs["additional_environment_settings"] == {"PIP_EXTRA_INDEX_URL": ""}
        assert result == os.path.join(staging, "azure_core-1.0.0-py3-none-any.whl")

    @patch("azpysdk.apistub.find_whl", return_value="azure_core-1.0.0-py3-none-any.whl")
    def test_download_pypi_wheel_falls_back_to_public_pypi(self, _find_whl, tmp_path):
        """download_pypi_wheel should retry public PyPI when the Azure SDK feed fails."""
        stub = apistub()

        with patch.object(stub, "run_venv_command", side_effect=[CalledProcessError(1, "pip"), None]) as run:
            result = stub.download_pypi_wheel(sys.executable, "azure-core", "1.0.0", str(tmp_path))

        assert run.call_count == 2
        assert "--index-url=https://pypi.org/simple/" in run.call_args_list[1].args[1]
        assert all(
            call.kwargs["additional_environment_settings"] == {"PIP_EXTRA_INDEX_URL": ""} for call in run.call_args_list
        )
        assert result == os.path.join(str(tmp_path), "azure_core-1.0.0-py3-none-any.whl")

    def test_download_pypi_wheel_reports_both_index_failures(self, tmp_path, caplog):
        """download_pypi_wheel should propagate the public PyPI failure after both indexes fail."""
        stub = apistub()
        public_pypi_error = CalledProcessError(2, "pip", stderr="public PyPI unavailable")

        with patch.object(
            stub, "run_venv_command", side_effect=[CalledProcessError(1, "pip"), public_pypi_error]
        ) as run:
            with pytest.raises(CalledProcessError) as exc_info:
                stub.download_pypi_wheel(sys.executable, "azure-core", "1.0.0", str(tmp_path))

        assert run.call_count == 2
        assert exc_info.value is public_pypi_error
        assert "public PyPI unavailable" in caplog.text

    @patch("azpysdk.apistub.find_whl", return_value=None)
    def test_download_pypi_wheel_raises_when_no_wheel(self, _find_whl, tmp_path):
        """download_pypi_wheel should raise FileNotFoundError when no wheel is downloaded."""
        stub = apistub()
        with patch.object(stub, "run_venv_command"):
            with pytest.raises(FileNotFoundError, match="No wheel found"):
                stub.download_pypi_wheel(sys.executable, "azure-core", "1.0.0", str(tmp_path))
