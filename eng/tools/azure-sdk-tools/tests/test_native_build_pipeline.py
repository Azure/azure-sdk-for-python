# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json
import os
from pathlib import Path
import re
import shutil
import subprocess

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
TEMPLATES = REPO_ROOT / "eng" / "pipelines" / "templates"
RUST_GATE = "${{ if parameters.InstallMsRustToolchain }}"
RUST_PARAMETERS = (
    "InstallMsRustToolchain",
    "MsRustWorkingDirectory",
    "MsRustToolchainFeed",
    "MsRustAdditionalTargets",
)


def load_template(relative_path):
    return yaml.safe_load((TEMPLATES / relative_path).read_text())


def run_powershell(script, **environment):
    powershell = shutil.which("pwsh")
    if not powershell:
        pytest.skip("PowerShell is required to execute pipeline scripts")
    return subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-Command", script],
        env={**os.environ, **environment},
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def test_rust_support_is_disabled_by_default_and_forwarded():
    archetype = load_template("stages/archetype-sdk-client.yml")
    jobs = load_template("jobs/ci.yml")
    build = load_template("steps/build-package-artifacts.yml")
    for template in (archetype, jobs, build):
        defaults = {
            parameter["name"]: parameter["default"]
            for parameter in template["parameters"]
            if parameter["name"] in RUST_PARAMETERS
        }
        assert defaults["InstallMsRustToolchain"] is False
        assert all(defaults[name] == "" for name in RUST_PARAMETERS[1:])

    build_stage = next(stage for stage in archetype["extends"]["parameters"]["stages"] if stage.get("stage") == "Build")
    forwarded = build_stage["jobs"][0]["parameters"]
    assert all(forwarded[name] == "${{ parameters." + name + " }}" for name in RUST_PARAMETERS)

    for job in jobs["jobs"]:
        if job.get("job") not in ("Build_Linux", "Build_Windows", "Build_MacOS"):
            continue
        assert job[RUST_GATE]["timeoutInMinutes"] == 240
        assert job["${{ else }}"]["timeoutInMinutes"] == 90
        forwarded = job["steps"][0]["parameters"]
        assert all(forwarded[name] == "${{ parameters." + name + " }}" for name in RUST_PARAMETERS)


def test_rust_credentials_and_target_setup_are_opt_in():
    build = load_template("steps/build-package-artifacts.yml")
    install = next(step[RUST_GATE][0] for step in build["steps"] if RUST_GATE in step)
    assert install["template"].endswith("install-msrust-toolchain.yml")
    assert install["parameters"]["Condition"] == "and(succeeded(), eq(variables['ENABLE_EXTENSION_BUILD'], 'true'))"
    assert install["parameters"]["ToolchainFeed"] == "${{ parameters.MsRustToolchainFeed }}"
    assert install["parameters"]["${{ if eq(parameters.ArtifactSuffix, 'windows') }}"] == {
        "AdditionalTargets": "${{ parameters.MsRustAdditionalTargets }}"
    }

    generate = next(step for step in build["steps"] if step.get("displayName") == "Generate Packages")
    assert generate[RUST_GATE]["timeoutInMinutes"] == 210
    assert generate["${{ else }}"]["timeoutInMinutes"] == 80
    assert generate["env"]["LOGLEVEL"] == "$(SDK_BUILD_LOGLEVEL)"
    assert generate["env"][RUST_GATE]["MSRUSTUP_ACCESS_TOKEN"] == "$(System.AccessToken)"
    assert "MSRUSTUP_ACCESS_TOKEN" not in generate["env"]

    installer = load_template("steps/install-msrust-toolchain.yml")
    assert all(step["condition"] == "${{ parameters.Condition }}" for step in installer["steps"])
    cargo_auth = next(step for step in installer["steps"] if step.get("task") == "CargoAuthenticate@0")
    assert cargo_auth["env"] == {"SYSTEM_ACCESSTOKEN": "$(VSS_NUGET_ACCESSTOKEN)"}

    provision = next(
        step for step in build["steps"] if step.get("displayName") == "Pre-provision CPython for cibuildwheel"
    )
    assert provision["env"]["INSTALL_MS_RUST_TOOLCHAIN"] == "${{ format('{0}', parameters.InstallMsRustToolchain) }}"


