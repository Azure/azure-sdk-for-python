# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location("regenerate_typespec", REPO_ROOT / "eng/scripts/regenerate_typespec.py")
regeneration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(regeneration)


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True, encoding="utf-8").stdout


def write(repo, name, content):
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def commit(repo):
    git(repo, "add", ".")
    git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "Test fixture")


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = tmp_path / "checkout with spaces"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "core.autocrlf", "false")
    write(root, ".gitignore", "node_modules/\nTempTypeSpecFiles/\n")
    # Exercise real subprocess execution and Git diff collection without network
    # access or an emitter install, using Python as the stand-in Node executable.
    cli = "eng/common/tsp-client/node_modules/@azure-tools/typespec-client-generator-cli/cmd/tsp-client.js"
    write(
        root,
        cli,
        """import sys
from pathlib import Path
assert sys.argv[1:] == ["update", "--skip-install", "--debug"], sys.argv
print("generation log", flush=True)
Path("generated.py").write_text("# regenerated\\n")
Path("new file.bin").write_bytes(b"\\x00\\x01\\x02")
Path("obsolete.py").unlink(missing_ok=True)
raise SystemExit(1 if Path.cwd().name == "azure-fail" else 0)
""",
    )
    monkeypatch.setattr(regeneration.shutil, "which", lambda command: sys.executable)
    return root


def add_client(repo, directory, config="directory: specification/example\ncommit: fixed-sha\nrepo: Azure/example\n"):
    write(repo, f"{directory}/tsp-location.yaml", config)
    return repo / directory


def test_discovery_includes_nested_clients_and_skips_valid_batch_wrappers(repo):
    first = add_client(repo, "sdk/service/azure-first")
    nested = add_client(repo, "sdk/service/azure-package/azure/internal")
    add_client(repo, "sdk/other/azure-batch", "batch:\n  - ./one\n  - ./two\n")
    one = add_client(repo, "sdk/other/azure-batch/one")
    two = add_client(repo, "sdk/other/azure-batch/two")
    add_client(repo, "sdk/service", "batch:\n  - ./azure-first\n")
    # Untracked copies and emitter temporary inputs must not become work items.
    git(repo, "add", ".")
    add_client(repo, "sdk/service/untracked")
    add_client(repo, "sdk/service/azure-first/TempTypeSpecFiles/copied")

    assert set(regeneration.discover_clients(repo)) == {first, nested, one, two}


@pytest.mark.parametrize(
    "config",
    [
        "batch: [\n",
        "batch:\n  - ./missing\n",
        "batch: []\n",
        "batch: not-a-list\n",
        "batch:\n  - 123\n",
        "batch:\n  - ./one\ndirectory: invalid-with-batch\n",
    ],
)
def test_invalid_configurations_are_attempted_not_silently_excluded(repo, config):
    parent = add_client(repo, "sdk/service/azure-batch", config)
    child = add_client(repo, "sdk/service/azure-batch/one")
    commit(repo)

    assert set(regeneration.discover_clients(repo)) == {parent, child}


def test_package_selection_includes_nested_clients_and_deduplicates(repo):
    first = add_client(repo, "sdk/service/azure-first")
    nested = add_client(repo, "sdk/service/azure-first/azure/internal")
    other = add_client(repo, "sdk/service/azure-other")
    clients = [first, nested, other]

    assert regeneration.select_clients(
        repo, clients, " sdk/service/azure-first, sdk/service/azure-first/azure/internal "
    ) == [first, nested]
    assert regeneration.select_clients(repo, clients, r"sdk\service\azure-first") == [first, nested]
    assert regeneration.select_clients(repo, clients, "*") == clients
    assert regeneration.select_clients(repo, clients, "sdk/service/azure-first/azure/internal") == [nested]


@pytest.mark.parametrize(
    "packages",
    [
        "",
        "sdk/service/azure-missing",
        "sdk/service/azure-first,",
        "sdk/service/azure-first,sdk/service/azure-missing",
        "sdk/service/azure-fir",
        "sdk/service",
        "../sdk/service/azure-first",
        "sdk/service/../service/azure-first",
        "/sdk/service/azure-first",
        "*,sdk/service/azure-first",
    ],
)
def test_invalid_package_selections_fail_explicitly(repo, packages):
    client = add_client(repo, "sdk/service/azure-first")
    with pytest.raises(ValueError, match="directory"):
        regeneration.select_clients(repo, [client], packages)


