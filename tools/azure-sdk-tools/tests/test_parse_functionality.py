from ci_tools.parsing import parse_require, ParsedSetup
from packaging.specifiers import SpecifierSet
import os
from unittest.mock import patch

import pytest

package_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
test_folder = os.path.join(
    os.path.dirname(__file__),
)
scenarios_folder = os.path.join(os.path.dirname(__file__), "integration", "scenarios")
metapackage_scenario = os.path.join(scenarios_folder, "setup_py_metapackage")
pyproject_scenario = os.path.join(scenarios_folder, "pyproject_project_def")
pyproject_extension_scenario = os.path.join(scenarios_folder, "pyproject_project_def_with_extension")


def test_parse_require():
    test_scenarios = [
        ("ConfigArgParse>=0.12.0", "configargparse", ">=0.12.0"),
        ("msrest>=0.6.10", "msrest", ">=0.6.10"),
        ("azure-core<2.0.0,>=1.2.2", "azure-core", "<2.0.0,>=1.2.2"),
        ("msrest==0.6.10", "msrest", "==0.6.10"),
        ("msrest<0.6.10", "msrest", "<0.6.10"),
        ("msrest>0.6.9", "msrest", ">0.6.9"),
        ("azure-core<2.0.0,>=1.2.2", "azure-core", "<2.0.0,>=1.2.2"),
        ("azure-core[aio]<2.0.0,>=1.26.0", "azure-core", "<2.0.0,>=1.26.0"),
        ("azure-core[aio,cool_extra]<2.0.0,>=1.26.0", "azure-core", "<2.0.0,>=1.26.0"),
        ("azure-core[]", "azure-core", None),
    ]

    for scenario in test_scenarios:
        result = parse_require(scenario[0])
        assert result.key is not None
        if scenario[2] is not None:
            assert len(result.specifier) != 0
        assert result.key == scenario[1]
        assert str(result.specifier) == (scenario[2] or "")


def test_parse_require_with_no_spec():
    spec_scenarios = ["readme_renderer"]

    for scenario in spec_scenarios:
        result = parse_require(scenario)

        assert result.key == scenario.replace("_", "-")
        assert len(result.specifier) == 0


@patch("ci_tools.parsing.parse_functions.read_setup_py_content")
def test_sdk_sample_setup(test_patch):
    test_patch.return_value = """
import re
import os.path
from io import open
from setuptools import find_packages, setup  # type: ignore

# Change the PACKAGE_NAME only to change folder and different name
PACKAGE_NAME = "azure-core"
PACKAGE_PPRINT_NAME = "Core"

# a-b-c => a/b/c
package_folder_path = PACKAGE_NAME.replace('-', '/')
# a-b-c => a.b.c
namespace_name = PACKAGE_NAME.replace('-', '.')

version = "1.21.0"
readme = "a buncha readme content"
changelog = "some other readme content"

setup(
    name=PACKAGE_NAME,
    version=version,
    include_package_data=True,
    description='Microsoft Azure {} Library for Python'.format(PACKAGE_PPRINT_NAME),
    long_description=readme + changelog,
    long_description_content_type='text/markdown',
    license='MIT License',
    author='Microsoft Corporation',
    author_email='azpysdkhelp@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Programming Language :: Python',
        "Programming Language :: Python :: 3 :: Only",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    packages=find_packages(exclude=[
        'tests',
        # Exclude packages that will be covered by PEP420 or nspkg
        'azure',
    ]),
    package_data={
        'pytyped': ['py.typed'],
    },
    python_requires=">=3.7",
    keywords=["azure sdk", "hello world"],
    install_requires=[
        'requests>=2.18.4',
        'six>=1.11.0',
        "typing-extensions>=4.0.1",
    ],
)
    """

    result = ParsedSetup.from_path(package_root)

    assert result.name == "azure-core"
    assert result.version == "1.21.0"
    assert result.python_requires == ">=3.7"
    assert result.requires == ["requests>=2.18.4", "six>=1.11.0", "typing-extensions>=4.0.1"]
    assert result.is_new_sdk == True
    assert result.setup_filename == os.path.join(package_root, "setup.py")
    assert "pytyped" in result.package_data
    assert result.include_package_data == True
    assert result.folder == package_root
    assert len(result.classifiers) > 0
    assert result.classifiers[0] == "Development Status :: 5 - Production/Stable"
    assert result.classifiers[5] == "Programming Language :: Python :: 3.8"
    assert result.keywords[0] == "azure sdk"
    assert result.is_metapackage == False
    assert len(result.keywords) == 2


