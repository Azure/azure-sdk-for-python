import os

from ci_tools.parsing import ParsedSetup

integration_folder = os.path.join(os.path.dirname(__file__), 'integration')

def test_toml_result():
    package_with_toml = os.path.join(integration_folder, 'scenarios', 'optional_environment')
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
                'additional_pytest_args': []
            },
            {
                'name': 'no_aiohttp', 
                'install': [], 
                'uninstall': ['aiohttp'], 
                'additional_pytest_args': []
            }
        ]
    }

    assert actual == expected

    