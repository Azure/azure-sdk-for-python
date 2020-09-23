# Management Package Release

## General Release Process Overview

Once Swagger PR is merged, SDK automation will create pull request to Azure SDK for Python repository, and here are steps that you need to do in order to release a new package:

- open PR that was merged in swagger repository and find the link to the PR createted in Azure SDK for Python
- reopen generated SDK PR and make sure the CI passes
- verify that generated code was generated correctly, make sure right version was generated with right configuration
- merge the PR if everything looks good
- create another PR manually in order to add release notest and update version (this is currently not done by automation)
- generate release notes as described below, verify they match actual changes (HISTORY.rst)
- update version accordingly to changes that were made (version.py)
- merge the PR
- run release pipeline

Once you have a PR that contains accurate with correct tests (or no tests at all, but CI is green), this page explains how to prepare for a release.

IMPORTANT NOTE: All the commands in this page assumes you have loaded the [dev_setup](https://github.com/Azure/azure-sdk-for-python/blob/master/doc/dev/dev_setup.md) in your currently loaded virtual environment.

## Manual generation

If the automation is not doing its job to create an auto PR, Python has a SwaggerToSdk CLI that can be used to generate a specific Readme. You need
a virtual environment loaded with at least `tools/azure-sdk-tools` installed.

```shell
# Using default configuration (this can be a Github raw link)
generate_sdk -v -m ..\azure-rest-api-specs\specification\compute\resource-manager\readme.md

# Forcing Track1 generation
generate_sdk -v -c eng\swagger_to_sdk_config_v4.json -m ..\azure-rest-api-specs\specification\cognitiveservices\data-plane\Face\readme.md

# For more details about the available options
generate_sdk --help
```

## Building the packaging information

If the automation is doing its job correctly, there is a pipeline called "update PR" that is supposed to update the package on the branch.

If not, you can execute this command (replace the last part by your package name)
```shell
python -m packaging_tools --build-conf azure-mgmt-web
```

If the file sdk_packaging.toml didn't exist, now one is created with default values. Update this file and update the default values to the one from this service. Once it's done, restart the same script.

Your packaging info are up-to-date

## Building the ChangeLog

For all packages, you need to update the `HISTORY.rst` file

```
/azure-mgmt-myservice/HISTORY.rst
```

For all **autorest generated packages**, there is a tool that allows you to auto-build the ChangeLog.

This works in two steps:
- Step one: building the code "report", that introspect both the candidate code and the latest code created on PyPI into two report as files
- Step two: the tool will diff them, and deduce what are the changes

### Build the code report

#### Build the report from the latest package on PyPI:
```shell
python -m packaging_tools.code_report --last-pypi azure-mgmt-trafficmanager
```

Output will look like this:
```shell
INFO:__main__:Download versions of azure-mgmt-trafficmanager on PyPI
INFO:__main__:Got ['0.30.0rc5', '0.30.0rc6', '0.30.0', '0.40.0', '0.50.0', '0.51.0']
INFO:__main__:Only keep last PyPI version
INFO:__main__:Installing version 0.51.0 of azure-mgmt-trafficmanager in a venv
INFO:__main__:Looking for Autorest generated package in azure.mgmt.trafficmanager
INFO:__main__:Found azure.mgmt.trafficmanager
INFO:__main__:Working on azure.mgmt.trafficmanager
INFO:__main__:Report written to sdk/trafficmanager/azure-mgmt-trafficmanager/code_reports/0.51.0/report.json
```

Note the output path of the report:
`sdk/trafficmanager/azure-mgmt-trafficmanager/code_reports/0.51.0/report.json`

#### Build the report from the current code.

The principle is to introspect the current code in the package installed in editable mode:

```shell
python -m packaging_tools.code_report azure-mgmt-trafficmanager
```

IMPORTANT NOTE: If you forgot to install the package in editable mode, you will get this error:
```shell
INFO:__main__:Looking for Autorest generated package in azure.mgmt.trafficmanager
ModuleNotFoundError: No module named 'azure.mgmt.trafficmanager'
```

Correct output will look like this:
```shell
INFO:__main__:Looking for Autorest generated package in azure.mgmt.trafficmanager
INFO:__main__:Found azure.mgmt.trafficmanager
INFO:__main__:Working on azure.mgmt.trafficmanager
INFO:__main__:Report written to sdk/trafficmanager/azure-mgmt-trafficmanager/code_reports/latest/report.json
```

Note the output path of the report:
`sdk/trafficmanager/azure-mgmt-trafficmanager/code_reports/latest/report.json`

### Call the ChangeLog tool

You call the changelog tool with these report as input:
```shell
python -m packaging_tools.change_log sdk/trafficmanager/azure-mgmt-trafficmanager/code_reports/0.51.0/report.json sdk/trafficmanager/azure-mgmt-trafficmanager/code_reports/latest/report.json
```

Output will Markdown syntax that you can copy/paste directly into the HISTORY.txt
Example:
```shell
**Features**

- Model Endpoint has a new parameter subnets
- Model Profile has a new parameter max_return
- Added operation group TrafficManagerUserMetricsKeysOperations
```

### Note on multi-api packages

If a package is using multi-api, this means it contains several Autorest generated folder. The tool will then build one report per Autorest generation.

To simplify the change log call, the code report also build a "merged_report" that will merge correctly all api-versions and build a report suitable *for the default floating latest*

Example of output if call with network:
```shell
INFO:__main__:Looking for Autorest generated package in azure.mgmt.network
...
INFO:__main__:Merged report written to sdk/network/azure-mgmt-network/code_reports/latest/merged_report.json
```

Usually the merged report is enough, but you might need to select individual code report in some occasions.

## Version

You need to check the version in:
```
/azure-mgmt-myservice/azure/mgmt/myservice/version.py
```

Python SDK _strictly_ follows [semver](https://semver.org/). A few notes:

- First release should always use 0.1.0, unless asked explicitly by service team
- If a version is 0.5.2:
  - Next breaking / feature version is 0.6.0
  - Next bug fix is 0.5.3
- If a version is 2.1.0:
  - Next preview breaking is 3.0.0rc1
  - Next stable breaking is 3.0.0
  - Next preview feature is 2.2.0rc1
  - Next stable feature is 2.2.0
  - Next patch is  2.1.1