@pytest.mark.parametrize("sign_binaries", [False, True])
def test_platform_selection_uses_artifact_opt_in(tmp_path, sign_binaries):
    package_info = {"Name": "example-native-package", "ArtifactDetails": {"signBinaries": sign_binaries}}
    (tmp_path / "example-native-package.json").write_text(json.dumps(package_info))
    resolver = load_template("steps/resolve-build-platforms.yml")["steps"][0]["pwsh"]
    resolver = resolver.replace("${{ parameters.PackagePropertiesFolder }}", str(tmp_path))

    result = run_powershell(resolver)

    assert result.returncode == 0, result.stderr
    assert ("variable=ENABLE_EXTENSION_BUILD]true" in result.stdout) is sign_binaries
    assert f"variable=SDK_BUILD_LOGLEVEL]{'DEBUG' if sign_binaries else 'INFO'}" in result.stdout


@pytest.mark.parametrize("enabled", [False, True])
def test_container_forwarding_preserves_non_rust_builds(enabled):
    build = load_template("steps/build-package-artifacts.yml")
    forwarding = next(
        step for step in build["steps"] if step.get("displayName") == "Forward build environment to cibuildwheel"
    )
    extra = forwarding["env"][RUST_GATE]["RUST_ENVIRONMENT_PASS"] if enabled else ""

    result = run_powershell(forwarding["pwsh"], RUST_ENVIRONMENT_PASS=extra)

    assert result.returncode == 0, result.stderr
    assert "variable=CIBW_ENVIRONMENT_PASS_LINUX]PIP_INDEX_URL" in result.stdout
    assert ("MSRUSTUP_ACCESS_TOKEN" in result.stdout) is enabled
    assert ("CARGO_REGISTRIES_AZURE_SDK_FOR_RUST_PUBLIC_TOKEN" in result.stdout) is enabled


@pytest.mark.parametrize("missing", ["feed", "directory", "toolchain"])
def test_rust_installation_requires_explicit_configuration(tmp_path, missing):
    validation = load_template("steps/install-msrust-toolchain.yml")["steps"][0]["pwsh"]
    if missing != "toolchain":
        (tmp_path / "rust-toolchain.toml").write_text('[toolchain]\nchannel = "ms-prod-1.97"\n')
    result = run_powershell(
        validation,
        RUST_TOOLCHAIN_FEED=(
            "" if missing == "feed" else "https://pkgs.dev.azure.com/azure-sdk/_packaging/example/nuget/v3/index.json"
        ),
        RUST_WORKING_DIRECTORY="" if missing == "directory" else str(tmp_path),
    )
    assert result.returncode != 0


def test_rust_installation_accepts_explicit_configuration(tmp_path):
    validation = load_template("steps/install-msrust-toolchain.yml")["steps"][0]["pwsh"]
    (tmp_path / "rust-toolchain.toml").write_text('[toolchain]\nchannel = "ms-prod-1.97"\n')
    result = run_powershell(
        validation,
        RUST_TOOLCHAIN_FEED="https://pkgs.dev.azure.com/azure-sdk/_packaging/example/nuget/v3/index.json",
        RUST_WORKING_DIRECTORY=str(tmp_path),
    )
    assert result.returncode == 0, result.stderr


def test_cargo_feed_configuration_does_not_overwrite_existing_config(tmp_path):
    configure = load_template("steps/install-msrust-toolchain.yml")["steps"][2]["pwsh"]
    feed = "sparse+https://pkgs.dev.azure.com/azure-sdk/public/_packaging/example/Cargo/index/"
    result = run_powershell(
        configure, CARGO_HOME=str(tmp_path), CARGO_FEED_URL=feed, RUST_TOOLCHAIN_FEED="example-feed"
    )
    assert result.returncode == 0, result.stderr
    config = (tmp_path / "config.toml").read_text()
    assert feed in config
    assert 'replace-with = "azure-sdk-for-rust-public"' in config
    assert "token" not in config
    assert "variable=CARGO_REGISTRIES_AZURE_SDK_FOR_RUST_PUBLIC_INDEX]" + feed in result.stdout

    result = run_powershell(
        configure, CARGO_HOME=str(tmp_path), CARGO_FEED_URL=feed, RUST_TOOLCHAIN_FEED="example-feed"
    )
    assert result.returncode != 0
    assert (tmp_path / "config.toml").read_text() == config


