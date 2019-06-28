# Doing a mgmt release

IMPORTANT NOTE: All the commands in this page assumes you have loaded the [dev_setup](https://github.com/Azure/azure-sdk-for-python/wiki/Contributing-to-the-tests#setting-up-a-test-environment) in your currently loaded virtual environment.

## Building the code

If the automation is doing its job correctly, you should not have to build the SDK, but look for an integration PR for the service in question. This link will give you for instance [the list of all integration PRs](https://github.com/Azure/azure-sdk-for-python/labels/ServicePR).

If you really need to generate the code manually:
- Checkout the branch
- Checkout the RestAPI specs repo
- Call the tool: `python -m packaging_tools.generate_sdk -v -m restapi_path/readme.md` changing the last path to the readme you want to generate.

That's it.

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
