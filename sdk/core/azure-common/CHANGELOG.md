# Release History

## 1.1.24 (2019-12-18)

- get_client_from_cli_profile now supports KV 4.x, Storage 12.x, AppConfig and all packages based on azure-core

## 1.1.23 (2019-06-24)

- Add Monitor into Profile v2019_03_01_hybrid (requires azure-mgmt-monitor >= 0.7.0)

## 1.1.22 (2019-06-06)

- Fix KeyVaultClient support for get_client_from_auth_file

## 1.1.21 (2019-05-21)

- Fix compute support in profile v2019_03_01_hybrid

## 1.1.20 (2019-04-30)

- Add support for profile v2019_03_01_hybrid
- Fix profile v2018_03_01_hybrid for DNS definition

## 1.1.19 (2019-04-18)

- Azure Stack support for get_client_from_auth_file and get_client_from_json_dict

## 1.1.18 (2019-01-29)

- Remove deprecated extra dependencies

## 1.1.17 (2019-01-15)

- Fix KeyVaultClient creation with get_client_from_cli_profile

Thanks to patrikn for the contribution

## 1.1.16 (2018-09-26)

- azure-nspkg is not installed anymore on Python 3 (PEP420-based namespace package)

## 1.1.15 (2018-09-13)

**Features**

- Adding profile v2018-03-01-hybrid definition

## 1.1.14 (2018-07-23)

**Features**

- Adding KeyVault to profile v2017_03_09_profile

## 1.1.13 (2018-07-03)

**Features**

- get_azure_cli_credentials has a new parameter "with_tenant" to get default CLI tenant ID

**Bugfixes**

- get_client_from_cli_profile now supports the "azure-graphrbac" package #2867
- get_client_from_auth_file now supports the "azure-graphrbac" package #2867

## 1.1.12 (2018-05-29)

**Features**

- Add Authorization profile definition

## 1.1.11 (2018-05-08)

**Features**

- Add support for "resource" in "get_azure_cli_credentials"

## 1.1.10 (2018-04-30)

**Bugfixes**

- Fix MultiApiClientMixin.__init__ to be a real mixin

## 1.1.9 (2018-04-03)

**Features**

- Add "azure.profiles" namespace #2247

**Bugfixes**

- get_client_from_cli_profile now supports Datalake #2318

## 1.1.8 (2017-07-28)

**Bugfix**

- Fix get_client_from_auth_file and get_client_from_json_dict on Python 2.7

Thank you to @jayden-at-arista for the contribution.

## 1.1.7 (2017-07-19)

- Adds azure.common.client_factory.get_client_from_auth_file
- Adds azure.common.client_factory.get_client_from_json_dict

## 1.1.6 (2017-05-16)

- Adds azure.common.client_factory.get_client_from_cli_profile

## 1.1.5 (2017-04-11)

- "extra_requires" autorest is deprecated and should not be used anymore
- This wheel package is now built with the azure wheel extension

## 1.1.4 (2016-05-25)

- Support for msrest/msrestazure 0.4.x series
- Drop support for msrest/msrestazure 0.3.x series

## 1.1.3 (2016-04-26)

- Support for msrest/msrestazure 0.3.x series
- Drop support for msrest/msrestazure 0.2.x series

## 1.1.2 (2016-03-28)

- Support for msrest/msrestazure 0.2.x series
- Drop support for msrest/msrestazure 0.1.x series

## 1.1.1 (2016-03-07)

- Move msrestazure depency as "extra_requires"

## 1.1.0 (2016-03-04)

- Support for msrest/msrestazure 0.1.x series
- Adds alias from msrestazure.azure_active_directory.* to azure.common.credentials

## 1.0.0 (2015-08-31)

Initial release, extracted from azure==0.11.1