def test_cargo_feed_configuration_uses_default_cargo_home(tmp_path):
    configure = load_template("steps/install-msrust-toolchain.yml")["steps"][2]["pwsh"]
    feed = "sparse+https://pkgs.dev.azure.com/azure-sdk/public/_packaging/example/Cargo/index/"

    result = run_powershell(
        configure,
        CARGO_HOME="",
        CARGO_FEED_URL=feed,
        HOME=str(tmp_path),
        RUST_TOOLCHAIN_FEED="example-feed",
    )

    assert result.returncode == 0, result.stderr
    config = tmp_path / ".cargo" / "config.toml"
    assert config.is_file()
    assert feed in config.read_text()


def test_build_powershell_scripts_parse():
    for template_path in (
        "steps/install-msrust-toolchain.yml",
        "steps/build-package-artifacts.yml",
        "steps/resolve-build-platforms.yml",
    ):
        template = load_template(template_path)
        for step in template["steps"]:
            if "pwsh" not in step:
                continue
            # Azure expands template expressions and the command-valued PIP_EXE macro before parsing.
            script = re.sub(r"\$\{\{.*?\}\}", "example", step["pwsh"])
            script = script.replace("$(PIP_EXE)", "python -m pip")
            result = run_powershell(
                """
                $tokens = $null
                $errors = $null
                [System.Management.Automation.Language.Parser]::ParseInput(
                    $env:SCRIPT, [ref]$tokens, [ref]$errors
                ) | Out-Null
                if ($errors.Count) {
                    $errors | ForEach-Object { Write-Error $_.Message }
                    exit 1
                }
                """,
                SCRIPT=script,
            )
            assert result.returncode == 0, f"{template_path}: {step['displayName']}: {result.stderr}"


def release_publish_steps():
    template = load_template("stages/release-artifact.yml")
    gate = "${{if ne(parameters.Artifact.skipPublishPackage, 'true')}}"
    deployment = next(job[gate][0] for job in template["stages"][0]["jobs"] if gate in job)
    return deployment["strategy"]["runOnce"]["deploy"]["steps"]


def render_publish_script(script, *, workspace, skip_sdist):
    parameters = {
        "Artifact.name": "azure-cosmos",
        "ArtifactName": "packages_azurecosmos_signed",
        "Artifact.skipPublishSdist": skip_sdist,
        "PackagePath": str(workspace / "packages_azurecosmos_signed" / "azure-cosmos"),
    }
    script = re.sub(
        r"\$\{\{\s*parameters\.([\w.]+)\s*\}\}",
        lambda match: parameters[match.group(1)],
        script,
    )
    return (
        script.replace("$(Pipeline.Workspace)", str(workspace))
        .replace("$(DevFeedName)", "test-feed")
        .replace("$(PYPIRC_PATH)", str(workspace / "pypirc"))
    )


def test_only_cosmos_opts_out_of_source_distribution_publication():
    ci = yaml.safe_load((REPO_ROOT / "sdk" / "cosmos" / "ci.yml").read_text())
    artifacts = {artifact["name"]: artifact for artifact in ci["extends"]["parameters"]["Artifacts"]}
    assert artifacts["azure-cosmos"]["skipPublishSdist"] is True
    assert not artifacts["azure-mgmt-cosmosdb"].get("skipPublishSdist", False)


