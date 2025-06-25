from typing import Dict
import os

DEFAULT_ENVIRONMENT_VARIABLES = {
    "SPHINX_APIDOC_OPTIONS": "members,undoc-members,inherited-members",
    "PROXY_URL": "http://localhost:5000",
    "VIRTUALENV_WHEEL": "0.45.1",
    "VIRTUALENV_PIP": "24.0",
    "VIRTUALENV_SETUPTOOLS": "75.3.2",
    "PIP_EXTRA_INDEX_URL": "https://pypi.python.org/simple",
     # I haven't spent much time looking to see if a variable exists when invoking uv run. there might be one already that we can depend
     # on for get_pip_command adjustment.
    "IN_UV": "1"
}

def set_environment_variable_defaults(settings: Dict[str, str]) -> None:
    """
    Sets default environment variables for the UV prepare script.

    Args:
        settings (Dict[str, str]): A dictionary of environment variable names and their default values.
    """
    for key, value in settings.items():
        if key not in os.environ:
            os.environ.setdefault(key, value)