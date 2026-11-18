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

    job_defaults = {parameter["name"]: parameter.get("default") for parameter in jobs["parameters"]}
    assert job_defaults["BuildTimeoutInMinutes"] == 90
    timeout_gate = "${{ if and(parameters.InstallMsRustToolchain, lt(parameters.BuildTimeoutInMinutes, 240)) }}"
    for job in jobs["jobs"]:
        if job.get("job") not in ("Build_Linux", "Build_Windows", "Build_MacOS"):
            continue
        assert job[timeout_gate]["timeoutInMinutes"] == 240
        assert job["${{ else }}"]["timeoutInMinutes"] == "${{ parameters.BuildTimeoutInMinutes }}"
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
    assert "variable=AZURESDK_PYTHON_NUGET_FEED]" in provision["pwsh"]
    assert "variable=AZURESDK_PYTHON_ARM64_LIBS]true" in provision["pwsh"]
    assert "variable=PYTHON_ARM64_LIB_DIR]" not in provision["pwsh"]


@pytest.mark.parametrize("rust", ["true", "false"])
def test_windows_provisioning_configuration(tmp_path, rust):
    build = load_template("steps/build-package-artifacts.yml")
    provision = next(
        step for step in build["steps"] if step.get("displayName") == "Pre-provision CPython for cibuildwheel"
    )
    assert provision["condition"] == (
        "and(succeeded(), eq(variables['Agent.OS'], 'Windows_NT'), eq(variables['ENABLE_EXTENSION_BUILD'], 'true'))"
    )
    script = provision["pwsh"].replace("$(Agent.TempDirectory)", str(tmp_path))
    result = run_powershell(script, INSTALL_MS_RUST_TOOLCHAIN=rust)
    assert result.returncode == 0, result.stderr
    assert "variable=CIBW_CACHE_PATH]" in result.stdout
    assert (
        "variable=AZURESDK_PYTHON_NUGET_FEED]"
        "https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-net/nuget/v3/index.json"
    ) in result.stdout
    assert ("variable=AZURESDK_PYTHON_ARM64_LIBS]true" in result.stdout) is (rust == "true")
    assert "variable=PYTHON_ARM64_LIB_DIR]" not in result.stdout


def test_dev_requirements_share_selected_target_provisioning(tmp_path):
    steps = [step for step in load_template("jobs/live.tests.yml")["jobs"][0]["steps"] if isinstance(step, dict)]
    provision = next(step for step in steps if step.get("displayName") == "Pre-provision CPython for cibuildwheel")
    assert provision["condition"] == (
        "and(succeeded(), eq(variables['Agent.OS'], 'Windows_NT'), eq(variables['CIBUILDWHEEL_DEV_REQ'], 'true'))"
    )
    configure = next(
        step for step in steps if step.get("displayName") == "Configure cibuildwheel for dev requirement builds"
    )
    assert "variable=CIBW_ARCHS]native" in configure["pwsh"]
    assert "nuget install" not in provision["pwsh"]
    assert "3.10.11" not in provision["pwsh"]
    result = run_powershell(provision["pwsh"].replace("$(Agent.TempDirectory)", str(tmp_path)))
    assert result.returncode == 0, result.stderr
    assert "variable=CIBW_CACHE_PATH]" in result.stdout
    assert "variable=AZURESDK_PYTHON_NUGET_FEED]" in result.stdout
    assert "variable=AZURESDK_PYTHON_ARM64_LIBS]" not in result.stdout