@pytest.mark.parametrize("skip_sdist", ["", "False", "True", "true"])
def test_esrp_staging_obeys_source_publication_policy(tmp_path, skip_sdist):
    source = tmp_path / "packages_azurecosmos_signed" / "azure-cosmos"
    source.mkdir(parents=True)
    wheel = "azure_cosmos-5.0.0-cp310-abi3-win_amd64.whl"
    sdist = "azure_cosmos-5.0.0.tar.gz"
    for name in (wheel, sdist, "metadata.json"):
        (source / name).write_text(name)
    branch = "${{ if eq(parameters.PublicFeed, 'PyPi') }}"
    steps = next(step[branch] for step in release_publish_steps() if branch in step)
    script = next(step["pwsh"] for step in steps if step.get("displayName") == "Isolate files for ESRP Publish")

    result = run_powershell(render_publish_script(script, workspace=tmp_path, skip_sdist=skip_sdist))

    assert result.returncode == 0, result.stderr
    staged = tmp_path / "esrp-release" / "packages_azurecosmos_signed" / "azure-cosmos"
    assert {path.name for path in staged.iterdir()} == ({wheel} if skip_sdist.lower() == "true" else {wheel, sdist})
    assert (source / sdist).read_text() == sdist


def test_wheels_only_esrp_staging_rejects_a_stale_source_archive(tmp_path):
    source = tmp_path / "packages_azurecosmos_signed" / "azure-cosmos"
    source.mkdir(parents=True)
    (source / "azure_cosmos-5.0.0-cp310-abi3-win_amd64.whl").touch()
    staged = tmp_path / "esrp-release" / "packages_azurecosmos_signed" / "azure-cosmos"
    staged.mkdir(parents=True)
    (staged / "azure_cosmos-5.0.0.tar.gz").touch()
    branch = "${{ if eq(parameters.PublicFeed, 'PyPi') }}"
    steps = next(step[branch] for step in release_publish_steps() if branch in step)
    script = next(step["pwsh"] for step in steps if step.get("displayName") == "Isolate files for ESRP Publish")

    result = run_powershell(render_publish_script(script, workspace=tmp_path, skip_sdist="True"))

    assert result.returncode != 0
    assert "Source distributions must not be staged" in result.stderr


def test_release_feed_source_uploads_require_explicit_template_branch():
    deployment = release_publish_steps()
    public_branch = "${{ if ne(parameters.PublicFeed, 'PyPi') }}"
    public_steps = next(step[public_branch] for step in deployment if public_branch in step)
    source_gate = "${{ if ne(parameters.Artifact.skipPublishSdist, 'true') }}"
    for steps in (deployment, public_steps):
        wheel_scripts = [step["script"] for step in steps if "script" in step and "twine upload" in step["script"]]
        assert len(wheel_scripts) == 1
        assert "*.whl" in wheel_scripts[0]
        assert "*.tar.gz" not in wheel_scripts[0]
        source_steps = [step[source_gate] for step in steps if source_gate in step]
        assert len(source_steps) == 1
        assert len(source_steps[0]) == 1
        assert "*.tar.gz" in source_steps[0][0]["script"]
        assert "set -e" in source_steps[0][0]["script"]


@pytest.mark.parametrize("skip_sdist", ["", "False", "True", "true"])
def test_alpha_upload_obeys_source_publication_policy(tmp_path, skip_sdist):
    source = tmp_path / "packages_azurecosmos_signed" / "azure-cosmos"
    source.mkdir(parents=True)
    for name in ("azure_cosmos-5.0.0a1-cp310-abi3-win_amd64.whl", "azure_cosmos-5.0.0a1.tar.gz"):
        (source / name).touch()
    script = load_template("steps/publish-alpha-package.yml")["steps"][0]["pwsh"]
    script = render_publish_script(script, workspace=tmp_path, skip_sdist=skip_sdist)
    # Capture exact upload arguments without invoking twine or contacting any feed.
    result = run_powershell(
        'function twine { Write-Output ("UPLOAD: " + ($args -join " ")) }\n' + script,
        BUILDTARGETINGSTRING="azure-cosmos",
    )

    assert result.returncode == 0, result.stderr
    uploads = [line for line in result.stdout.splitlines() if line.startswith("UPLOAD: ")]
    assert len(uploads) == (1 if skip_sdist.lower() == "true" else 2)
    assert uploads[0].endswith("/*-*a*.whl")
    if skip_sdist.lower() != "true":
        assert uploads[1].endswith("/*-*a*.tar.gz")


