# Mgmt helper commands cheat sheet

## Create a venv

Windows:
`py -3.7 -m venv env3.7`

Linux (or Windows with Python from app store):
`python3 -m venv env3.7`

## Setup a venv for development

For all packages: `python ./scripts/dev_setup.py`

For a specific package: `python ./scripts/dev_setup.py -p azure-mgmt-servicename`

## Generate tags for multi-api Swagger Readme

`python ./scripts/multi_api_readme_help.py /azure-rest-api-specs/specification/service/resource-manager/`

## Generate a package

`python -m packaging_tools.generate_sdk -v -m restapi_path/readme.md`

Regenerate multi-api client: `python ./scripts/multiapi_init_gen.py azure-mgmt-myservice`

Regenerate multi-api of multi-client package: `python ./scripts/multiapi_init_gen.py azure-mgmt-myservice#subclientname`

## Update packaging setup.py / MANIFEST / etc.

Locally:
`python -m packaging_tools --build-conf azure-mgmt-myservice`

Update a given PR (needs GH_TOKEN env variable set): `python -m packaging_tools.update_pr -v -p 3979`

Edit `sdk_packaging.toml` if necesseray and restart the tool.

Available options:
| option name | type | description | example |
|-|-|-|-|
| auto_update | bool | If false, disable the bot system | false |
| package_name | str | package name | azure-mgmt-myservice |
| package_nspkg | str | namespace package name | azure-mgmt-nspkg |
| package_pprint_name | str | The nice name to show on PyPI | MyService Management |
| package_doc_id | str | the moniker on docs.microsoft.com (could be empty) | my-service |
| is_stable | bool | Should have discriminer as stable | false |
| is_arm | bool | needs a dependency on msrestazure | true |

## ChangeLog

Generate code report for last version on PyPI: `python -m packaging_tools.code_report --last-pypi azure-mgmt-myservice`

Generate code report for version installed in current venv: `python -m packaging_tools.code_report azure-mgmt-myservice`

Generate a markdown changelog: `python -m packaging_tools.change_log ./old_version_report.json ./new_version_report.json`

## Tests

Env variable quick copy/paste for Powershell:
```shell
$env:AZURE_TEST_RUN_LIVE='true'
$env:AZURE_TEST_RUN_LIVE='false'
Remove-Item Env:\AZURE_TEST_RUN_LIVE
```

Env variable quick copy/paste for Linux:
```shell
export AZURE_TEST_RUN_LIVE=true
export AZURE_TEST_RUN_LIVE=false
unset AZURE_TEST_RUN_LIVE
```

Start all tests: `pytest`

Start test for a package: `pytest -s sdk/service/azure-mgmt-service`

Start a specific test for a package: `pytest -s sdk/service/azure-mgmt-service -k TestFeatureOne`