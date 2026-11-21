# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import json
import hashlib
import io
import os
from pathlib import Path
import socket
import subprocess
import sys
import textwrap
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from toxiproxy import run_toxiproxy
from toxiproxy import _toxiproxy_config
from toxiproxy._process_tree import OwnedProcessTree, run_owned_worker
from toxiproxy._toxiproxy_config import digest
from toxiproxy._toxiproxy_config import validate_endpoint
from fault_injection._regional_routing import assert_fields


def test_local_runner_selections_use_dedicated_folder_rust():
    folder = Path(__file__).parent
    assert Path(run_toxiproxy.__file__).parent == folder
    for selection in run_toxiproxy.SELECTIONS.values():
        assert all((folder / name).is_file() for name in selection)


@pytest.mark.parametrize("valid", [False, True])
def test_server_install_checks_hash_before_publishing_executable_rust(tmp_path, monkeypatch, valid):
    content = b"controlled executable bytes"
    expected = hashlib.sha256(content if valid else b"different release").hexdigest()
    monkeypatch.setattr(_toxiproxy_config, "SERVER_SHA256", expected)
    download = Mock(return_value=io.BytesIO(content))
    monkeypatch.setattr(_toxiproxy_config, "urlopen", download)
    path = tmp_path / "tools" / "server.exe"
    if valid:
        assert _toxiproxy_config.install_server(path) == path
        assert path.read_bytes() == content
        assert _toxiproxy_config.install_server(path) == path
    else:
        with pytest.raises(ValueError, match="checksum"):
            _toxiproxy_config.install_server(path)
        assert not path.exists()
    download.assert_called_once_with(_toxiproxy_config.SERVER_URL, timeout=60)
    assert list(path.parent.iterdir()) == ([path] if valid else [])


def test_server_install_does_not_replace_an_unverified_existing_file_rust(tmp_path, monkeypatch):
    path = tmp_path / "server.exe"
    path.write_bytes(b"not the requested release")
    download = Mock()
    monkeypatch.setattr(_toxiproxy_config, "urlopen", download)
    with pytest.raises(ValueError, match="checksum"):
        _toxiproxy_config.install_server(path)
    download.assert_not_called()
    assert path.read_bytes() == b"not the requested release"


def test_resource_fixture_is_shared_between_fault_suites_rust():
    from config.fault_resources import owned_target
    from fault_injection import conftest as driver_fixtures
    from toxiproxy import conftest as proxy_fixtures

    assert driver_fixtures.owned_target is owned_target
    assert proxy_fixtures.owned_target is owned_target
    assert not hasattr(driver_fixtures, "proxy_route")


def test_proxy_fixture_rejects_remote_endpoint_before_startup_rust(tmp_path, monkeypatch):
    from toxiproxy import conftest as fixtures

    start = Mock()
    request = SimpleNamespace(param="plain", addfinalizer=Mock())
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.documents.azure.com/")
    monkeypatch.setattr("toxiproxy._toxiproxy.OwnedProxy", start)
    with pytest.raises(ValueError, match="loopback"):
        fixtures.proxy_route.__wrapped__(tmp_path, request, monkeypatch)
    start.assert_not_called()
    request.addfinalizer.assert_not_called()


def test_proxy_fixture_accepts_current_driver_revision_rust(tmp_path, monkeypatch):
    from azure.cosmos import _rust
    from toxiproxy import conftest as fixtures

    monkeypatch.setattr(_rust, "__rust_driver_commit__", "unit-test-revision")
    monkeypatch.setenv("ACCOUNT_HOST", "https://localhost:8081/")
    proxy = Mock(sdk_endpoint="127.0.0.1:19081")
    tunnel = Mock(proxy_url="http://127.0.0.1:19082")
    monkeypatch.setattr("toxiproxy._toxiproxy.OwnedProxy", Mock(return_value=proxy))
    monkeypatch.setattr("toxiproxy._connect_tunnel.ConnectTunnel", Mock(return_value=tunnel))
    configure = Mock()
    monkeypatch.setattr("toxiproxy._connect_tunnel.configure_proxy_environment", configure)
    request = SimpleNamespace(param="plain", addfinalizer=Mock())
    assert fixtures.proxy_route.__wrapped__(tmp_path, request, monkeypatch) is proxy
    proxy.start.assert_called_once_with()
    tunnel.start.assert_called_once_with()
    configure.assert_called_once_with(monkeypatch, tunnel)


@pytest.mark.parametrize("endpoint", ["https://localhost:8081/", "https://127.0.0.1:8081"])
def test_local_runner_accepts_only_loopback_rust(endpoint):
    validate_endpoint(endpoint)


