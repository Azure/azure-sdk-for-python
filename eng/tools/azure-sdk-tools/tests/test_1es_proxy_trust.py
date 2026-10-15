import os
import ssl
import subprocess
import sys
import venv
from pathlib import Path
from types import SimpleNamespace

import certifi
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eng.scripts import run_with_1es_proxy_trust as proxy_trust


@pytest.fixture
def proxy_ca_environment(tmp_path, monkeypatch):
    roots = ssl.create_default_context(cafile=certifi.where()).get_ca_certs(binary_form=True)
    baseline = tmp_path / "baseline.pem"
    proxy_ca = tmp_path / "agent supplied proxy CA.pem"
    baseline.write_text(ssl.DER_cert_to_PEM_cert(roots[0]).rstrip(), encoding="ascii")
    proxy_ca.write_text(ssl.DER_cert_to_PEM_cert(roots[1]), encoding="ascii")
    monkeypatch.setattr(sys, "platform", "win32")
    for name, value in {
        "TF_BUILD": "True",
        "BUILD_BUILDID": "not-used-to-discover-the-certificate",
        "1ESNI_CONFIG_PATH": str(tmp_path),
        "HTTPS_PROXY": "http://proxy.example.invalid:18080",
        "SSL_CERT_FILE": str(baseline),
        "NODE_EXTRA_CA_CERTS": str(proxy_ca),
        "REQUESTS_CA_BUNDLE": "unchanged-requests-ca.pem",
        "PIP_INDEX_URL": "https://example.invalid/cfs",
        "UV_DEFAULT_INDEX": "https://example.invalid/cfs",
        "UV_SYSTEM_CERTS": "1",
        "CIBW_BUILD": "cp310* pp*",
        "CIBW_SKIP": "*-musllinux*",
        "CIBW_BUILD_FRONTEND": "build",
        "CIBW_ARCHS_WINDOWS": "AMD64 ARM64",
        "CIBW_ENVIRONMENT": 'CFLAGS="-DSTORAGE_TEST"',
    }.items():
        monkeypatch.setenv(name, value)
    return baseline, proxy_ca, {roots[0], roots[1]}


@pytest.mark.parametrize("explicit_baseline", [False, True])
def test_proxy_bundle(proxy_ca_environment, explicit_baseline, monkeypatch):
    baseline, proxy_ca, expected_roots = proxy_ca_environment
    if not explicit_baseline:
        monkeypatch.delenv("SSL_CERT_FILE")
        baseline = Path(certifi.where())
        expected_roots = set(ssl.create_default_context(cafile=str(baseline)).get_ca_certs(binary_form=True))
    before = os.environ.copy()

    with proxy_trust.proxy_environment() as environment:
        bundle = Path(environment["SSL_CERT_FILE"])
        assert bundle.read_bytes() == baseline.read_bytes() + b"\n" + proxy_ca.read_bytes() + b"\n"
        context = ssl.create_default_context(cafile=str(bundle))
        assert set(context.get_ca_certs(binary_form=True)) == expected_roots
        assert context.verify_mode == ssl.CERT_REQUIRED
        assert context.check_hostname
        assert environment == {**before, "SSL_CERT_FILE": str(bundle)}
        assert os.environ == before

    assert not bundle.parent.exists()
    assert os.environ == before


@pytest.mark.parametrize(
    "platform,name,value",
    [
        ("linux", None, None),
        ("darwin", None, None),
        ("win32", "TF_BUILD", None),
        ("win32", "TF_BUILD", "False"),
        ("win32", "1ESNI_CONFIG_PATH", None),
        ("win32", "HTTPS_PROXY", None),
        ("win32", "HTTPS_PROXY", ""),
    ],
)
def test_proxy_bundle_inactive(proxy_ca_environment, platform, name, value, monkeypatch):
    monkeypatch.setattr(sys, "platform", platform)
    monkeypatch.setenv("NODE_EXTRA_CA_CERTS", "unreadable-and-not-trusted-outside-1es.pem")
    if name:
        if value is None:
            monkeypatch.delenv(name)
        else:
            monkeypatch.setenv(name, value)
    before = os.environ.copy()
    with proxy_trust.proxy_environment() as environment:
        assert environment is None
    assert os.environ == before


