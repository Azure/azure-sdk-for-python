import os, tempfile, shutil


import pytest

from ci_tools.parsing import update_build_config, get_build_config, get_config_setting

integration_folder = os.path.join(os.path.dirname(__file__), "integration")
pyproject_folder = os.path.join(integration_folder, "scenarios", "sample_pyprojects")
pyproject_file = os.path.join(integration_folder, "scenarios", "sample_pyprojects", "pyproject.toml")


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


def test_pyproject_update_check_override():
    with tempfile.TemporaryDirectory() as temp_dir:
        new_path = shutil.copy(pyproject_file, temp_dir)

        build_config = get_build_config(temp_dir)

        build_config["pyright"] = True

        update_result = update_build_config(temp_dir, build_config)

        assert update_result == build_config

        reloaded_build_config = get_build_config(temp_dir)
        assert reloaded_build_config == update_result
