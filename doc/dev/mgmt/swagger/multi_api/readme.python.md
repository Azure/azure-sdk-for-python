## Python

These settings apply only when `--python` is specified on the command line.

``` yaml $(python)
python:
  azure-arm: true
  license-header: MICROSOFT_MIT_NO_VERSION
  payload-flattening-threshold: 2
  package-name: azure-mgmt-servicetoreplace
  clear-output-folder: true
  no-namespace-folders: true
  python-base-folder: servicetoreplace/azure-mgmt-servicetoreplace/azure/mgmt/servicetoreplace
  python-base-namespace: azure.mgmt.servicetoreplace
```

### Python multi-api

Generate all API versions currently shipped for this package

```yaml $(python) && $(multiapi)
batch:
  - tag: package-2019-04
  - tag: package-2019-02
  - tag: package-2018-12
  - tag: package-2018-11
  - tag: package-2018-10
  - tag: package-2018-08
```

### Tag: package-2019-04 and python

These settings apply only when `--tag=package-2019-04 --python` is specified on the command line.
Please also specify `--python-sdks-folder=<path to the root directory of your azure-sdk-for-python clone>`.

``` yaml $(tag) == 'package-2019-04' && $(python)
python:
  namespace: $(python-base-namespace).v2019_04_01
  output-folder: $(python-sdks-folder)/$(python-base-folder)/v2019_04_01
```

### Tag: package-2019-02 and python

These settings apply only when `--tag=package-2019-02 --python` is specified on the command line.
Please also specify `--python-sdks-folder=<path to the root directory of your azure-sdk-for-python clone>`.

``` yaml $(tag) == 'package-2019-02' && $(python)
python:
  namespace: $(python-base-namespace).v2019_02_01
  output-folder: $(python-sdks-folder)/$(python-base-folder)/v2019_02_01
```

### Tag: package-2018-12 and python

These settings apply only when `--tag=package-2018-12 --python` is specified on the command line.
Please also specify `--python-sdks-folder=<path to the root directory of your azure-sdk-for-python clone>`.

``` yaml $(tag) == 'package-2018-12' && $(python)
python:
  namespace: $(python-base-namespace).v2018_12_01
  output-folder: $(python-sdks-folder)/$(python-base-folder)/v2018_12_01
```

### Tag: package-2018-11 and python

These settings apply only when `--tag=package-2018-11 --python` is specified on the command line.
Please also specify `--python-sdks-folder=<path to the root directory of your azure-sdk-for-python clone>`.

``` yaml $(tag) == 'package-2018-11' && $(python)
python:
  namespace: $(python-base-namespace).v2018_11_01
  output-folder: $(python-sdks-folder)/$(python-base-folder)/v2018_11_01
```

### Tag: package-2018-10 and python

These settings apply only when `--tag=package-2018-10 --python` is specified on the command line.
Please also specify `--python-sdks-folder=<path to the root directory of your azure-sdk-for-python clone>`.

``` yaml $(tag) == 'package-2018-10' && $(python)
python:
  namespace: $(python-base-namespace).v2018_10_01
  output-folder: $(python-sdks-folder)/$(python-base-folder)/v2018_10_01
```

### Tag: package-2018-08 and python

These settings apply only when `--tag=package-2018-08 --python` is specified on the command line.
Please also specify `--python-sdks-folder=<path to the root directory of your azure-sdk-for-python clone>`.

``` yaml $(tag) == 'package-2018-08' && $(python)
python:
  namespace: $(python-base-namespace).v2018_08_01
  output-folder: $(python-sdks-folder)/$(python-base-folder)/v2018_08_01
```