@pytest.mark.parametrize("existing_namespaces", [False, True])
@pytest.mark.parametrize("scenario", ["pure-python", "platform-wheels", "dev-version", "missing", "wrong-version"])
def test_package_namespaces_inspect_one_exact_version_wheel(tmp_path, existing_namespaces, scenario):
    from zipfile import ZipFile

    repository = tmp_path / "repo"
    scripts = repository / "eng" / "scripts"
    helpers = repository / "eng" / "common" / "scripts" / "Helpers"
    service = repository / "sdk" / "example"
    packages = tmp_path / "artifacts" / "PackageInfo"
    wheels = tmp_path / "artifacts" / "azure-example"
    temporary = tmp_path / "temp"
    for directory in (scripts, helpers, service, packages, wheels, temporary):
        directory.mkdir(parents=True)
    shutil.copyfile(
        REPO_ROOT / "eng" / "scripts" / "Save-Package-Namespaces-Property.ps1",
        scripts / "Save-Package-Namespaces-Property.ps1",
    )
    shutil.copyfile(REPO_ROOT / "eng" / "scripts" / "docs" / "Docs-ToC.ps1", scripts / "Docs-ToC.ps1")
    # Keep module installation and YAML parsing offline; run the real namespace
    # updater and wheel inspection against complete temporary artifact trees.
    (helpers / "PSModule-Helpers.ps1").write_text(
        'function Install-ModuleIfNotInstalled { "Microsoft.PowerShell.Utility" }\n'
    )
    (helpers.parent / "common.ps1").write_text("""
$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
. (Join-Path $RepoRoot 'eng/scripts/Docs-ToC.ps1')
function ConvertFrom-Yaml($Content) { ConvertFrom-Json -InputObject $Content -AsHashtable }
function LogError($Message) { Write-Host "ERROR: $Message" }
function LogWarning($Message) { Write-Warning $Message }
""")
    (service / "ci.yml").write_text(json.dumps({"extends": {"parameters": {"Artifacts": [{"name": "azure-example"}]}}}))
    properties = {"Name": "azure-example", "ServiceDirectory": "example", "Version": "1.0.0"}
    if existing_namespaces:
        properties["Namespaces"] = ["old.namespace"]
    if scenario == "dev-version":
        properties["DevVersion"] = "1.0.0a20261022"
    info = packages / "azure-example.json"
    info.write_text(json.dumps(properties))
    version = properties.get("DevVersion", properties["Version"])
    if scenario == "wrong-version":
        version += "1"
    tags = ["py3-none-any"]
    if scenario in ("platform-wheels", "dev-version"):
        tags = ["cp310-abi3-win_amd64", "cp310-abi3-win_arm64", "cp310-abi3-manylinux_2_28_x86_64"]
    if scenario != "missing":
        for tag in tags:
            with ZipFile(wheels / f"azure_example-{version}-{tag}.whl", "w") as archive:
                archive.writestr("azure/__init__.py", "")
                archive.writestr("azure/example/__init__.py", "")
                archive.writestr("azure/example/_internal/__init__.py", "")

    result = run_powershell(
        "& (Join-Path $env:TEST_SCRIPTS 'Save-Package-Namespaces-Property.ps1') "
        "-ArtifactStagingDirectory $env:TEST_ARTIFACTS",
        TEST_SCRIPTS=str(scripts),
        TEST_ARTIFACTS=str(packages.parent),
        TEMP=str(temporary),
        TMP=str(temporary),
        TMPDIR=str(temporary),
    )

    if scenario in ("missing", "wrong-version"):
        assert result.returncode == 1, result.stdout + result.stderr
        assert "was not found" in result.stdout
        assert json.loads(info.read_text(encoding="utf-8-sig")) == properties
    else:
        assert result.returncode == 0, result.stdout + result.stderr
        assert json.loads(info.read_text(encoding="utf-8-sig")) == {
            **properties,
            "Namespaces": ["azure.example"],
        }
