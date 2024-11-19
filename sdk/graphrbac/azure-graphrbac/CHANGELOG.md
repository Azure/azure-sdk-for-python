# Release History

## 0.61.2 (2024-10-31)

### Other Changes

- This package has been deprecated and will no longer be maintained after 10-31-2024. This package will only receive security fixes until 10-31-2024. Refer to the samples in the [MS Graph SDK for Python repo](https://github.com/microsoftgraph/msgraph-sdk-python) instead.

- For additional support, open a new issue in the [Issues](https://github.com/microsoftgraph/msgraph-sdk-python/issues) section of the MS Graph SDK for Python repo.

## 0.61.1 (2019-05-29)

**Bugfix**

  - account_enabled is now correctly bool (from str)

## 0.61.0 (2019-03-20)

**Features**

  - Adding applications.get_service_principals_id_by_app_id

**Bugfix**

  - identifier_uris is not a required application parameter

## 0.60.0 (2019-03-13)

**Features**

  - Model Application has a new parameter optional_claims
  - Model Application has a new parameter pre_authorized_applications
  - Model Application has a new parameter group_membership_claims
  - Model Application has a new parameter
    oauth2_allow_url_path_matching
  - Model Application has a new parameter allow_passthrough_users
  - Model Application has a new parameter
    is_device_only_auth_supported
  - Model Application has a new parameter saml_metadata_url
  - Model Application has a new parameter app_logo_url
  - Model Application has a new parameter sign_in_audience
  - Model Application has a new parameter logout_url
  - Model Application has a new parameter oauth2_permissions
  - Model Application has a new parameter
    oauth2_require_post_response
  - Model Application has a new parameter org_restrictions
  - Model Application has a new parameter allow_guests_sign_in
  - Model Application has a new parameter www_homepage
  - Model Application has a new parameter public_client
  - Model Application has a new parameter error_url
  - Model Application has a new parameter known_client_applications
  - Model Application has a new parameter publisher_domain
  - Model Application has a new parameter informational_urls

**Breaking changes**

  - client.oauth2 has been renamed client.oauth2_permission_grant

## 0.53.0 (2018-11-27)

**Features**

  - Add PasswordCredentials.custom_key_identifier
  - Add Application.key_credentials
  - Add Application.password_credentials

**Bugfix**

  - Fix KeyCredential.custom_key_identifier type from bytes to str

## 0.52.0 (2018-10-29)

**Bugfix**

  - Add missing required_resource_access in Application

## 0.51.1 (2018-10-16)

**Bugfix**

  - Fix sdist broken in 0.50.0 and 0.51.0. No code change.

## 0.51.0 (2018-10-11)

**Features**

  - Add delete group/application owner

## 0.50.0 (2018-10-10)

**Features**

  - signed_in_user.get : Return the currently logged-in User object
  - signed_in_user.list_owned_objects : All objects owned by current
    user
  - deleted_applications.restore : Restore an application deleted in
    the last 30 days
  - deleted_applications.list : List all applications deleted in the
    last 30 days
  - deleted_applications.hard_delete : Delete for real an application
    in the deleted list
  - groups.list_owners : List owner of the group
  - groups.add_owner : Add owner to this group
  - Application and ServicePrincipals have now the attribute
    "app_roles" which is a list of AppRole class. To implement this.
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance
  - Model ADGroup has a attributes mail_enabled and mail_nickname
  - Model KeyCredential has a new atrribute custom_key_identifier
  - Added operation group oauth2_operations (operations "get" and
    "grant")

**Bug fixes**

  - Fix applications.list_owners access to next page
  - Fix service_principal.list_owners access to next page

**Breaking changes**

  - ApplicationAddOwnerParameters has been renamed AddOwnerParameters
  - objects.get_current_user has been removed. Use
    signed_in_user.get instead. The main difference is this new method
    returns a DirectoryObjectList, where every elements could be
    sub-type of DirectoryObject (User, Group, etc.)
  - objects.get_objects_by_object_ids now returns a
    DirectoryObjectList, where every element could be sub-type of
    DirectoryObject (User, Group, etc.)
  - GetObjectsParameters.include_directory_object_references is no
    longer required.
  - Groups.get_members now returns a DirectoryObjectList, where every
    element could be sub-type of DirectoryObject (User, Group, etc.)

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

**Note**

  - azure-mgmt-nspkg is not installed anymore on Python 3 (PEP420-based
    namespace package)

## 0.40.0 (2018-02-05)

**Disclaimer**

To prepare future versions, all Model creation should use keyword only
arguments.

**Breaking changes**

  - ApplicationCreateParameters changed __init__ signature, breaks
    if positional arguments was used.
  - ApplicationUpdateParameters changed __init__ signature, breaks
    if positional arguments was used.
  - CheckGroupMembershipParameters changed __init__ signature,
    breaks if positional arguments was used.
  - GetObjectsParameters changed __init__ signature, breaks if
    positional arguments was used.
  - GroupAddMemberParameters changed __init__ signature, breaks if
    positional arguments was used.
  - GroupCreateParameters changed __init__ signature, breaks if
    positional arguments was used.
  - GroupGetMemberGroupsParameters changed __init__ signature,
    breaks if positional arguments was used.
  - ServicePrincipalCreateParameters changed __init__ signature,
    breaks if positional arguments was used.
  - UserCreateParameters changed __init__ signature, breaks if
    positional arguments was used.
  - UserGetMemberGroupsParameters changed __init__ signature, breaks
    if positional arguments was used.
  - UserUpdateParameters changed __init__ signature, breaks if
    positional arguments was used.
  - groups.is_member_of now takes an instance of
    CheckGroupMembershipParameters, and not group_id, member_id
    parameters
  - groups.add_member now have an optional parameter
    "additional_properties", breaks if positional arguments was used.
  - groups.create now takes an instance of GroupCreateParameters, and
    not display_name, mail_nickname parameters
  - groups.get_member_groups now have an optional parameter
    "additional_properties", breaks if positional arguments was used.
  - service_principals.get_member_groups now have an optional
    parameter "additional_properties", breaks if positional arguments
    was used.

**Features**

  - Enable additional_properties on all Models. to dynamically harvest
    new properties.
  - Better hierarchy resolution and new generic Model like AADObject.
    This adds several new attribute to a lot of models.
  - Operation groups now have a "models" attribute.
  - Add applications.list_owners
  - Add applications.add_owner
  - Add service_principals.list_owners

## 0.33.0 (2017-11-01)

**Features**

  - add "required_resource_access" when applicable

**Bugfixes**

  - Get/Delete of Users now encode for you if you provide the UPN.

## 0.32.0 (2017-09-22)

**Features**

  - Add Application.oauth2_allow_implicit_flow (create, update, get)
  - Add to User: immutable_id, given_name, surname, user_type,
    account_enabled
  - Add to UserCreate: given_name, surname, user_type, mail
  - Add to UserUpdate: immutable_id, given_name, surname, user_type,
    user_principal_name

**Bugfixes**

  - Renamed User.signInName to an array User.signInNames

## 0.31.0 (2017-08-09)

  - Add domains operation group
  - Add usage locations to user
  - Add several new attributes to AADObject

## 0.30.0 (2017-04-20)

  - ApiVersion is now 1.6 for the whole package
  - This wheel package is now built with the azure wheel extension

## 0.30.0rc6 (2016-09-14)

**Bugfixes**

  - 'list' methods returned only 100 entries (#653)

## 0.30.0rc5 (2016-06-23)

  - Initial preview release
