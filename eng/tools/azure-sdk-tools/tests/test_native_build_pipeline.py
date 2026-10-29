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
import zipfile

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


def test_analysis_checkout_has_history_for_api_comparison():
    jobs = load_template("jobs/ci.yml")
    analyze = next(job for job in jobs["jobs"] if job.get("job") == "Analyze")
    assert analyze["steps"][0] == {
        "checkout": "self",
        "${{ if eq(variables['Build.Reason'], 'PullRequest') }}": {"fetchDepth": 0, "fetchTags": False},
    }


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


def test_documentation_forwards_host_rust_configuration():
    jobs = load_template("jobs/ci.yml")
    documentation = next(job for job in jobs["jobs"] if job.get("job") == "Build_Documentation")
    forwarded = documentation["steps"][-1]["parameters"]
    assert all(forwarded[name] == "${{ parameters." + name + " }}" for name in RUST_PARAMETERS[:3])
    assert "MsRustAdditionalTargets" not in forwarded

    extended = next(job for job in jobs["jobs"] if job.get("job") == "Build_Extended")
    assert "InstallMsRustToolchain" not in extended["steps"][-1]["parameters"]

    build = load_template("steps/build-extended-artifacts.yml")
    defaults = {parameter["name"]: parameter["default"] for parameter in build["parameters"]}
    assert defaults["InstallMsRustToolchain"] is False
    assert defaults["MsRustWorkingDirectory"] == ""
    assert defaults["MsRustToolchainFeed"] == ""

    rust_gate = "${{ if and(parameters.InstallMsRustToolchain, parameters.BuildDocs) }}"
    install = next(step[rust_gate][0] for step in build["steps"] if rust_gate in step)
    assert install["template"].endswith("install-msrust-toolchain.yml")
    assert install["parameters"] == {
        "ToolchainFeed": "${{ parameters.MsRustToolchainFeed }}",
        "WorkingDirectory": "${{ parameters.MsRustWorkingDirectory }}",
    }

    docs_group = next(step for step in build["steps"] if "${{ if eq(parameters.BuildDocs, 'true') }}" in step)
    docs = docs_group["${{ if eq(parameters.BuildDocs, 'true') }}"][0]
    assert build["steps"].index(next(step for step in build["steps"] if rust_gate in step)) < build["steps"].index(
        docs_group
    )
    assert docs["displayName"] == "Generate Docs"
    assert set(docs["env"]) == {RUST_GATE}
    assert docs["env"][RUST_GATE] == {
        "MSRUSTUP_ACCESS_TOKEN": "$(System.AccessToken)",
        "MSRUSTUP_FEED_URL": "$(MSRUSTUP_FEED_URL)",
        "CARGO_REGISTRIES_AZURE_SDK_FOR_RUST_PUBLIC_TOKEN": "$(CARGO_REGISTRIES_AZURE_SDK_FOR_RUST_PUBLIC_TOKEN)",
        "CARGO_REGISTRIES_AZURE_SDK_FOR_RUST_PUBLIC_CREDENTIAL_PROVIDER": (
            "$(CARGO_REGISTRIES_AZURE_SDK_FOR_RUST_PUBLIC_CREDENTIAL_PROVIDER)"
        ),
    }


@pytest.mark.parametrize("wheel_count", [0, 1, 5])
@pytest.mark.parametrize("existing_namespaces", [False, True])
def test_namespace_properties_accept_platform_wheels(tmp_path, wheel_count, existing_namespaces):
    package_name = "example-native-package"
    package_info = {"Name": package_name, "Version": "1.0.0", "ServiceDirectory": "example"}
    if existing_namespaces:
        package_info["Namespaces"] = ["outdated.namespace"]
    info_directory = tmp_path / "PackageInfo"
    info_directory.mkdir()
    info_path = info_directory / f"{package_name}.json"
    info_path.write_text(json.dumps(package_info))

    wheel_directory = tmp_path / package_name
    wheel_directory.mkdir()
    tags = (
        ["py3-none-any"]
        if wheel_count == 1
        else [
            "cp310-abi3-macosx_11_0_arm64",
            "cp310-abi3-manylinux_2_28_aarch64",
            "cp310-abi3-manylinux_2_28_x86_64",
            "cp310-abi3-win_amd64",
            "cp310-abi3-win_arm64",
        ][:wheel_count]
    )
    for tag in tags:
        with zipfile.ZipFile(wheel_directory / f"example_native_package-1.0.0-{tag}.whl", "w") as wheel:
            wheel.writestr("azure/example/__init__.py", "")
    with zipfile.ZipFile(wheel_directory / "example_native_package-0.9.0-py3-none-any.whl", "w") as wheel:
        wheel.writestr("azure/wrong_version/__init__.py", "")

    temp_directory = tmp_path / "temp"
    temp_directory.mkdir()
    result = run_powershell(
        """
        $ErrorActionPreference = 'Stop'
        . "$env:REPO_ROOT/eng/scripts/docs/Docs-ToC.ps1"
        function ShouldPublish { return $true }
        function LogError { param([string] $Message) Write-Host "ERROR: $Message" }
        $RepoRoot = $env:REPO_ROOT
        $ArtifactStagingDirectory = $env:ARTIFACT_DIRECTORY
        $artifacts = Get-ChildItem "$ArtifactStagingDirectory/PackageInfo" -File -Filter '*.json'
        $foundError = $false
        $ast = [System.Management.Automation.Language.Parser]::ParseFile(
            "$RepoRoot/eng/scripts/Save-Package-Namespaces-Property.ps1", [ref]$null, [ref]$null
        )
        $loop = $ast.Find({
            param($node)
            $node -is [System.Management.Automation.Language.ForEachStatementAst] -and
                $node.Variable.VariablePath.UserPath -eq 'packageInfoFile'
        }, $false)
        . ([scriptblock]::Create($loop.Extent.Text))
        if ($foundError) { exit 1 }
        """,
        REPO_ROOT=str(REPO_ROOT),
        ARTIFACT_DIRECTORY=str(tmp_path),
        TMPDIR=str(temp_directory),
        TMP=str(temp_directory),
        TEMP=str(temp_directory),
    )

    if wheel_count:
        assert result.returncode == 0, result.stderr
        assert json.loads(info_path.read_text())["Namespaces"] == ["azure.example"]
        assert "Cannot convert value to type System.String" not in result.stderr
    else:
        assert result.returncode == 1
        assert "Whl file for, example-native-package, was not found" in result.stdout
        assert json.loads(info_path.read_text()) == package_info


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