def test_selection_is_applied_before_sharding(repo, tmp_path):
    selected = [
        add_client(repo, "sdk/service/azure-selected/one"),
        add_client(repo, "sdk/service/azure-selected/two"),
    ]
    unselected = add_client(repo, "sdk/service/azure-other")
    commit(repo)
    output = tmp_path / "artifacts"

    assert regeneration.regenerate(repo, output, 1, 2, "sdk/service/azure-selected") == 0
    results = json.loads((output / "results.json").read_text())
    assert [result["directory"] for result in results] == [selected[1].relative_to(repo).as_posix()]
    assert not (selected[0] / "generated.py").exists()
    assert not (unselected / "generated.py").exists()


def test_cli_forwards_package_selection(repo, tmp_path, monkeypatch):
    output = tmp_path / "artifacts"
    arguments = []
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "regenerate_typespec.py",
            "--repo",
            str(repo),
            "--output",
            str(output),
            "--packages",
            "sdk/service/azure-only",
        ],
    )
    monkeypatch.setattr(regeneration, "regenerate", lambda *args: arguments.append(args) or 0)

    assert regeneration.main() == 0
    assert arguments == [(repo, output, 0, 1, "sdk/service/azure-only")]


def test_regeneration_continues_after_failures_and_captures_complete_patch(repo, tmp_path):
    failed = add_client(repo, "sdk/service/azure-fail")
    succeeded = add_client(repo, "sdk/service/azure-success")
    for client in (failed, succeeded):
        write(repo, str(client.relative_to(repo) / "generated.py"), "# original\n")
        write(repo, str(client.relative_to(repo) / "obsolete.py"), "# obsolete\n")
    commit(repo)
    original_locations = {client: (client / "tsp-location.yaml").read_bytes() for client in (failed, succeeded)}
    output = tmp_path / "artifacts"

    assert regeneration.regenerate(repo, output) == 1

    results = json.loads((output / "results.json").read_text())
    assert [result["exit_code"] for result in results] == [1, 0]
    assert [result["directory"] for result in results] == [
        "sdk/service/azure-fail",
        "sdk/service/azure-success",
    ]
    assert all("generation log" in (output / result["log"]).read_text() for result in results)
    patch = (output / "changes.patch").read_text()
    assert "+# regenerated" in patch
    assert "new file mode" in patch
    assert "GIT binary patch" in patch
    assert "deleted file mode" in patch
    assert "azure-success" in (output / "changes.txt").read_text()
    assert all(
        (client / "tsp-location.yaml").read_bytes() == original_locations[client] for client in original_locations
    )
    # The captured patch must be applicable to the original baseline.
    clean = tmp_path / "patch-check"
    git(tmp_path, "clone", "--quiet", str(repo), str(clean))
    git(clean, "apply", "--check", str(output / "changes.patch"))


@pytest.mark.parametrize("shard_index", range(8))
def test_shards_partition_all_clients_without_duplicates(repo, tmp_path, shard_index):
    clients = [add_client(repo, f"sdk/service/azure-{index:02d}") for index in range(19)]
    commit(repo)
    output = tmp_path / "artifacts"

    assert regeneration.regenerate(repo, output, shard_index, 8) == 0

    results = json.loads((output / "results.json").read_text())
    assert [result["directory"] for result in results] == [
        client.relative_to(repo).as_posix() for client in clients[shard_index::8]
    ]


def test_empty_shard_succeeds_with_empty_artifacts(repo, tmp_path):
    add_client(repo, "sdk/service/azure-only")
    commit(repo)
    output = tmp_path / "artifacts"

    assert regeneration.regenerate(repo, output, 7, 8) == 0
    assert json.loads((output / "results.json").read_text()) == []
    assert (output / "changes.patch").read_bytes() == b""