def test_live_test_rust_support_is_opt_in_and_forwarded():
    archetype = load_template("stages/archetype-sdk-tests.yml")
    live = load_template("jobs/live.tests.yml")
    parameters = RUST_PARAMETERS[:3]
    for template in (archetype, live):
        defaults = {parameter["name"]: parameter.get("default") for parameter in template["parameters"]}
        assert defaults["InstallMsRustToolchain"] is False
        assert all(defaults[name] == "" for name in parameters[1:])

    stages = archetype["extends"]["parameters"]["stages"][0]
    clouds = next(iter(stages.values()))[0]
    cloud_gate = next(iter(clouds.values()))[0]
    supported_gate = next(iter(cloud_gate.values()))[0]
    stage = next(iter(supported_gate.values()))[0]
    matrix_types = stage["jobs"][0]
    matrix_gate = next(iter(matrix_types.values()))[0]
    matrix = next(iter(matrix_gate.values()))[0]
    forwarded = matrix["parameters"]["AdditionalParameters"]
    assert all(forwarded[name] == "${{ parameters." + name + " }}" for name in parameters)

    steps = live["jobs"][0]["steps"]
    install = next(step[RUST_GATE][0] for step in steps if isinstance(step, dict) and RUST_GATE in step)
    assert install["template"].endswith("install-msrust-toolchain.yml")
    assert install["parameters"] == {
        "ToolchainFeed": "${{ parameters.MsRustToolchainFeed }}",
        "WorkingDirectory": "${{ parameters.MsRustWorkingDirectory }}",
        "Condition": "and(succeeded(), eq(variables['CIBUILDWHEEL_DEV_REQ'], 'true'))",
    }
    test = next(
        step for step in steps if isinstance(step, dict) and step.get("template", "").endswith("build-test.yml")
    )
    credentials = test["parameters"]["EnvVars"][RUST_GATE]
    build = load_template("steps/build-package-artifacts.yml")
    generate = next(step for step in build["steps"] if step.get("displayName") == "Generate Packages")
    assert credentials == generate["env"][RUST_GATE]
    assert "${{ insert }}" in test["parameters"]["EnvVars"]
    assert steps.index(next(step for step in steps if isinstance(step, dict) and RUST_GATE in step)) < steps.index(test)

    run_tests = load_template("steps/build-test.yml")["steps"]
    federated = next(step for step in run_tests if "${{ if eq('true', parameters.UseFederatedAuth) }}" in step)
    non_federated = next(step for step in run_tests if "${{ else }}" in step)
    for step in federated["${{ if eq('true', parameters.UseFederatedAuth) }}"] + non_federated["${{ else }}"]:
        environment = step["env"]
        assert (
            environment.get("${{ insert }}") if isinstance(environment, dict) else environment
        ) == "${{ parameters.EnvVars }}"


@pytest.mark.parametrize("enabled", [False, True])
def test_live_test_container_forwarding_preserves_non_rust_builds(enabled):
    steps = load_template("jobs/live.tests.yml")["jobs"][0]["steps"]
    configure = next(
        step
        for step in steps
        if isinstance(step, dict) and step.get("displayName") == "Configure cibuildwheel for dev requirement builds"
    )
    build_steps = load_template("steps/build-package-artifacts.yml")["steps"]
    build_forwarding = next(
        step for step in build_steps if step.get("displayName") == "Forward build environment to cibuildwheel"
    )
    assert configure["env"] == build_forwarding["env"]
    extra = configure["env"][RUST_GATE]["RUST_ENVIRONMENT_PASS"] if enabled else ""
    result = run_powershell(configure["pwsh"], RUST_ENVIRONMENT_PASS=extra)
    assert result.returncode == 0, result.stderr
    expected = "PIP_INDEX_URL" + (" " + extra if enabled else "")
    assert f"variable=CIBW_ENVIRONMENT_PASS_LINUX]{expected}\n" in result.stdout
    assert "variable=CIBW_ARCHS]native" in result.stdout
    assert "variable=CIBW_SKIP]pp* *musllinux*" in result.stdout
    assert "variable=CIBW_TEST_SKIP]*" in result.stdout


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
        "jobs/live.tests.yml",
    ):
        template = load_template(template_path)
        steps = template["jobs"][0]["steps"] if "jobs" in template else template["steps"]
        for step in steps:
            if not isinstance(step, dict) or "pwsh" not in step:
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