@pytest.mark.parametrize("value", [None, ""])
def test_missing_proxy_ca_path(proxy_ca_environment, value, monkeypatch):
    if value is None:
        monkeypatch.delenv("NODE_EXTRA_CA_CERTS")
    else:
        monkeypatch.setenv("NODE_EXTRA_CA_CERTS", value)
    with pytest.raises(RuntimeError, match="CA path supplied in NODE_EXTRA_CA_CERTS"):
        with proxy_trust.proxy_environment():
            pytest.fail("Missing infrastructure configuration must fail the command.")


@pytest.mark.parametrize("source", ["baseline", "proxy"])
@pytest.mark.parametrize("state", ["missing", "empty", "invalid"])
def test_invalid_certificates(proxy_ca_environment, source, state, tmp_path, monkeypatch):
    baseline, proxy_ca, _ = proxy_ca_environment
    certificate = baseline if source == "baseline" else proxy_ca
    if state == "missing":
        certificate.unlink()
        expected_error = FileNotFoundError
    else:
        certificate.write_text("" if state == "empty" else "not a certificate", encoding="ascii")
        expected_error = ssl.SSLError
    real_temporary_directory = proxy_trust.TemporaryDirectory
    monkeypatch.setattr(
        proxy_trust, "TemporaryDirectory", lambda **kwargs: real_temporary_directory(dir=tmp_path, **kwargs)
    )
    before = os.environ.copy()
    with pytest.raises(expected_error):
        with proxy_trust.proxy_environment():
            pytest.fail("Missing or invalid CA certificates must fail the command.")
    assert not list(tmp_path.glob("pipeline-proxy-ca-*"))
    assert os.environ == before


@pytest.mark.parametrize("returncode", [0, 7])
def test_child_command_and_exit_code(proxy_ca_environment, returncode, monkeypatch):
    command = ["sdk_build", "--service=storage", "a package with spaces", "--inactive"]
    monkeypatch.setattr(sys, "argv", ["run_with_1es_proxy_trust.py", *command])
    before = os.environ.copy()
    bundle = None

    def run(command_args, **kwargs):
        nonlocal bundle
        bundle = Path(kwargs["env"]["SSL_CERT_FILE"])
        assert bundle.is_file()
        assert command_args == command
        assert kwargs == {"env": {**before, "SSL_CERT_FILE": str(bundle)}, "check": False}
        assert os.environ == before
        return SimpleNamespace(returncode=returncode)

    monkeypatch.setattr(proxy_trust.subprocess, "run", run)
    assert proxy_trust.main() == returncode
    assert not bundle.parent.exists()
    assert os.environ == before


def test_child_launch_failure_cleans_up(proxy_ca_environment, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["run_with_1es_proxy_trust.py", "missing-command"])
    before = os.environ.copy()
    bundle = None

    def run(*args, **kwargs):
        nonlocal bundle
        bundle = Path(kwargs["env"]["SSL_CERT_FILE"])
        assert bundle.is_file()
        raise FileNotFoundError("missing-command")

    monkeypatch.setattr(proxy_trust.subprocess, "run", run)
    with pytest.raises(FileNotFoundError, match="missing-command"):
        proxy_trust.main()
    assert not bundle.parent.exists()
    assert os.environ == before


def test_child_process_uses_bundle(proxy_ca_environment, monkeypatch, capfd):
    before = os.environ.copy()
    script = (
        "import os, ssl; from pathlib import Path; "
        "bundle = os.environ['SSL_CERT_FILE']; "
        "context = ssl.create_default_context(cafile=bundle); "
        "assert context.verify_mode == ssl.CERT_REQUIRED and context.check_hostname; "
        "assert len(context.get_ca_certs()) == 2; "
        "print(bundle); raise SystemExit(7)"
    )
    monkeypatch.setattr(sys, "argv", ["run_with_1es_proxy_trust.py", "python", "-c", script])
    assert proxy_trust.main() == 7
    bundle = Path(capfd.readouterr().out.strip().splitlines()[-1])
    assert not bundle.parent.exists()
    assert os.environ == before


def test_inactive_child_inherits_environment(monkeypatch):
    monkeypatch.setenv("TF_BUILD", "False")
    monkeypatch.setenv("NODE_EXTRA_CA_CERTS", "unreadable-and-not-trusted-outside-1es.pem")
    monkeypatch.setattr(sys, "argv", ["run_with_1es_proxy_trust.py", "sdk_build", "--inactive"])
    before = os.environ.copy()

    def run(command, **kwargs):
        assert command == ["sdk_build", "--inactive"]
        assert kwargs == {"env": None, "check": False}
        assert os.environ == before
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(proxy_trust.subprocess, "run", run)
    assert proxy_trust.main() == 0


