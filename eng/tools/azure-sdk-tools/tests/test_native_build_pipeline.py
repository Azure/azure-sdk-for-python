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
import sys

import pytest
import yaml

from ci_tools.build import create_package
from ci_tools.parsing import ParsedSetup
from ci_tools.parsing.parse_functions import get_pyproject_dict


REPO_ROOT = Path(__file__).resolve().parents[4]
TEMPLATES = REPO_ROOT / "eng" / "pipelines" / "templates"
RUST_FIXTURE = REPO_ROOT / "sdk" / "template" / "azure-template-three"
GENERIC_PR_EXCLUSION_SCRIPT = (
    REPO_ROOT / "eng" / "scripts" / "Exclude-RustTemplateFixtureFromGenericPR.ps1"
)
RUST_GATE = "${{ if parameters.InstallMsRustToolchain }}"
RUST_TOOLCHAIN_FEED = (
    "https://pkgs.dev.azure.com/azure-sdk/_packaging/azure-sdk-for-rust-org-test/nuget/v3/index.json"
)
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
        assert defaults["MsRustWorkingDirectory"] == ""
        assert defaults["MsRustToolchainFeed"] == ""
        assert defaults["MsRustAdditionalTargets"] == ""

    installer = load_template("steps/install-msrust-toolchain.yml")
    assert next(
        parameter["default"] for parameter in installer["parameters"] if parameter["name"] == "ToolchainFeed"
    ) == ""

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


def test_rust_template_is_always_on_and_uses_cosmos_prototype_settings():
    pipeline = yaml.safe_load((REPO_ROOT / "sdk" / "template" / "ci.yml").read_text())
    assert all(parameter["name"] != "EnableRustFixture" for parameter in pipeline["parameters"])
    parameters = pipeline["extends"]["parameters"]
    assert "BuildTargetingString" not in parameters
    assert parameters["InstallMsRustToolchain"] is True
    assert parameters["MsRustWorkingDirectory"] == (
        "$(Build.SourcesDirectory)/sdk/template/azure-template-three"
    )
    assert parameters["MsRustToolchainFeed"] == RUST_TOOLCHAIN_FEED
    assert parameters["MsRustAdditionalTargets"] == "aarch64-pc-windows-msvc"
    assert "variables" not in pipeline
    artifact_entries = parameters["Artifacts"]
    assert [artifact["name"] for artifact in artifact_entries] == [
        "azure-template",
        "azure-template-two",
        "azure-template-three",
    ]
    rust = artifact_entries[2]
    assert rust["name"] == "azure-template-three"
    assert rust["signBinaries"] is True
    assert "skipPublishDevFeed" not in rust

    pullrequest = yaml.safe_load((REPO_ROOT / "eng" / "pipelines" / "pullrequest.yml").read_text())
    assert "sdk/template/azure-template-three/" in pullrequest["extends"]["parameters"]["ExcludePaths"]
    live = yaml.safe_load((REPO_ROOT / "sdk" / "template" / "tests.yml").read_text())
    assert live["extends"]["parameters"]["BuildTargetingString"] == "azure-template|azure-template-two"


@pytest.mark.parametrize(
    "targeting,expected",
    [
        ("azure-*", ["azure-template", "azure-template-two"]),
        ("azure-template*", ["azure-template", "azure-template-two"]),
        ("azure-template-three", []),
        ("azure-template-two", ["azure-template-two"]),
        ("missing-*", []),
    ],
)
def test_generic_pr_package_targeting_excludes_rust_fixture(tmp_path, targeting, expected):
    for name in ("azure-template", "azure-template-two", "azure-template-three"):
        (tmp_path / f"{name}.json").write_text(json.dumps({"IncludedForValidation": False}))
    script = REPO_ROOT / "eng" / "scripts" / "resolve-package-info.ps1"
    result = run_powershell(
        """
        $ErrorActionPreference = 'Stop'
        & $env:FILTER_SCRIPT -PackagePropertiesFolder $env:PACKAGE_INFO
        & $env:RESOLVE_SCRIPT -ParameterTargetingStringSetting $env:TARGETS -PackagePropertiesFolder $env:PACKAGE_INFO
        """,
        FILTER_SCRIPT=str(GENERIC_PR_EXCLUSION_SCRIPT),
        RESOLVE_SCRIPT=str(script),
        TARGETS=targeting,
        PACKAGE_INFO=str(tmp_path),
        BUILDTARGETINGSTRING="",
        TARGETINGSTRING="",
    )
    assert result.returncode == 0, result.stderr
    assert sorted(path.stem for path in tmp_path.glob("*.json")) == expected
    output = next(line for line in result.stdout.splitlines() if "variable=TargetingString;]" in line)
    targets = output.split("]", 1)[1]
    assert sorted(targets.split(",")) == (expected or ["null"])