@pytest.mark.parametrize(
    "endpoint",
    [
        "https://example.documents.azure.com/",
        "http://localhost:8081/",
        "https://localhost:8081/path",
        "https://localhost:8081/?x=1",
        "https://localhost:8081/#x",
        "https://user@localhost:8081/",
        "https://localhost:0/",
    ],
)
def test_local_runner_rejects_unsafe_endpoint_rust(endpoint):
    with pytest.raises(ValueError):
        validate_endpoint(endpoint)


@pytest.mark.parametrize("counter", [0, 2])
def test_stored_increment_rejects_missing_or_duplicate_application_rust(counter):
    with pytest.raises(AssertionError):
        assert_fields(
            {"refund_attempts": counter, "receipt": "full"},
            {"refund_attempts": 1, "receipt": "full"},
        )


def test_stored_write_rejects_partial_receipt_rust():
    with pytest.raises(AssertionError):
        assert_fields(
            {"refund_attempts": 1, "receipt": "par"},
            {"refund_attempts": 1, "receipt": "partial"},
        )


@pytest.fixture
def gated_worker(tmp_path):
    script = tmp_path / "worker.py"
    script.write_text(
        textwrap.dedent("""
            import json
            from pathlib import Path
            import os
            import socket
            import subprocess
            import sys
            import time

            mode, marker = sys.argv[1], Path(sys.argv[2])
            if mode == "child":
                with socket.socket() as listener:
                    listener.bind(("127.0.0.1", 0))
                    listener.listen()
                    temporary = marker.with_suffix(".tmp")
                    temporary.write_text(json.dumps({"pid": os.getpid(), "port": listener.getsockname()[1]}))
                    temporary.replace(marker)
                    time.sleep(60)
            else:
                if sys.stdin.buffer.read(1) != b"1":
                    raise RuntimeError("Worker was not released")
                subprocess.Popen([sys.executable, __file__, "child", str(marker)])
                deadline = time.monotonic() + 5
                while not marker.exists():
                    if time.monotonic() > deadline:
                        raise TimeoutError("Child was not ready")
                    time.sleep(0.01)
                if mode == "timeout":
                    time.sleep(60)
                else:
                    sys.exit(int(mode))
            """),
        encoding="utf-8",
    )
    return script


@pytest.mark.skipif(os.name != "nt", reason="Windows process-tree ownership")
@pytest.mark.parametrize("outcome", ["0", "7", "timeout"], ids=["success", "failure", "timeout"])
def test_worker_cleanup_reaps_descendants_but_not_unrelated_processes_rust(tmp_path, gated_worker, outcome):
    marker = tmp_path / "child.json"
    state = {}
    control = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    try:
        with (tmp_path / "worker.log").open("wb") as log:
            command = [sys.executable, str(gated_worker), outcome, str(marker)]
            if outcome == "timeout":
                with pytest.raises(subprocess.TimeoutExpired):
                    run_owned_worker(command, cwd=tmp_path, env=os.environ.copy(), log=log, state=state, timeout=5)
            else:
                assert run_owned_worker(
                    command, cwd=tmp_path, env=os.environ.copy(), log=log, state=state, timeout=10
                ) == int(outcome)
        child = json.loads(marker.read_text())
        assert state["process_tree_stopped"]
        assert child["pid"] not in (control.pid, state["worker_pid"])
        assert control.poll() is None
        with socket.socket() as probe:
            probe.settimeout(1)
            assert probe.connect_ex(("127.0.0.1", child["port"])) != 0
    finally:
        control.terminate()
        control.wait(timeout=5)


@pytest.mark.skipif(os.name != "nt", reason="Windows process-tree ownership")
def test_assignment_failure_never_releases_worker_rust(tmp_path, gated_worker, monkeypatch):
    processes, state = [], {}
    popen = subprocess.Popen

    def start(*args, **kwargs):
        process = popen(*args, **kwargs)
        processes.append(process)
        return process

    def fail_assignment(self, pid):
        raise OSError("deliberate job assignment failure")

    monkeypatch.setattr(subprocess, "Popen", start)
    monkeypatch.setattr(OwnedProcessTree, "assign", fail_assignment)
    marker = tmp_path / "child.json"
    with (tmp_path / "worker.log").open("wb") as log:
        with pytest.raises(OSError, match="assignment failure"):
            run_owned_worker(
                [sys.executable, str(gated_worker), "0", str(marker)],
                cwd=tmp_path,
                env=os.environ.copy(),
                log=log,
                state=state,
                timeout=5,
            )
    assert not marker.exists()
    assert len(processes) == 1 and processes[0].poll() is not None