@pytest.mark.parametrize("shard_index,shard_count", [(-1, 8), (8, 8), (0, 0)])
def test_invalid_shards_are_rejected(repo, tmp_path, shard_index, shard_count):
    with pytest.raises(ValueError, match="shard"):
        regeneration.regenerate(repo, tmp_path / "artifacts", shard_index, shard_count)


def test_dirty_checkout_is_rejected_without_altering_user_files(repo, tmp_path):
    client = add_client(repo, "sdk/service/azure-example")
    commit(repo)
    original = b"# handwritten change\n"
    (client / "custom.py").write_bytes(original)

    with pytest.raises(ValueError, match="clean checkout"):
        regeneration.regenerate(repo, tmp_path / "artifacts")
    assert (client / "custom.py").read_bytes() == original


def test_output_inside_checkout_is_rejected(repo):
    with pytest.raises(ValueError, match="outside"):
        regeneration.regenerate(repo, repo / "artifacts")


def test_no_clients_is_an_error(repo, tmp_path):
    commit(repo)
    with pytest.raises(ValueError, match="No TypeSpec clients"):
        regeneration.regenerate(repo, tmp_path / "artifacts")


def test_missing_cli_is_an_actionable_error(repo, tmp_path):
    add_client(repo, "sdk/service/azure-example")
    commit(repo)
    cli = next(repo.glob("eng/common/tsp-client/node_modules/**/tsp-client.js"))
    cli.unlink()
    with pytest.raises(FileNotFoundError, match="npm ci"):
        regeneration.regenerate(repo, tmp_path / "artifacts")


def test_pipeline_uses_pinned_dependencies_and_publishes_failed_job_artifacts():
    pipeline = yaml.safe_load((REPO_ROOT / "eng/pipelines/typespec-regeneration.yml").read_text())
    for trigger in ("trigger", "pr"):
        assert "eng/emitter-package.json" in pipeline[trigger]["paths"]["include"]
        assert "eng/emitter-package-lock.json" in pipeline[trigger]["paths"]["include"]
    assert pipeline["extends"]["template"].endswith("1es-redirect.yml")
    job = pipeline["extends"]["parameters"]["stages"][0]["jobs"][0]
    all_gate = "${{ if eq(parameters.PackageDirectories, '*') }}"
    matrix = job["strategy"]["matrix"]
    assert matrix["Batch0"] == {"ShardIndex": 0}
    assert sorted(batch["ShardIndex"] for batch in matrix[all_gate].values()) == list(range(1, 8))
    assert job["variables"][all_gate]["ShardCount"] == 8
    assert job["variables"]["${{ else }}"]["ShardCount"] == 1
    scripts = [step["script"] for step in job["steps"] if "script" in step]
    assert "npm ci --prefix eng/common/tsp-client" in scripts
    assert "npm exec --prefix eng/common/tsp-client --no -- tsp-client install-dependencies" in scripts
    assert "--shard-count $(ShardCount)" in scripts[-1]
    assert "--shard-index $(ShardIndex)" in scripts[-1]
    assert '--packages "$TYPESPEC_REGENERATION_PACKAGES"' in scripts[-1]
    assert job["steps"][-1]["env"]["TYPESPEC_REGENERATION_PACKAGES"] == "${{ parameters.PackageDirectories }}"
    output = job["templateContext"]["outputs"][0]
    assert output["condition"] == "succeededOrFailed()"
    assert "$(ShardIndex)" in output["artifactName"]


def test_pipeline_default_is_a_small_existing_representative_set():
    pipeline = yaml.safe_load((REPO_ROOT / "eng/pipelines/typespec-regeneration.yml").read_text())
    default = next(
        parameter["default"] for parameter in pipeline["parameters"] if parameter["name"] == "PackageDirectories"
    )
    assert default.split(",") == [
        "sdk/advisor/azure-mgmt-advisor",
        "sdk/appconfiguration/azure-appconfiguration",
        "sdk/agentserver/azure-ai-agentserver-responses/type_spec",
    ]
    clients = regeneration.select_clients(REPO_ROOT, regeneration.discover_clients(REPO_ROOT), default)
    assert [client.relative_to(REPO_ROOT).as_posix() for client in clients] == sorted(default.split(","))