def run_generic_pr_exclusion(tmp_path, **environment):
    return run_powershell(
        """
        $ErrorView = 'NormalView'
        & $env:FILTER_SCRIPT -PackagePropertiesFolder $env:PACKAGE_INFO
        """,
        **{
            "FILTER_SCRIPT": str(GENERIC_PR_EXCLUSION_SCRIPT),
            "PACKAGE_INFO": str(tmp_path),
            "TARGETINGSTRING": "",
            **environment,
        },
    )


@pytest.mark.parametrize(
    "targets,expected",
    [
        ("azure-template,azure-template-three,azure-template-two", "azure-template,azure-template-two"),
        (" azure-template-three , azure-cosmos ", "azure-cosmos"),
        ("azure-template-three", "null"),
        ("azure-cosmos", "azure-cosmos"),
    ],
)
def test_generic_pr_exclusion_applies_to_preselected_matrix_batches(tmp_path, targets, expected):
    for name in ("azure-template", "azure-template-two", "azure-template-three", "azure-cosmos"):
        (tmp_path / f"{name}.json").write_text("{}")
    result = run_generic_pr_exclusion(tmp_path, TARGETINGSTRING=targets)
    assert result.returncode == 0, result.stderr
    assert f"variable=TargetingString;]{expected}" in result.stdout
    assert not (tmp_path / "azure-template-three.json").exists()
    assert (tmp_path / "azure-cosmos.json").exists()

def test_generic_pr_exclusion_precedes_target_resolution_and_matrix_generation():
    targeting = load_template("steps/resolve-package-targeting.yml")["steps"]
    assert all("Filter-RustTemplateFixture.ps1" not in step.get("pwsh", "") for step in targeting)

    build = load_template("steps/build-package-artifacts.yml")["steps"]
    filter_index = next(
        index
        for index, step in enumerate(build)
        if "${{ if eq(parameters.ServiceDirectory, 'auto') }}" in step
    )
    filter_step = build[filter_index]["${{ if eq(parameters.ServiceDirectory, 'auto') }}"][0]
    assert "Exclude-RustTemplateFixtureFromGenericPR.ps1" in filter_step["pwsh"]
    resolve_index = next(
        index
        for index, step in enumerate(build)
        if step.get("template", "").endswith("/steps/resolve-package-targeting.yml")
    )
    assert filter_index < resolve_index

    jobs = load_template("jobs/ci.yml")["jobs"]
    matrix = next(job for job in jobs if job.get("template", "").endswith("/jobs/generate-job-matrix.yml"))
    steps = matrix["parameters"]["${{ if eq(parameters.ServiceDirectory, 'auto') }}"]["PreGenerationSteps"]
    assert steps[-2]["template"].endswith("/steps/save-package-properties.yml")
    assert "Exclude-RustTemplateFixtureFromGenericPR.ps1" in steps[-1]["pwsh"]
    assert '-PackagePropertiesFolder "$(Build.ArtifactStagingDirectory)/PackageInfo"' in steps[-1]["pwsh"]
    assert "condition" not in steps[-1]