@patch("ci_tools.parsing.parse_functions.read_setup_py_content")
def test_parse_recognizes_extensions(test_patch):
    test_patch.return_value = """
import re
import os.path
from io import open
import glob
from setuptools import find_packages, setup, Extension  # type: ignore
# Change the PACKAGE_NAME only to change folder and different name
PACKAGE_NAME = "azure-storage-extensions"
PACKAGE_PPRINT_NAME = "Storage Extensions"
# a-b-c => a/b/c
package_folder_path = PACKAGE_NAME.replace('-', '/')
# a-b-c => a.b.c
namespace_name = PACKAGE_NAME.replace('-', '.')
version = "1.21.0"
readme = "a buncha readme content"
changelog = "some other readme content"
setup(
    name=PACKAGE_NAME,
    version=version,
    include_package_data=True,
    description='Microsoft Azure {} Library for Python'.format(PACKAGE_PPRINT_NAME),
    long_description=readme + changelog,
    long_description_content_type='text/markdown',
    license='MIT License',
    author='Microsoft Corporation',
    author_email='azpysdkhelp@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Programming Language :: Python',
        "Programming Language :: Python :: 3 :: Only",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    packages=find_packages(exclude=[
        'tests',
        # Exclude packages that will be covered by PEP420 or nspkg
        'azure',
    ]),
    ext_package='azure.storage.extensions',
    ext_modules=[
        Extension('crc64', glob.glob(os.path.join(package_folder_path, 'crc64', '*.c')))
    ],
    package_data={
        'pytyped': ['py.typed'],
    },
    python_requires=">=3.7",
    install_requires=[
        'requests>=2.18.4',
        'six>=1.11.0',
        "typing-extensions>=4.0.1",
    ],
)
    """

    result = ParsedSetup.from_path(package_root)

    assert result.name == "azure-storage-extensions"
    assert result.version == "1.21.0"
    assert result.python_requires == ">=3.7"
    assert result.requires == ["requests>=2.18.4", "six>=1.11.0", "typing-extensions>=4.0.1"]
    # todo resolve this conflict assert result.is_new_sdk == True
    assert result.setup_filename == os.path.join(package_root, "setup.py")
    assert "pytyped" in result.package_data
    assert result.include_package_data == True
    assert result.folder == package_root
    assert len(result.classifiers) > 0
    assert result.classifiers[0] == "Development Status :: 5 - Production/Stable"
    assert result.classifiers[5] == "Programming Language :: Python :: 3.8"
    assert result.ext_package == "azure.storage.extensions"
    assert result.ext_modules is not None
    assert result.is_pyproject == False
    assert result.is_metapackage == False
    assert len(result.ext_modules) == 1
    assert str(type(result.ext_modules[0])) == "<class 'setuptools.extension.Extension'>"


def test_metapackage_detection():
    parsed_project = ParsedSetup.from_path(metapackage_scenario)
    assert parsed_project.is_metapackage == True
    assert parsed_project.name == "azure-keyvault"


def test_parse_pyproject():
    # ensure that we can parse from a folder and a specific file
    parsed_project = ParsedSetup.from_path(pyproject_scenario)

    assert parsed_project.name == "azure-keyvault-keys"
    assert parsed_project.version == "0.0.1"
    assert parsed_project.requires == [
        "azure-common~=1.1",
        "azure-core<2.0.0,>=1.24.0",
        "cryptography>=2.1.4",
        "isodate>=0.6.1",
        "typing-extensions>=4.0.1",
    ]
    assert parsed_project.python_requires == ">=3.7"
    assert parsed_project.is_new_sdk == True
    assert parsed_project.is_pyproject == True
    assert parsed_project.package_data == {"py.typed": ["py.typed"]}
    assert parsed_project.include_package_data == True
    assert parsed_project.folder == pyproject_scenario
    assert parsed_project.is_metapackage == False
    assert parsed_project.namespace == "azure.keyvault.keys"


def test_parse_pyproject_extensions():
    # ensure that we can parse from a folder and a specific file
    parsed_project = ParsedSetup.from_path(pyproject_extension_scenario)

    assert parsed_project.name == "azure-keyvault-keys"
    assert parsed_project.version == "0.0.1b1"
    assert parsed_project.requires == [
        "azure-common~=1.1",
        "azure-core<2.0.0,>=1.24.0",
        "cryptography>=2.1.4",
        "isodate>=0.6.1",
        "typing-extensions>=4.0.1",
    ]
    assert parsed_project.python_requires == ">=3.8"
    assert parsed_project.is_new_sdk == True
    assert parsed_project.is_pyproject == True
    assert parsed_project.package_data == {"py.typed": ["py.typed"]}
    assert parsed_project.include_package_data == True
    assert parsed_project.folder == pyproject_extension_scenario
    assert parsed_project.namespace == "azure.keyvault.keys"
    assert parsed_project.ext_package == "azure.keyvault.keys"
    assert parsed_project.ext_modules is not None
    assert parsed_project.is_metapackage == False
    assert len(parsed_project.ext_modules) == 1
    assert str(type(parsed_project.ext_modules[0])) == "<class 'setuptools.extension.Extension'>"
