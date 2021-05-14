# Release History

## 1.0.0 (2021-05-14)

**Features**

  - Model CertificateProperties has a new parameter certificate
  - Model VerificationCodeResponseProperties has a new parameter certificate
  - Model IotDpsPropertiesDescription has a new parameter ip_filter_rules
  - Model IotDpsPropertiesDescription has a new parameter private_endpoint_connections
  - Model IotDpsPropertiesDescription has a new parameter public_network_access
  - Added operation IotDpsResourceOperations.get_private_endpoint_connection
  - Added operation IotDpsResourceOperations.list_private_link_resources
  - Added operation IotDpsResourceOperations.begin_create_or_update
  - Added operation IotDpsResourceOperations.begin_create_or_update_private_endpoint_connection
  - Added operation IotDpsResourceOperations.begin_update
  - Added operation IotDpsResourceOperations.get_private_link_resources
  - Added operation IotDpsResourceOperations.list_private_endpoint_connections
  - Added operation IotDpsResourceOperations.begin_delete_private_endpoint_connection
  - Added operation IotDpsResourceOperations.begin_delete

**Breaking changes**

  - Operation DpsCertificateOperations.create_or_update has a new signature
  - Operation DpsCertificateOperations.get has a new signature
  - Operation DpsCertificateOperations.list has a new signature
  - Operation IotDpsResourceOperations.get has a new signature
  - Operation IotDpsResourceOperations.get_operation_result has a new signature
  - Operation IotDpsResourceOperations.list_by_resource_group has a new signature
  - Operation IotDpsResourceOperations.list_keys has a new signature
  - Operation IotDpsResourceOperations.list_keys_for_key_name has a new signature
  - Operation IotDpsResourceOperations.list_valid_skus has a new signature
  - Operation DpsCertificateOperations.create_or_update has a new signature
  - Operation DpsCertificateOperations.verify_certificate has a new signature
  - Operation DpsCertificateOperations.generate_verification_code has a new signature
  - Operation DpsCertificateOperations.delete has a new signature
  - Operation Operations.list has a new signature
  - Operation IotDpsResourceOperations.check_provisioning_service_name_availability has a new signature
  - Operation IotDpsResourceOperations.list_by_subscription has a new signature
  - Removed operation IotDpsResourceOperations.create_or_update
  - Removed operation IotDpsResourceOperations.delete
  - Removed operation IotDpsResourceOperations.update

## 0.2.0 (2018-04-17)

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes.

  - Model signatures now use only keyword-argument syntax. All
    positional arguments must be re-written as keyword-arguments. To
    keep auto-completion in most cases, models are now generated for
    Python 2 and Python 3. Python 3 uses the "*" syntax for
    keyword-only arguments.
  - Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to
    improve the behavior when unrecognized enum values are encountered.
    While this is not a breaking change, the distinctions are important,
    and are documented here:
    <https://docs.python.org/3/library/enum.html#others> At a glance:
      - "is" should not be used at all.
      - "format" will return the string value, where "%s" string
        formatting will return `NameOfEnum.stringvalue`. Format syntax
        should be prefered.
  - New Long Running Operation:
      - Return type changes from
        `msrestazure.azure_operation.AzureOperationPoller` to
        `msrest.polling.LROPoller`. External API is the same.
      - Return type is now **always** a `msrest.polling.LROPoller`,
        regardless of the optional parameters used.
      - The behavior has changed when using `raw=True`. Instead of
        returning the initial call result as `ClientRawResponse`,
        without polling, now this returns an LROPoller. After polling,
        the final resource will be returned as a `ClientRawResponse`.
      - New `polling` parameter. The default behavior is
        `Polling=True` which will poll using ARM algorithm. When
        `Polling=False`, the response of the initial call will be
        returned without polling.
      - `polling` parameter accepts instances of subclasses of
        `msrest.polling.PollingMethod`.
      - `add_done_callback` will no longer raise if called after
        polling is finished, but will instead execute the callback right
        away.

**Bugfixes**

  - Compatibility of the sdist with wheel 0.31.0

**Features**

  - New ApiVersion 2018-01-22

## 0.1.0 (2018-01-04)

  - Initial Release