@pytest.mark.parametrize("indirect", [False, True])
def test_pr_matrix_batches_exclude_rust_fixture(tmp_path, indirect):
    package_info = tmp_path / "PackageInfo"
    package_info.mkdir()
    for name in ("azure-template", "azure-template-two", "azure-template-three", "azure-cosmos"):
        (package_info / f"{name}.json").write_text(
            json.dumps(
                {
                    "ArtifactName": name,
                    "IncludedForValidation": indirect,
                    "CIParameters": {"CIMatrixConfigs": None},
                }
            )
        )
    config = tmp_path / "matrix.json"
    archetype = load_template("stages/archetype-sdk-client.yml")
    config.write_text(
        json.dumps(
            next(parameter["default"] for parameter in archetype["parameters"] if parameter["name"] == "MatrixConfigs")
        )
    )
    result = run_powershell(
        """
        $ErrorActionPreference = 'Stop'
        & $env:FILTER_SCRIPT -PackagePropertiesFolder $env:PACKAGE_INFO
        & $env:MATRIX_SCRIPT -PackagePropertiesFolder $env:PACKAGE_INFO `
            -PRMatrixFile $env:MATRIX_CONFIG -PRMatrixSetting TargetingString `
            -Filters 'container=^$', 'SupportedClouds=^$|Public', 'Pool=.*Linux.*Pool$' -CI
        """,
        FILTER_SCRIPT=str(GENERIC_PR_EXCLUSION_SCRIPT),
        MATRIX_SCRIPT=str(REPO_ROOT / "eng" / "common" / "scripts" / "job-matrix" / "Create-PrJobMatrix.ps1"),
        PACKAGE_INFO=str(package_info),
        MATRIX_CONFIG=str(config),
        TARGETINGSTRING="",
        BUILD_REASON="PullRequest",
        SETDEVVERSION="false",
        LINUXVMIMAGE="ubuntu-24.04",
        LINUXPOOL="AzureSDKLinuxPool",
        WINDOWSVMIMAGE="windows-2022",
        WINDOWSPOOL="AzureSDKWindowsPool",
        MACVMIMAGE="macOS-15",
        MACPOOL="AzureSDKMacPool",
    )
    assert result.returncode == 0, result.stderr
    output = next(
        line
        for line in result.stdout.splitlines()
        if line.startswith("##vso[task.setVariable variable=matrix;isOutput=true]")
    )
    matrix = json.loads(output.split("]", 1)[1])
    assert matrix
    targets = {name for job in matrix.values() for name in job["TargetingString"].split(",")}
    assert targets == {"azure-template", "azure-template-two", "azure-cosmos"}


def run_pr_fixture_discovery(tmp_path, changed, include_cosmos=False):
    diff = tmp_path / "diff.json"
    diff.write_text(
        json.dumps(
            {
                "ChangedFiles": changed,
                "ExcludePaths": ["sdk/template/azure-template-three/", "sdk/cosmos/"],
            }
        )
    )
    source = (REPO_ROOT / "eng" / "common" / "scripts" / "Package-Properties.ps1").read_text()
    helpers = source[source.index("function Get-TriggerPaths(") : source.index("function Get-AllPkgProperties (")]
    package_info = tmp_path / "PackageInfo"
    package_info.mkdir()
    return run_powershell(
        """
        $ErrorActionPreference = 'Stop'
        $RepoRoot = $env:REPO_ROOT
        function LogInfo($message) {}
        function Get-AllPkgProperties {
            foreach ($name in @('azure-template', 'azure-template-two', 'azure-template-three')) {
                [PSCustomObject]@{
                    Name = $name
                    DirectoryPath = Join-Path $RepoRoot "sdk/template/$name"
                    ServiceDirectory = 'template'
                    ArtifactDetails = @{ triggeringPaths = @('sdk/template/ci.yml') }
                    AdditionalValidationPackages = @(
                        if ($env:INCLUDE_COSMOS -eq 'true' -and $name -eq 'azure-template-two') {
                            'sdk/cosmos/azure-cosmos'
                        }
                    )
                    IncludedForValidation = $false
                }
            }
            if ($env:INCLUDE_COSMOS -eq 'true') {
                [PSCustomObject]@{
                    Name = 'azure-cosmos'
                    DirectoryPath = Join-Path $RepoRoot 'sdk/cosmos/azure-cosmos'
                    ServiceDirectory = 'cosmos'
                    ArtifactDetails = @{ triggeringPaths = @('sdk/cosmos/ci.yml') }
                    AdditionalValidationPackages = @()
                    IncludedForValidation = $false
                }
            }
        }
        """
        + helpers
        + """
        $packages = @(Get-PrPkgProperties $env:PR_DIFF)
        $names = @($packages | Select-Object -ExpandProperty Name | Sort-Object)
        Write-Host "SelectedPackages:$($names -join ',')"
        foreach ($package in $packages) {
            $package | ConvertTo-Json -Depth 10 | Set-Content (
                Join-Path $env:PACKAGE_INFO "$($package.Name).json"
            )
        }
        & $env:FILTER_SCRIPT -PackagePropertiesFolder $env:PACKAGE_INFO
        $retained = @(Get-ChildItem $env:PACKAGE_INFO -Filter '*.json' |
            Select-Object -ExpandProperty BaseName | Sort-Object)
        Write-Host "RetainedPackages:$($retained -join ',')"
        """,
        REPO_ROOT=str(REPO_ROOT),
        PR_DIFF=str(diff),
        PACKAGE_INFO=str(package_info),
        FILTER_SCRIPT=str(GENERIC_PR_EXCLUSION_SCRIPT),
        INCLUDE_COSMOS=str(include_cosmos),
        TARGETINGSTRING="",
    )


