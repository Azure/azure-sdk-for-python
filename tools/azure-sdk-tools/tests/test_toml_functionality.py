import os

from ci_tools.parsing import ParsedSetup

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
core_service_root = os.path.join(repo_root, "sdk", "core")

def test_toml_result():
    package_with_toml = os.path.join(core_service_root, "azure-core")

    parsed_setup = ParsedSetup.from_path(package_with_toml)
    result = parsed_setup.get_build_config()

    expected = {
        "type_check_samples": False,
        "verifytypes": False,
        "pyright": False,
    }

    assert expected == result