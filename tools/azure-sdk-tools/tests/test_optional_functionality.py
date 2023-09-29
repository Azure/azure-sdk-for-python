import os
import pytest

from ci_tools.parsing import ParsedSetup
from ci_tools.functions import get_config_setting
from ci_tools.scenario.generation import create_scenario_file

integration_folder = os.path.join(os.path.dirname(__file__), 'integration')

def test_toml_result():
    package_with_toml = os.path.join(integration_folder, 'scenarios', 'optional_environment_two_options')
    parsed_setup = ParsedSetup.from_path(package_with_toml)
    actual = parsed_setup.get_build_config()

    expected = {
        'mypy': True,
        'type_check_samples': True,
        'verifytypes': True,
        'pyright': True,
        'pylint': True,
        'black': True,
        'optional':[
            {
                'name': 'no_requests',
                'install': [],
                'uninstall': ['requests'],
                'additional_pytest_args': ['-k', '*_async.py']
            },
            {
                'name': 'no_aiohttp', 
                'install': [], 
                'uninstall': ['aiohttp'], 
                'additional_pytest_args': ['-k', 'not *_async.py']
            }
        ]
    }

    assert actual == expected

    
def test_optional_specific_get():
    package_with_toml = os.path.join(integration_folder, 'scenarios', 'optional_environment_two_options')
    actual = get_config_setting(package_with_toml, 'optional')
    expected = [
        {
            'name': 'no_requests',
            'install': [],
            'uninstall': ['requests'],
            'additional_pytest_args': ['-k', '*_async.py']
        },
        {
            'name': 'no_aiohttp', 
            'install': [], 
            'uninstall': ['aiohttp'], 
            'additional_pytest_args': ['-k', 'not *_async.py']
        }
    ]

    assert expected == actual


def test_optional_specific_get_no_result():
    package_with_toml = os.path.join(integration_folder, 'scenarios', 'optional_environment_zero_options')
    actual = get_config_setting(package_with_toml, 'optional', None)
    expected = None

    assert expected == actual

ZERO_OPTION_EXPECTED_INSTALL_FILE_NR = """-e ../../../../../../tools/azure-sdk-tools
../../../../../../sdk/core/azure-core
-e ../../../../../../tools/azure-devtools
aiohttp
requests
blah2
blah3
"""

ONE_OPTION_EXPECTED_INSTALL_FILE_NR = """blah
blah2
blah3
"""

TWO_OPTION_EXPECTED_INSTALL_FILE_NR = """blah
blah2
blah3
"""

ZERO_OPTION_EXPECTED_INSTALL_FILE_NA = """blah
blah2
blah3
"""

ONE_OPTION_EXPECTED_INSTALL_FILE_NA = """blah
blah2
blah3
"""

TWO_OPTION_EXPECTED_INSTALL_FILE_NA = """blah
blah2
blah3
"""

@pytest.mark.parametrize("path,env,expected", [
    ("optional_environment_zero_options", "no_requests", ZERO_OPTION_EXPECTED_INSTALL_FILE_NR),
    ("optional_environment_one_option", "no_requests", ONE_OPTION_EXPECTED_INSTALL_FILE_NR),
    ("optional_environment_two_options", "no_requests", TWO_OPTION_EXPECTED_INSTALL_FILE_NR),
    ("optional_environment_zero_options", "no_aiohttp", ZERO_OPTION_EXPECTED_INSTALL_FILE_NA),
    ("optional_environment_one_option", "no_aiohttp", ONE_OPTION_EXPECTED_INSTALL_FILE_NA),
    ("optional_environment_two_options", "no_aiohttp", TWO_OPTION_EXPECTED_INSTALL_FILE_NA),
])
def test_file_generation(path: str, env: str, expected: str):
    scenario_folder = os.path.join(integration_folder, 'scenarios', path)

    scenario_file = create_scenario_file(scenario_folder, env)
    assert scenario_file is not None

    exists = os.path.exists(scenario_file)
    assert exists

    with open(scenario_file, 'r', encoding='utf-8') as f:
        content = f.read()
    try:
        os.remove(scenario_file)
    except:
        pass
    assert content == expected


def test_invocation_errors_on_incompatible_uninstall():
    # need to ensure that we actually fail a situation where we break imports by uninstalling a dependency of azure-core
    pass

def test_empty_environment_cleanup():
    scenario_folder = os.path.join(integration_folder, 'scenarios', 'no_existing_scenario_file')
    pass

def test_standard_scenario_cleanup():
    scenario_folder = os.path.join(integration_folder, 'scenarios', 'single_existing_scenario_file')
    pass

def test_earlyexit_scenario_cleanup():
    """
    Normally the scenario file from a previous invocation is _immediately_ cleaned up by the next optional run. The only way it would
    not be is if we had messed something up. In that case, we should just take a simple join() of the pip_freeze() results.
    """
    scenario_folder = os.path.join(integration_folder, 'scenarios', 'multiple_existing_scenario_file')
    pass
