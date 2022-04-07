## Python

These settings apply only when `--python` is specified on the command line.

``` yaml $(python)
azure-arm: true
license-header: MICROSOFT_MIT_NO_VERSION
package-name: azure-mgmt-servicetoreplace
package-version: 1.0.0b1
no-namespace-folders: true
```

### Python multi-api

Generate all API versions currently shipped for this package

```yaml $(python) && $(multiapi)
clear-output-folder: true
batch:
  - tag: package-2019-04
  - tag: package-2019-02
  - multiapiscript: true
```

``` yaml $(multiapiscript)
output-folder: $(python-sdks-folder)/servicetoreplace/azure-mgmt-servicetoreplace/azure/mgmt/servicetoreplace/
perform-load: false
```

### Tag: package-2019-04 and python

These settings apply only when `--tag=package-2019-04 --python` is specified on the command line.
Please also specify `--python-sdks-folder=<path to the root directory of your azure-sdk-for-python clone>`.

``` yaml $(tag) == 'package-2019-04' && $(python)
namespace: azure.mgmt.servicetoreplace.v2019_04_01
output-folder: $(python-sdks-folder)/servicetoreplace/azure-mgmt-servicetoreplace/azure/mgmt/servicetoreplace/v2019_04_01
```

### Tag: package-2019-02 and python

These settings apply only when `--tag=package-2019-02 --python` is specified on the command line.
Please also specify `--python-sdks-folder=<path to the root directory of your azure-sdk-for-python clone>`.

``` yaml $(tag) == 'package-2019-02' && $(python)
namespace: azure.mgmt.servicetoreplace.v2019_02_01
output-folder: $(python-sdks-folder)/servicetoreplace/azure-mgmt-servicetoreplace/azure/mgmt/servicetoreplace/v2019_02_01
```