@pytest.mark.parametrize("changed", [["sdk/template/ci.yml"], ["eng/scripts/resolve-package-info.ps1"]])
def test_generic_pr_exclusion_filters_service_changes_and_fallback(tmp_path, changed):
    result = run_pr_fixture_discovery(tmp_path, changed)
    assert result.returncode == 0, result.stderr
    assert "SelectedPackages:azure-template,azure-template-three,azure-template-two" in result.stdout
    assert "RetainedPackages:azure-template,azure-template-two" in result.stdout


def test_pr_discovery_preserves_excluded_package_dependency_validation(tmp_path):
    result = run_pr_fixture_discovery(tmp_path, ["sdk/template/azure-template-two/README.md"], include_cosmos=True)
    assert result.returncode == 0, result.stderr
    assert "SelectedPackages:azure-cosmos,azure-template-two" in result.stdout
    assert "RetainedPackages:azure-cosmos,azure-template-two" in result.stdout
    cosmos = json.loads((tmp_path / "PackageInfo" / "azure-cosmos.json").read_text())
    assert cosmos["IncludedForValidation"] is True


def test_rust_fixture_routes_through_cibuildwheel_without_setuptools_extensions(tmp_path, monkeypatch):
    package = ParsedSetup.from_path(str(RUST_FIXTURE))
    assert package.name == "azure-template-three"
    assert package.version == "1.0.0b1"
    assert package.namespace == "azure.template.three"
    assert package.uses_cibuildwheel
    assert not package.ext_modules
    commands = []
    monkeypatch.setattr("ci_tools.build.run_logged", lambda command, **kwargs: commands.append(command))
    create_package(str(RUST_FIXTURE), str(tmp_path))
    assert commands == [
        [sys.executable, "-m", "cibuildwheel", "--output-dir", str(tmp_path)],
        [sys.executable, "-m", "build", "-s", "-o", str(tmp_path)],
    ]


def test_rust_fixture_matrix_and_container_contract():
    config = get_pyproject_dict(str(RUST_FIXTURE / "pyproject.toml"))
    assert config["build-system"] == {"requires": ["maturin==1.15.0"], "build-backend": "maturin"}
    assert config["tool"]["maturin"]["locked"] is True
    wheel = config["tool"]["cibuildwheel"]
    assert wheel["linux"]["archs"] == ["x86_64", "aarch64"]
    assert wheel["macos"]["archs"] == ["arm64"]
    assert wheel["windows"]["archs"] == ["AMD64", "ARM64"]
    build = load_template("steps/build-package-artifacts.yml")
    forwarding = next(
        step for step in build["steps"] if step.get("displayName") == "Forward build environment to cibuildwheel"
    )
    variables = {"PIP_INDEX_URL", *forwarding["env"][RUST_GATE]["RUST_ENVIRONMENT_PASS"].split()}
    assert set(wheel["linux"]["environment-pass"]) == variables
    assert "scripts/install-msrustup.sh" in wheel["linux"]["before-all"]
    assert "scripts/configure-cargo-feed.sh" in wheel["linux"]["before-all"]
    assert wheel["overrides"] == [
        {
            "select": "*-win_arm64",
            "environment": {
                "CARGO_BUILD_TARGET": "aarch64-pc-windows-msvc",
                "PYO3_CROSS_LIB_DIR": "$PYTHON_ARM64_LIB_DIR",
            },
        }
    ]
    toolchain = get_pyproject_dict(str(RUST_FIXTURE / "rust-toolchain.toml"))
    assert toolchain["toolchain"] == {"channel": "ms-prod-1.97", "profile": "minimal"}


