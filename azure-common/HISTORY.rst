.. :changelog:

Release History
===============

1.1.10 (2018-04-30)
+++++++++++++++++++

**Bugfixes**

- Fix MultiApiClientMixin.__init__ to be a real mixin

1.1.9 (2018-04-03)
++++++++++++++++++

**Features**

- Add "azure.profiles" namespace #2247

**Bugfixes**

- get_client_from_cli_profile now supports Datalake #2318

1.1.8 (2017-07-28)
++++++++++++++++++

**Bugfix**

- Fix get_client_from_auth_file and get_client_from_json_dict on Python 2.7

Thank you to @jayden-at-arista for the contribution.

1.1.7 (2017-07-19)
++++++++++++++++++

- Adds azure.common.client_factory.get_client_from_auth_file
- Adds azure.common.client_factory.get_client_from_json_dict

1.1.6 (2017-05-16)
++++++++++++++++++

- Adds azure.common.client_factory.get_client_from_cli_profile

1.1.5 (2017-04-11)
++++++++++++++++++

- "extra_requires" autorest is deprecated and should not be used anymore
- This wheel package is now built with the azure wheel extension

1.1.4 (2016-05-25)
++++++++++++++++++

- Support for msrest/msrestazure 0.4.x series
- Drop support for msrest/msrestazure 0.3.x series

1.1.3 (2016-04-26)
++++++++++++++++++

- Support for msrest/msrestazure 0.3.x series
- Drop support for msrest/msrestazure 0.2.x series

1.1.2 (2016-03-28)
++++++++++++++++++

- Support for msrest/msrestazure 0.2.x series
- Drop support for msrest/msrestazure 0.1.x series

1.1.1 (2016-03-07)
++++++++++++++++++

- Move msrestazure depency as "extra_requires"

1.1.0 (2016-03-04)
++++++++++++++++++

- Support for msrest/msrestazure 0.1.x series
- Adds alias from msrestazure.azure_active_directory.* to azure.common.credentials

1.0.0 (2015-08-31)
++++++++++++++++++

Initial release, extracted from azure==0.11.1