@pytest.mark.skipif(os.name != "nt", reason="Windows process-tree ownership")
def test_cleanup_failure_preserves_timeout_and_does_not_report_success_rust(tmp_path, gated_worker, monkeypatch):
    close = OwnedProcessTree.close

    def fail_close(self):
        close(self)
        raise OSError("deliberate process cleanup failure")

    monkeypatch.setattr(OwnedProcessTree, "close", fail_close)
    state = {}
    marker = tmp_path / "child.json"
    with (tmp_path / "worker.log").open("wb") as log:
        with pytest.raises(OSError, match="cleanup failure") as raised:
            run_owned_worker(
                [sys.executable, str(gated_worker), "timeout", str(marker)],
                cwd=tmp_path,
                env=os.environ.copy(),
                log=log,
                state=state,
                timeout=5,
            )
    assert isinstance(raised.value.__context__, subprocess.TimeoutExpired)
    assert state["outer_timeout"] and not state["process_tree_stopped"]
    child = json.loads(marker.read_text())
    with socket.socket() as probe:
        probe.settimeout(1)
        assert probe.connect_ex(("127.0.0.1", child["port"])) != 0


def test_worker_rejects_missing_ownership_release_rust():
    result = subprocess.run(
        [sys.executable, str(Path(run_toxiproxy.__file__)), "--worker"],
        input=b"",
        capture_output=True,
        timeout=10,
    )
    assert result.returncode != 0
    assert b"did not establish process-tree ownership" in result.stderr


def test_worker_accepts_snapshot_driver_revision_rust(tmp_path, monkeypatch):
    import azure
    import azure.cosmos
    from config.settings import TestSettings

    base = tmp_path / "snapshot"
    binary = base / "azure" / "cosmos" / "_rust.pyd"
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"test binary")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"binary_sha256": digest(binary)}))
    native = SimpleNamespace(__file__=str(binary), __rust_driver_commit__="unit-test-revision")
    monkeypatch.setattr(azure.cosmos, "_rust", native)
    monkeypatch.setattr(azure, "__path__", list(azure.__path__))
    monkeypatch.setattr(sys, "stdin", SimpleNamespace(buffer=io.BytesIO(b"1")))
    monkeypatch.setattr(TestSettings, "masterKey", "unit-test-key")
    monkeypatch.delenv("ACCOUNT_KEY", raising=False)
    execute = Mock(return_value=0)
    monkeypatch.setattr(pytest, "main", execute)
    assert run_toxiproxy.worker([str(base), str(manifest), str(tmp_path / "run")]) == 0
    execute.assert_called_once()


def test_runner_records_timeout_without_success_fallback_rust(tmp_path, monkeypatch):
    root, base = tmp_path / "package", tmp_path / "snapshot"
    for directory in (root, base):
        binary = directory / "azure" / "cosmos" / "_rust.pyd"
        binary.parent.mkdir(parents=True)
        binary.write_bytes(b"test binary")
    sources = [
        Path("tests") / "toxiproxy" / "test_toxiproxy_read.py",
        Path("tests") / "fault_injection" / "_regional_routing.py",
        Path("tests") / "config" / "fault_resources.py",
        Path("tests") / "config" / "clients.py",
        Path("tests") / "config" / "diagnostics.py",
        Path("tests") / "config" / "provisioning.py",
    ]
    for path in sources:
        source = root / path
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("# controlled test source\n", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "driver_source": "unit-test-driver-source",
                "binary_sha256": digest(base / "azure" / "cosmos" / "_rust.pyd"),
                "sources": {},
            }
        )
    )
    output = tmp_path / "run"
    failure = subprocess.TimeoutExpired("worker", 600)

    def timeout(command, *, state, **kwargs):
        state["process_tree_stopped"] = True
        raise failure

    monkeypatch.setattr(run_toxiproxy, "ROOT", root)
    monkeypatch.setattr(run_toxiproxy, "run_owned_worker", timeout)
    with pytest.raises(subprocess.TimeoutExpired) as raised:
        run_toxiproxy.main(
            [
                "--sdk-snapshot",
                str(base),
                "--manifest",
                str(manifest),
                "--output",
                str(output),
                "--selection",
                "no-opt-in",
            ]
        )
    assert raised.value is failure
    record = json.loads((output / "run.json").read_text())
    assert record["outer_timeout"] and record["exit_code"] is None
    assert record["process_tree_stopped"]
    assert set(record["test_hashes"]) == {str(path) for path in sources}
    for path in sources:
        assert (output / "test_sources" / path).read_bytes() == (root / path).read_bytes()