def run_cargo_configuration(tmp_path, index="", token=""):
    shell = shutil.which("sh")
    if not shell:
        pytest.skip("A POSIX shell is required for Linux container configuration tests")
    return subprocess.run(
        [shell, str(RUST_FIXTURE / "scripts" / "configure-cargo-feed.sh")],
        env={
            **os.environ,
            "CARGO_HOME": str(tmp_path),
            "CARGO_REGISTRIES_AZURE_SDK_FOR_RUST_PUBLIC_INDEX": index,
            "CARGO_REGISTRIES_AZURE_SDK_FOR_RUST_PUBLIC_TOKEN": token,
        },
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def test_container_cargo_configuration_keeps_credentials_out_of_files(tmp_path):
    index = "sparse+https://example.test/Cargo/index/"
    result = run_cargo_configuration(tmp_path, index, "fixture-test-token")
    assert result.returncode == 0, result.stderr
    config = (tmp_path / "config.toml").read_text()
    assert index in config
    assert 'replace-with = "azure-sdk-for-rust-public"' in config
    assert "fixture-test-token" not in config + result.stdout + result.stderr
    result = run_cargo_configuration(tmp_path, index, "fixture-test-token")
    assert result.returncode != 0
    assert (tmp_path / "config.toml").read_text() == config


def test_container_cargo_configuration_requires_token_when_index_is_set(tmp_path):
    result = run_cargo_configuration(tmp_path, "sparse+https://example.test/Cargo/index/")
    assert result.returncode != 0
    assert "requires an authentication token" in result.stderr
    assert not (tmp_path / "config.toml").exists()


def test_container_cargo_configuration_preserves_local_crates_io(tmp_path):
    existing = tmp_path / "config.toml"
    existing.write_text("[net]\noffline = true\n")
    result = run_cargo_configuration(tmp_path)
    assert result.returncode == 0, result.stderr
    assert existing.read_text() == "[net]\noffline = true\n"


@pytest.mark.parametrize(
    "architecture,failure,expected",
    [
        ("x86_64", "", 0),
        ("aarch64", "", 0),
        ("x86_64", "index", 1),
        ("unsupported", "", 1),
    ],
)
def test_container_msrustup_bootstrap_downloads_and_surfaces_failures(tmp_path, architecture, failure, expected):
    if os.name == "nt" or not shutil.which("jq"):
        pytest.skip("The Linux bootstrap requires POSIX executables and jq")
    tools = tmp_path / "bin"
    tools.mkdir()
    commands = {
        "uname": '#!/bin/sh\nif [ "$1" = "-s" ]; then echo Linux; else echo "$FIXTURE_ARCH"; fi\n',
        "unzip": '#!/bin/sh\nprintf "#!/bin/sh\\nexit 0\\n" > msrustup\n',
        "curl": """#!/bin/sh
while [ "$#" -gt 0 ]; do
    case "$1" in
        -H) [ "$2" = "Authorization: Bearer fixture-test-token" ] || exit 9; shift 2 ;;
        --retry) shift 2 ;;
        -o) : > "$2"; shift 2 ;;
        -*) shift ;;
        *) url="$1"; shift ;;
    esac
done
case "$url" in
    https://example.test/feed)
        printf '{"resources":[{"@type":"PackageBaseAddress/3.0.0","@id":"https://example.test/packages/"}]}'
        ;;
    */index.json)
        [ "$FIXTURE_FAILURE" != "index" ] || exit 1
        printf '{"versions":["7.0.0"]}'
        ;;
    *.nupkg) printf '%s\\n' "$url" > "$FIXTURE_REQUEST" ;;
    *) exit 8 ;;
esac
""",
    }
    for name, content in commands.items():
        executable = tools / name
        executable.write_text(content)
        executable.chmod(0o755)
    request = tmp_path / "request.txt"
    result = subprocess.run(
        ["sh", str(RUST_FIXTURE / "scripts" / "install-msrustup.sh")],
        cwd=tmp_path,
        env={
            **os.environ,
            "PATH": f"{tools}{os.pathsep}{os.environ['PATH']}",
            "MSRUSTUP_FEED_URL": "https://example.test/feed",
            "MSRUSTUP_ACCESS_TOKEN": "fixture-test-token",
            "MSRUSTUP_PAT": "",
            "FIXTURE_ARCH": architecture,
            "FIXTURE_FAILURE": failure,
            "FIXTURE_REQUEST": str(request),
        },
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == expected, result.stderr
    assert "fixture-test-token" not in result.stdout + result.stderr
    assert not (tmp_path / "msrustup.zip").exists()
    if expected == 0:
        package = f"rust.msrustup-{architecture}-unknown-linux-gnu"
        assert request.read_text().strip() == f"https://example.test/packages/{package}/7.0.0/{package}.7.0.0.nupkg"
        assert os.access(tmp_path / "msrustup", os.X_OK)
    else:
        assert not (tmp_path / "msrustup").exists()