@pytest.mark.parametrize("command", ["python", "python.exe"])
@pytest.mark.parametrize("active", [False, True])
def test_python_alias_uses_wrapper_interpreter(proxy_ca_environment, command, active, tmp_path, monkeypatch):
    if not active:
        monkeypatch.setenv("TF_BUILD", "False")
    executable = str(tmp_path / "venv with spaces" / "python.exe")
    arguments = ["script with spaces.py", "--service=storage"]
    monkeypatch.setattr(sys, "executable", executable)
    monkeypatch.setattr(sys, "argv", ["run_with_1es_proxy_trust.py", command, *arguments])

    def run(command_args, **kwargs):
        assert command_args == [executable, *arguments]
        assert kwargs["check"] is False
        if active:
            assert Path(kwargs["env"]["SSL_CERT_FILE"]).is_file()
        else:
            assert kwargs["env"] is None
        return SimpleNamespace(returncode=7)

    monkeypatch.setattr(proxy_trust.subprocess, "run", run)
    assert proxy_trust.main() == 7


def test_bare_python_command_preserves_virtualenv(tmp_path, monkeypatch):
    environment = tmp_path / "venv with spaces"
    venv.EnvBuilder(with_pip=False).create(environment)
    python = environment / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")
    site_packages = next(environment.rglob("site-packages"))
    # Let the wrapper import the already-installed certifi without downloading packages.
    (site_packages / "test-certifi.pth").write_text(
        str(Path(certifi.__file__).resolve().parent.parent) + "\n", encoding="utf-8"
    )
    (site_packages / "venv_only_dependency.py").write_text("VALUE = 123\n", encoding="ascii")
    script = (
        "import sys, venv_only_dependency; "
        "assert venv_only_dependency.VALUE == 123; "
        "print(sys.prefix); raise SystemExit(7)"
    )
    monkeypatch.setenv("TF_BUILD", "False")
    monkeypatch.setenv("PATH", str(python.parent) + os.pathsep + os.environ["PATH"])

    result = subprocess.run(
        [str(python), str(Path(proxy_trust.__file__).resolve()), "python", "-c", script],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 7, result.stderr
    assert Path(result.stdout.strip()) == environment


@pytest.mark.parametrize("command", ["python3", "sdk_build", sys.executable, os.path.join("custom", "python.exe")])
def test_other_commands_are_not_rewritten(command, monkeypatch):
    monkeypatch.setenv("TF_BUILD", "False")
    monkeypatch.setattr(sys, "argv", ["run_with_1es_proxy_trust.py", command, "--version"])

    def run(command_args, **kwargs):
        assert command_args == [command, "--version"]
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(proxy_trust.subprocess, "run", run)
    assert proxy_trust.main() == 0


def test_missing_command(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["run_with_1es_proxy_trust.py"])
    with pytest.raises(SystemExit) as error:
        proxy_trust.main()
    assert error.value.code == 2


@pytest.mark.parametrize("federated", [False, True])
def test_pipeline_commands_use_wrapper(federated):
    steps_dir = REPO_ROOT / "eng" / "pipelines" / "templates" / "steps"
    artifact_steps = yaml.safe_load((steps_dir / "build-package-artifacts.yml").read_text())["steps"]
    build_step = next(step for step in artifact_steps if step.get("displayName") == "Generate Packages")
    assert "python eng/scripts/run_with_1es_proxy_trust.py sdk_build " in build_step["pwsh"]
    assert "exit $LASTEXITCODE" in build_step["pwsh"]

    test_steps = yaml.safe_load((steps_dir / "build-test.yml").read_text())["steps"]
    branches = [step for step in test_steps if any("UseFederatedAuth" in key or "${{ else }}" in key for key in step)]
    assert len(branches) == 4
    commands = []
    for branch in branches:
        key = next(iter(branch))
        if ("UseFederatedAuth" in key) == federated:
            for step in branch[key]:
                if federated:
                    commands.append(step["inputs"]["Inline"])
                else:
                    commands.append(step["pwsh"])
    assert len(commands) == 2
    for command in commands:
        assert "python eng/scripts/run_with_1es_proxy_trust.py python eng/scripts/dispatch_checks.py" in command
