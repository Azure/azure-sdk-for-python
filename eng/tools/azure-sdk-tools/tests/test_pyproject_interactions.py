import os, tempfile, shutil


import pytest

from ci_tools.dependency_analysis import get_lib_deps
from ci_tools.parsing import update_build_config, get_build_config, get_config_setting
from ci_tools.environment_exclusions import is_check_enabled
from ci_tools.variables import discover_repo_root

integration_folder = os.path.join(os.path.dirname(__file__), "integration")
pyproject_folder = os.path.join(integration_folder, "scenarios", "pyproject_build_config")
pyproject_file = os.path.join(integration_folder, "scenarios", "pyproject_build_config", "pyproject.toml")


@pytest.mark.parametrize(
    "target",
    [
        # check is true
        pyproject_file,
        pyproject_folder,
        os.path.join(pyproject_folder, "setup.py"),
    ],
)
def test_pyproject_parse(target):
    config = get_build_config(target)

    assert config == {"mypy": True, "type_check_samples": True, "verifytypes": True, "pyright": False}


@pytest.mark.parametrize(
    "check_name, default_value, expected_result",
    [
        # check is true
        ("mypy", None, True),
        ("mypy", True, True),
        ("mypy", False, True),
        # check is false
        ("pyright", None, False),
        ("pyright", True, False),
        ("pyright", False, False),
        # check isn't present in the tools config
        ("non_present_check", None, None),
        ("non_present_check", True, True),
        ("non_present_check", False, False),
    ],
)
def test_get_config_setting(check_name, default_value, expected_result):
    result = get_config_setting(pyproject_folder, check_name, default_value)

    assert result == expected_result


def test_nonpresent_pyproject_update():
    with tempfile.TemporaryDirectory() as temp_dir:
        new_path = shutil.copy(pyproject_file, temp_dir)

        input = {"sdist": False}
        update_result = update_build_config(temp_dir, input)

        reloaded_build_config = get_build_config(new_path)
        assert reloaded_build_config == update_result


@pytest.mark.parametrize(
    "check_name, environment_value, expected_result",
    [("mindependency", "true", True), ("mindependency", "false", False)],
)
def test_environment_override(check_name, environment_value, expected_result):
    with tempfile.TemporaryDirectory() as temp_dir:
        new_path = shutil.copy(pyproject_file, temp_dir)

        os.environ[f"{os.path.basename(temp_dir).upper()}_{check_name.upper()}"] = environment_value
        result = is_check_enabled(temp_dir, check_name)

        assert result == expected_result


@pytest.fixture
def apistub_package(tmp_path, monkeypatch):
    package = tmp_path / "azure-test"
    package.mkdir()
    for check in ("APISTUB", "PYLINT", "CI_ENABLED"):
        monkeypatch.delenv(f"AZURE_TEST_{check}", raising=False)
    monkeypatch.setattr("ci_tools.environment_exclusions.in_public", lambda: False)
    monkeypatch.setattr("ci_tools.environment_exclusions.in_analyze_weekly", lambda: False)
    return package


@pytest.mark.parametrize("config", ["", "[tool.azure-sdk-build]\n", "[tool.azure-sdk-build]\napistub = true\n"])
def test_apistub_enabled(apistub_package, config):
    if config:
        (apistub_package / "pyproject.toml").write_text(config)

    assert is_check_enabled(str(apistub_package), "apistub") is True


@pytest.mark.parametrize("check", ["apistub", " APISTUB "])
@pytest.mark.parametrize("target", ["folder", "setup.py", "."])
def test_apistub_opt_out_rejected(apistub_package, monkeypatch, check, target):
    (apistub_package / "pyproject.toml").write_text("[tool.azure-sdk-build]\napistub = false\n")
    if target == ".":
        monkeypatch.chdir(apistub_package)
        package_path = "."
    elif target == "setup.py":
        package_path = str(apistub_package / "setup.py")
    else:
        package_path = str(apistub_package)

    with pytest.raises(ValueError, match="apistub is required") as error:
        is_check_enabled(package_path, check)

    assert str(apistub_package) in str(error.value)
    assert "apistub = false" in str(error.value)
    assert "[tool.azure-sdk-build]" in str(error.value)


def test_apistub_environment_opt_out_rejected(apistub_package, monkeypatch):
    (apistub_package / "pyproject.toml").write_text("[tool.azure-sdk-build]\napistub = true\n")
    monkeypatch.setenv("AZURE_TEST_APISTUB", "false")

    with pytest.raises(ValueError, match="APISTUB environment override"):
        is_check_enabled(str(apistub_package), "apistub")


def test_other_check_opt_out_preserved(apistub_package):
    (apistub_package / "pyproject.toml").write_text("[tool.azure-sdk-build]\npylint = false\n")

    assert is_check_enabled(str(apistub_package), "pylint") is False
    assert is_check_enabled(str(apistub_package), "black", default=False) is False


@pytest.mark.parametrize("build_mode", ["internal", "public", "weekly"])
@pytest.mark.parametrize("apistub_enabled", [True, False])
def test_apistub_ci_enabled_behavior_preserved(apistub_package, monkeypatch, build_mode, apistub_enabled):
    (apistub_package / "pyproject.toml").write_text(
        f"[tool.azure-sdk-build]\nci_enabled = false\napistub = {str(apistub_enabled).lower()}\n"
    )
    monkeypatch.setattr("ci_tools.environment_exclusions.in_public", lambda: build_mode == "public")
    monkeypatch.setattr("ci_tools.environment_exclusions.in_analyze_weekly", lambda: build_mode == "weekly")

    if build_mode != "internal" and not apistub_enabled:
        with pytest.raises(ValueError, match="apistub is required"):
            is_check_enabled(str(apistub_package), "apistub")
    else:
        assert is_check_enabled(str(apistub_package), "apistub") is (build_mode != "internal")


def test_pyproject_update_check_override():
    with tempfile.TemporaryDirectory() as temp_dir:
        new_path = shutil.copy(pyproject_file, temp_dir)

        build_config = get_build_config(temp_dir)

        assert build_config is not None
        build_config["pyright"] = True

        update_result = update_build_config(temp_dir, build_config)

        assert update_result == build_config

        reloaded_build_config = get_build_config(temp_dir)
        assert reloaded_build_config == update_result


def test_pyproject_get_lib_deps():
    all_packages, _ = get_lib_deps(discover_repo_root(), "azure*")
    # Ensure that libraries with pyproject.toml files are fetched correctly; azure-keyvault-keys is an example
    pyproject_info = all_packages["azure-keyvault-keys"]
    assert pyproject_info["version"]
    assert pyproject_info["source"]
    assert len(pyproject_info["deps"]) > 0


def test_pyproject_get_lib_deps_scoped():
    all_packages, _ = get_lib_deps(discover_repo_root(), "azure-core, azure-storage-blob")
    # Ensure that libraries with pyproject.toml files are fetched correctly; azure-core is an example
    pyproject_info = all_packages["azure-core"]
    assert pyproject_info["version"]
    assert pyproject_info["source"]
    assert len(pyproject_info["deps"]) > 0
    assert len(all_packages) == 2
