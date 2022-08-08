# Release History

## 1.11.0b3 (2022-08-09)

Azure-identity is supported on Python 3.7 or later. For more details, please read our page on [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy).

### Features Added

- Added ability to specify `tenant_id` for `AzureCliCredential` (thanks @tikicoder)    ([#25207](https://github.com/Azure/azure-sdk-for-python/pull/25207))

### Breaking Changes

- Removed `VisualStudioCodeCredential` from `DefaultAzureCredential` token chain. ([#23249](https://github.com/Azure/azure-sdk-for-python/issues/23249))

## 1.11.0b2 (2022-07-05)

### Features Added

- `EnvironmentCredential` added `AZURE_CLIENT_CERTIFICATE_PASSWORD` support for the cert password    ([#24652](https://github.com/Azure/azure-sdk-for-python/issues/24652))

### Bugs Fixed

- Fixed the issue that failed to parse PEM certificate if it does not start with "-----"    ([#24643](https://github.com/Azure/azure-sdk-for-python/issues/24643))

## 1.11.0b1 (2022-05-10)

### Features Added

- Added `validate_authority` support for msal client  ([#22625](https://github.com/Azure/azure-sdk-for-python/issues/22625))

## 1.10.0 (2022-04-28)

### Breaking Changes

> These changes do not impact the API of stable versions such as 1.9.0.
> Only code written against a beta version such as 1.10.0b1 may be affected.
- `validate_authority` support is not available in 1.10.0.

### Other Changes

- Supported msal-extensions version 1.0.0    ([#23927](https://github.com/Azure/azure-sdk-for-python/issues/23927))

## 1.10.0b1 (2022-04-07)

### Features Added

- Added `validate_authority` support for msal client  ([#22625](https://github.com/Azure/azure-sdk-for-python/issues/22625))

## 1.9.0 (2022-04-05)

### Features Added

- Added PII logging if logging.DEBUG is enabled.    ([#23203](https://github.com/Azure/azure-sdk-for-python/issues/23203))

### Breaking Changes

> These changes do not impact the API of stable versions such as 1.8.0.
> Only code written against a beta version such as 1.9.0b1 may be affected.
- `validate_authority` support is not available in 1.9.0.

### Bugs Fixed

- Added check on `content` from msal response.    ([#23483](https://github.com/Azure/azure-sdk-for-python/issues/23483))
- Fixed the issue that async OBO credential does not refresh correctly.    ([#21981](https://github.com/Azure/azure-sdk-for-python/issues/21981))

### Other Changes

- Removed `resource_id`, please use `identity_config` instead.
- Renamed argument name `get_assertion` to `func` for `ClientAssertionCredential`.

## 1.9.0b1 (2022-03-08)

### Features Added

- Added `validate_authority` support for msal client  ([#22625](https://github.com/Azure/azure-sdk-for-python/issues/22625))
- Added `resource_id` support for user-assigned managed identity  ([#22329](https://github.com/Azure/azure-sdk-for-python/issues/22329))
- Added `ClientAssertionCredential` support  ([#22328](https://github.com/Azure/azure-sdk-for-python/issues/22328))
- Updated App service API version to "2019-08-01" ([#23034](https://github.com/Azure/azure-sdk-for-python/issues/23034))

## 1.8.0 (2022-03-01)

### Bugs Fixed

- Handle injected "tenant_id" and "claims" ([#23138](https://github.com/Azure/azure-sdk-for-python/issues/23138))
  
  "tenant_id" argument in get_token() method is only supported by:

  - `AuthorizationCodeCredential`
  - `AzureCliCredential`
  - `AzurePowerShellCredential`
  - `InteractiveBrowserCredential`
  - `DeviceCodeCredential`
  - `EnvironmentCredential`
  - `UsernamePasswordCredential`

   it is ignored by other types of credentials.

### Other Changes

- Python 2.7 is no longer supported. Please use Python version 3.6 or later.

## 1.7.1 (2021-11-09)

### Bugs Fixed

- Fix multi-tenant auth using async AadClient ([#21289](https://github.com/Azure/azure-sdk-for-python/issues/21289))

## 1.7.0 (2021-10-14)

### Breaking Changes
> These changes do not impact the API of stable versions such as 1.6.0.
> Only code written against a beta version such as 1.7.0b1 may be affected.

- The `allow_multitenant_authentication` argument has been removed and the default behavior is now as if it were true.
  The multitenant authentication feature can be totally disabled by setting the environment variable 
  `AZURE_IDENTITY_DISABLE_MULTITENANTAUTH` to `True`.
- `azure.identity.RegionalAuthority` is removed.
- `regional_authority` argument is removed for `CertificateCredential` and `ClientSecretCredential`.
- `AzureApplicationCredential` is removed.
- `client_credential` in the ctor of `OnBehalfOfCredential` is removed. Please use `client_secret` or `client_certificate` instead.
- Make `user_assertion` in the ctor of `OnBehalfOfCredential` a keyword only argument.

## 1.7.0b4 (2021-09-09)

### Features Added
- `CertificateCredential` accepts certificates in PKCS12 format
  ([#13540](https://github.com/Azure/azure-sdk-for-python/issues/13540))
- `OnBehalfOfCredential` supports the on-behalf-of authentication flow for
  accessing resources on behalf of users
  ([#19308](https://github.com/Azure/azure-sdk-for-python/issues/19308))
- `DefaultAzureCredential` allows specifying the client ID of interactive browser via keyword argument `interactive_browser_client_id`
  ([#20487](https://github.com/Azure/azure-sdk-for-python/issues/20487))

### Other Changes
- Added context manager methods and `close()` to credentials in the
  `azure.identity` namespace. At the end of a `with` block, or when `close()`
  is called, these credentials close their underlying transport sessions.
  ([#18798](https://github.com/Azure/azure-sdk-for-python/issues/18798))


## 1.6.1 (2021-08-19)

### Other Changes
- Persistent cache implementations are now loaded on demand, enabling
  workarounds when importing transitive dependencies such as pywin32
  fails
  ([#19989](https://github.com/Azure/azure-sdk-for-python/issues/19989))


## 1.7.0b3 (2021-08-10)

### Breaking Changes
> These changes do not impact the API of stable versions such as 1.6.0.
> Only code written against a beta version such as 1.7.0b1 may be affected.
- Renamed `AZURE_POD_IDENTITY_TOKEN_URL` to `AZURE_POD_IDENTITY_AUTHORITY_HOST`.
  The value should now be a host, for example "http://169.254.169.254" (the
  default).

### Bugs Fixed
- Fixed import of `azure.identity.aio.AzureApplicationCredential`
  ([#19943](https://github.com/Azure/azure-sdk-for-python/issues/19943))

### Other Changes
- Added `CustomHookPolicy` to credential HTTP pipelines. This allows applications
  to initialize credentials with `raw_request_hook` and `raw_response_hook`
  keyword arguments. The value of these arguments should be a callback taking a
  `PipelineRequest` and `PipelineResponse`, respectively. For example:
  `ManagedIdentityCredential(raw_request_hook=lambda request: print(request.http_request.url))`
- Reduced redundant `ChainedTokenCredential` and `DefaultAzureCredential`
  logging. On Python 3.7+, credentials invoked by these classes now log debug
  rather than info messages.
  ([#18972](https://github.com/Azure/azure-sdk-for-python/issues/18972))
- Persistent cache implementations are now loaded on demand, enabling
  workarounds when importing transitive dependencies such as pywin32
  fails
  ([#19989](https://github.com/Azure/azure-sdk-for-python/issues/19989))


## 1.7.0b2 (2021-07-08)
### Features Added
- `InteractiveBrowserCredential` keyword argument `login_hint` enables
  pre-filling the username/email address field on the login page
  ([#19225](https://github.com/Azure/azure-sdk-for-python/issues/19225))
- `AzureApplicationCredential`, a default credential chain for applications
  deployed to Azure
  ([#19309](https://github.com/Azure/azure-sdk-for-python/issues/19309))

### Bugs Fixed
- `azure.identity.aio.ManagedIdentityCredential` is an async context manager
  that closes its underlying transport session at the end of a `with` block

### Other Changes
- Most credentials can use tenant ID values returned from authentication
  challenges, enabling them to request tokens from the correct tenant. This
  behavior is optional and controlled by a new keyword argument,
  `allow_multitenant_authentication`.
  ([#19300](https://github.com/Azure/azure-sdk-for-python/issues/19300))
  - When `allow_multitenant_authentication` is False, which is the default, a
    credential will raise `ClientAuthenticationError` when its configured tenant
    doesn't match the tenant specified for a token request. This may be a
    different exception than was raised by prior versions of the credential. To
    maintain the prior behavior, set environment variable
    AZURE_IDENTITY_ENABLE_LEGACY_TENANT_SELECTION to "True".
- `CertificateCredential` and `ClientSecretCredential` support regional STS
  on Azure VMs by either keyword argument `regional_authority` or environment
  variable `AZURE_REGIONAL_AUTHORITY_NAME`. See `azure.identity.RegionalAuthority`
  for possible values.
  ([#19301](https://github.com/Azure/azure-sdk-for-python/issues/19301))
- Upgraded minimum `azure-core` version to 1.11.0 and minimum `msal` version to
  1.12.0
- After IMDS authentication fails, `ManagedIdentityCredential` raises consistent
  error messages and uses `raise from` to propagate inner exceptions
  ([#19423](https://github.com/Azure/azure-sdk-for-python/pull/19423))

## 1.7.0b1 (2021-06-08)
Beginning with this release, this library requires Python 2.7 or 3.6+.

### Added
- `VisualStudioCodeCredential` gets its default tenant and authority
  configuration from VS Code user settings
  ([#14808](https://github.com/Azure/azure-sdk-for-python/issues/14808))

## 1.6.0 (2021-05-13)
This is the last version to support Python 3.5. The next version will require
Python 2.7 or 3.6+.

### Added
- `AzurePowerShellCredential` authenticates as the identity logged in to Azure
  PowerShell. This credential is part of `DefaultAzureCredential` by default
  but can be disabled by a keyword argument:
  `DefaultAzureCredential(exclude_powershell_credential=True)`
  ([#17341](https://github.com/Azure/azure-sdk-for-python/issues/17341))

### Fixed
- `AzureCliCredential` raises `CredentialUnavailableError` when the CLI times out,
  and kills timed out subprocesses
- Reduced retry delay for `ManagedIdentityCredential` on Azure VMs

## 1.6.0b3 (2021-04-06)
### Breaking Changes
> These changes do not impact the API of stable versions such as 1.5.0.
> Only code written against a beta version such as 1.6.0b1 may be affected.
- Removed property `AuthenticationRequiredError.error_details`

### Fixed
- Credentials consistently retry token requests after connection failures, or
  when instructed to by a Retry-After header
- ManagedIdentityCredential caches tokens correctly

### Added
- `InteractiveBrowserCredential` functions in more WSL environments
  ([#17615](https://github.com/Azure/azure-sdk-for-python/issues/17615))

## 1.6.0b2 (2021-03-09)
### Breaking Changes
> These changes do not impact the API of stable versions such as 1.5.0.
> Only code written against a beta version such as 1.6.0b1 may be affected.
- Renamed `CertificateCredential` keyword argument `certificate_bytes` to
  `certificate_data`
- Credentials accepting keyword arguments `allow_unencrypted_cache` and
  `enable_persistent_cache` to configure persistent caching accept a
  `cache_persistence_options` argument instead whose value should be an
  instance of `TokenCachePersistenceOptions`. For example:
  ```
  # before (e.g. in 1.6.0b1):
  DeviceCodeCredential(enable_persistent_cache=True, allow_unencrypted_cache=True)

  # after:
  cache_options = TokenCachePersistenceOptions(allow_unencrypted_storage=True)
  DeviceCodeCredential(cache_persistence_options=cache_options)
  ```

  See the documentation and samples for more details.

### Added
- New class `TokenCachePersistenceOptions` configures persistent caching
- The `AuthenticationRequiredError.claims` property provides any additional
  claims required by a user credential's `authenticate()` method

## 1.6.0b1 (2021-02-09)
### Changed
- Raised minimum msal version to 1.7.0
- Raised minimum six version to 1.12.0

### Added
- `InteractiveBrowserCredential` uses PKCE internally to protect authorization
  codes
- `CertificateCredential` can load a certificate from bytes instead of a file
  path. To provide a certificate as bytes, use the keyword argument
  `certificate_bytes` instead of `certificate_path`, for example:
  `CertificateCredential(tenant_id, client_id, certificate_bytes=cert_bytes)`
  ([#14055](https://github.com/Azure/azure-sdk-for-python/issues/14055))
- User credentials support Continuous Access Evaluation (CAE)
- Application authentication APIs from 1.5.0b2

### Fixed
- `ManagedIdentityCredential` correctly parses responses from the current
  (preview) version of Azure ML managed identity
  ([#15361](https://github.com/Azure/azure-sdk-for-python/issues/15361))

## 1.5.0 (2020-11-11)
### Breaking Changes
- Renamed optional `CertificateCredential` keyword argument `send_certificate`
  (added in 1.5.0b1) to `send_certificate_chain`
- Removed user authentication APIs added in prior betas. These will be
  reintroduced in 1.6.0b1. Passing the keyword arguments below
  generally won't cause a runtime error, but the arguments have no effect.
  ([#14601](https://github.com/Azure/azure-sdk-for-python/issues/14601))
  - Removed `authenticate` method from `DeviceCodeCredential`,
    `InteractiveBrowserCredential`, and `UsernamePasswordCredential`
  - Removed `allow_unencrypted_cache` and `enable_persistent_cache` keyword
    arguments from `CertificateCredential`, `ClientSecretCredential`,
    `DeviceCodeCredential`, `InteractiveBrowserCredential`, and
    `UsernamePasswordCredential`
  - Removed `disable_automatic_authentication` keyword argument from
    `DeviceCodeCredential` and `InteractiveBrowserCredential`
  - Removed `allow_unencrypted_cache` keyword argument from
    `SharedTokenCacheCredential`
  - Removed classes `AuthenticationRecord` and `AuthenticationRequiredError`
- Removed `identity_config` keyword argument from `ManagedIdentityCredential`
  (was added in 1.5.0b1)

### Changed
- `DeviceCodeCredential` parameter `client_id` is now optional. When not
   provided, the credential will authenticate users to an Azure development
   application.
   ([#14354](https://github.com/Azure/azure-sdk-for-python/issues/14354))
- Credentials raise `ValueError` when constructed with tenant IDs containing
  invalid characters
  ([#14821](https://github.com/Azure/azure-sdk-for-python/issues/14821))
- Raised minimum msal version to 1.6.0

### Added
- `ManagedIdentityCredential` supports Service Fabric
  ([#12705](https://github.com/Azure/azure-sdk-for-python/issues/12705))
  and Azure Arc
  ([#12702](https://github.com/Azure/azure-sdk-for-python/issues/12702))

### Fixed
- Prevent `VisualStudioCodeCredential` using invalid authentication data when
  no user is signed in to Visual Studio Code
  ([#14438](https://github.com/Azure/azure-sdk-for-python/issues/14438))
- `ManagedIdentityCredential` uses the API version supported by Azure Functions
  on Linux consumption hosting plans
  ([#14670](https://github.com/Azure/azure-sdk-for-python/issues/14670))
- `InteractiveBrowserCredential.get_token()` raises a clearer error message when
  it times out waiting for a user to authenticate on Python 2.7
  ([#14773](https://github.com/Azure/azure-sdk-for-python/pull/14773))

## 1.5.0b2 (2020-10-07)
### Fixed
- `AzureCliCredential.get_token` correctly sets token expiration time,
  preventing clients from using expired tokens
  ([#14345](https://github.com/Azure/azure-sdk-for-python/issues/14345))

### Changed
- Adopted msal-extensions 0.3.0
([#13107](https://github.com/Azure/azure-sdk-for-python/issues/13107))

## 1.4.1 (2020-10-07)
### Fixed
- `AzureCliCredential.get_token` correctly sets token expiration time,
  preventing clients from using expired tokens
  ([#14345](https://github.com/Azure/azure-sdk-for-python/issues/14345))

## 1.5.0b1 (2020-09-08)
### Added
- Application authentication APIs from 1.4.0b7
- `ManagedIdentityCredential` supports the latest version of App Service
  ([#11346](https://github.com/Azure/azure-sdk-for-python/issues/11346))
- `DefaultAzureCredential` allows specifying the client ID of a user-assigned
  managed identity via keyword argument `managed_identity_client_id`
  ([#12991](https://github.com/Azure/azure-sdk-for-python/issues/12991))
- `CertificateCredential` supports Subject Name/Issuer authentication when
  created with `send_certificate=True`. The async `CertificateCredential`
  (`azure.identity.aio.CertificateCredential`) will support this in a
  future version.
  ([#10816](https://github.com/Azure/azure-sdk-for-python/issues/10816))
- Credentials in `azure.identity` support ADFS authorities, excepting
  `VisualStudioCodeCredential`. To configure a credential for this, configure
  the credential with `authority` and `tenant_id="adfs"` keyword arguments, for
  example
  `ClientSecretCredential(authority="<your ADFS URI>", tenant_id="adfs")`.
  Async credentials (those in `azure.identity.aio`) will support ADFS in a
  future release.
  ([#12696](https://github.com/Azure/azure-sdk-for-python/issues/12696))
- `InteractiveBrowserCredential` keyword argument `redirect_uri` enables
  authentication with a user-specified application having a custom redirect URI
  ([#13344](https://github.com/Azure/azure-sdk-for-python/issues/13344))

### Breaking changes
- Removed `authentication_record` keyword argument from the async
  `SharedTokenCacheCredential`, i.e. `azure.identity.aio.SharedTokenCacheCredential`

## 1.4.0 (2020-08-10)
### Added
- `DefaultAzureCredential` uses the value of environment variable
`AZURE_CLIENT_ID` to configure a user-assigned managed identity.
([#10931](https://github.com/Azure/azure-sdk-for-python/issues/10931))

### Breaking Changes
- Renamed `VSCodeCredential` to `VisualStudioCodeCredential`
- Removed application authentication APIs added in 1.4.0 beta versions. These
  will be reintroduced in 1.5.0b1. Passing the keyword arguments below
  generally won't cause a runtime error, but the arguments have no effect.
  - Removed `authenticate` method from `DeviceCodeCredential`,
    `InteractiveBrowserCredential`, and `UsernamePasswordCredential`
  - Removed `allow_unencrypted_cache` and `enable_persistent_cache` keyword
    arguments from `CertificateCredential`, `ClientSecretCredential`,
    `DeviceCodeCredential`, `InteractiveBrowserCredential`, and
    `UsernamePasswordCredential`
  - Removed `disable_automatic_authentication` keyword argument from
    `DeviceCodeCredential` and `InteractiveBrowserCredential`
  - Removed `allow_unencrypted_cache` keyword argument from
    `SharedTokenCacheCredential`
  - Removed classes `AuthenticationRecord` and `AuthenticationRequiredError`
  - Removed `identity_config` keyword argument from `ManagedIdentityCredential`

## 1.4.0b7 (2020-07-22)
- `DefaultAzureCredential` has a new optional keyword argument,
`visual_studio_code_tenant_id`, which sets the tenant the credential should
authenticate in when authenticating as the Azure user signed in to Visual
Studio Code.
- Renamed `AuthenticationRecord.deserialize` positional parameter `json_string`
to `data`.


## 1.4.0b6 (2020-07-07)
- `AzureCliCredential` no longer raises an exception due to unexpected output
  from the CLI when run by PyCharm (thanks @NVolcz)
  ([#11362](https://github.com/Azure/azure-sdk-for-python/pull/11362))
- Upgraded minimum `msal` version to 1.3.0
- The async `AzureCliCredential` correctly invokes `/bin/sh`
  ([#12048](https://github.com/Azure/azure-sdk-for-python/issues/12048))

## 1.4.0b5 (2020-06-12)
- Prevent an error on importing `AzureCliCredential` on Windows caused by a bug
  in old versions of Python 3.6 (this bug was fixed in Python 3.6.5).
  ([#12014](https://github.com/Azure/azure-sdk-for-python/issues/12014))
- `SharedTokenCacheCredential.get_token` raises `ValueError` instead of
  `ClientAuthenticationError` when called with no scopes.
  ([#11553](https://github.com/Azure/azure-sdk-for-python/issues/11553))

## 1.4.0b4 (2020-06-09)
- `ManagedIdentityCredential` can configure a user-assigned identity using any
  identifier supported by the current hosting environment. To specify an
  identity by its client ID, continue using the `client_id` argument. To
  specify an identity by any other ID, use the `identity_config` argument,
  for example: `ManagedIdentityCredential(identity_config={"object_id": ".."})`
  ([#10989](https://github.com/Azure/azure-sdk-for-python/issues/10989))
- `CertificateCredential` and `ClientSecretCredential` can optionally store
  access tokens they acquire in a persistent cache. To enable this, construct
  the credential with `enable_persistent_cache=True`. On Linux, the persistent
  cache requires libsecret and `pygobject`. If these are unavailable or
  unusable (e.g. in an SSH session), loading the persistent cache will raise an
  error. You may optionally configure the credential to fall back to an
  unencrypted cache by constructing it with keyword argument
  `allow_unencrypted_cache=True`.
  ([#11347](https://github.com/Azure/azure-sdk-for-python/issues/11347))
- `AzureCliCredential` raises `CredentialUnavailableError` when no user is
  logged in to the Azure CLI.
  ([#11819](https://github.com/Azure/azure-sdk-for-python/issues/11819))
- `AzureCliCredential` and `VSCodeCredential`, which enable authenticating as
  the identity signed in to the Azure CLI and Visual Studio Code, respectively,
  can be imported from `azure.identity` and `azure.identity.aio`.
- `azure.identity.aio.AuthorizationCodeCredential.get_token()` no longer accepts
  optional keyword arguments `executor` or `loop`. Prior versions of the method
  didn't use these correctly, provoking exceptions, and internal changes in this
  version have made them obsolete.
- `InteractiveBrowserCredential` raises `CredentialUnavailableError` when it
  can't start an HTTP server on `localhost`.
  ([#11665](https://github.com/Azure/azure-sdk-for-python/pull/11665))
- When constructing `DefaultAzureCredential`, you can now configure a tenant ID
  for `InteractiveBrowserCredential`. When none is specified, the credential
  authenticates users in their home tenants. To specify a different tenant, use
  the keyword argument `interactive_browser_tenant_id`, or set the environment
  variable `AZURE_TENANT_ID`.
  ([#11548](https://github.com/Azure/azure-sdk-for-python/issues/11548))
- `SharedTokenCacheCredential` can be initialized with an `AuthenticationRecord`
  provided by a user credential.
  ([#11448](https://github.com/Azure/azure-sdk-for-python/issues/11448))
- The user authentication API added to `DeviceCodeCredential` and
  `InteractiveBrowserCredential` in 1.4.0b3 is available on
  `UsernamePasswordCredential` as well.
  ([#11449](https://github.com/Azure/azure-sdk-for-python/issues/11449))
- The optional persistent cache for `DeviceCodeCredential` and
  `InteractiveBrowserCredential` added in 1.4.0b3 is now available on Linux and
  macOS as well as Windows.
  ([#11134](https://github.com/Azure/azure-sdk-for-python/issues/11134))
  - On Linux, the persistent cache requires libsecret and `pygobject`. If these
    are unavailable, or libsecret is unusable (e.g. in an SSH session), loading
    the persistent cache will raise an error. You may optionally configure the
    credential to fall back to an unencrypted cache by constructing it with
    keyword argument `allow_unencrypted_cache=True`.

## 1.4.0b3 (2020-05-04)
- `EnvironmentCredential` correctly initializes `UsernamePasswordCredential`
with the value of `AZURE_TENANT_ID`
([#11127](https://github.com/Azure/azure-sdk-for-python/pull/11127))
- Values for the constructor keyword argument `authority` and
`AZURE_AUTHORITY_HOST` may optionally specify an "https" scheme. For example,
"https://login.microsoftonline.us" and "login.microsoftonline.us" are both valid.
([#10819](https://github.com/Azure/azure-sdk-for-python/issues/10819))
- First preview of new API for authenticating users with `DeviceCodeCredential`
  and `InteractiveBrowserCredential`
  ([#10612](https://github.com/Azure/azure-sdk-for-python/pull/10612))
  - new method `authenticate` interactively authenticates a user, returns a
    serializable `AuthenticationRecord`
  - new constructor keyword arguments
    - `authentication_record` enables initializing a credential with an
      `AuthenticationRecord` from a prior authentication
    - `disable_automatic_authentication=True` configures the credential to raise
    `AuthenticationRequiredError` when interactive authentication is necessary
    to acquire a token rather than immediately begin that authentication
    - `enable_persistent_cache=True` configures these credentials to use a
    persistent cache on supported platforms (in this release, Windows only).
    By default they cache in memory only.
- Now `DefaultAzureCredential` can authenticate with the identity signed in to
Visual Studio Code's Azure extension.
([#10472](https://github.com/Azure/azure-sdk-for-python/issues/10472))

## 1.4.0b2 (2020-04-06)
- After an instance of `DefaultAzureCredential` successfully authenticates, it
uses the same authentication method for every subsequent token request. This
makes subsequent requests more efficient, and prevents unexpected changes of
authentication method.
([#10349](https://github.com/Azure/azure-sdk-for-python/pull/10349))
- All `get_token` methods consistently require at least one scope argument,
raising an error when none is passed. Although `get_token()` may sometimes
have succeeded in prior versions, it couldn't do so consistently because its
behavior was undefined, and dependened on the credential's type and internal
state. ([#10243](https://github.com/Azure/azure-sdk-for-python/issues/10243))
- `SharedTokenCacheCredential` raises `CredentialUnavailableError` when the
cache is available but contains ambiguous or insufficient information. This
causes `ChainedTokenCredential` to correctly try the next credential in the
chain. ([#10631](https://github.com/Azure/azure-sdk-for-python/issues/10631))
- The host of the Active Directory endpoint credentials should use can be set
in the environment variable `AZURE_AUTHORITY_HOST`. See
`azure.identity.KnownAuthorities` for a list of common values.
([#8094](https://github.com/Azure/azure-sdk-for-python/issues/8094))


## 1.3.1 (2020-03-30)

- `ManagedIdentityCredential` raises `CredentialUnavailableError` when no
identity is configured for an IMDS endpoint. This causes
`ChainedTokenCredential` to correctly try the next credential in the chain.
([#10488](https://github.com/Azure/azure-sdk-for-python/issues/10488))


## 1.4.0b1 (2020-03-10)
- `DefaultAzureCredential` can now authenticate using the identity logged in to
the Azure CLI, unless explicitly disabled with a keyword argument:
`DefaultAzureCredential(exclude_cli_credential=True)`
([#10092](https://github.com/Azure/azure-sdk-for-python/pull/10092))


## 1.3.0 (2020-02-11)

- Correctly parse token expiration time on Windows App Service
([#9393](https://github.com/Azure/azure-sdk-for-python/issues/9393))
- Credentials raise `CredentialUnavailableError` when they can't attempt to
authenticate due to missing data or state
([#9372](https://github.com/Azure/azure-sdk-for-python/pull/9372))
- `CertificateCredential` supports password-protected private keys
([#9434](https://github.com/Azure/azure-sdk-for-python/pull/9434))


## 1.2.0 (2020-01-14)

- All credential pipelines include `ProxyPolicy`
([#8945](https://github.com/Azure/azure-sdk-for-python/pull/8945))
- Async credentials are async context managers and have an async `close` method
([#9090](https://github.com/Azure/azure-sdk-for-python/pull/9090))


## 1.1.0 (2019-11-27)

- Constructing `DefaultAzureCredential` no longer raises `ImportError` on Python
3.8 on Windows ([8294](https://github.com/Azure/azure-sdk-for-python/pull/8294))
- `InteractiveBrowserCredential` raises when unable to open a web browser
([8465](https://github.com/Azure/azure-sdk-for-python/pull/8465))
- `InteractiveBrowserCredential` prompts for account selection
([8470](https://github.com/Azure/azure-sdk-for-python/pull/8470))
- The credentials composing `DefaultAzureCredential` are configurable by keyword
arguments ([8514](https://github.com/Azure/azure-sdk-for-python/pull/8514))
- `SharedTokenCacheCredential` accepts an optional `tenant_id` keyword argument
([8689](https://github.com/Azure/azure-sdk-for-python/pull/8689))


## 1.0.1 (2019-11-05)

- `ClientCertificateCredential` uses application and tenant IDs correctly
([8315](https://github.com/Azure/azure-sdk-for-python/pull/8315))
- `InteractiveBrowserCredential` properly caches tokens
([8352](https://github.com/Azure/azure-sdk-for-python/pull/8352))
- Adopted msal 1.0.0 and msal-extensions 0.1.3
([8359](https://github.com/Azure/azure-sdk-for-python/pull/8359))


## 1.0.0 (2019-10-29)
### Breaking changes:
- Async credentials now default to [`aiohttp`](https://pypi.org/project/aiohttp/)
for transport but the library does not require it as a dependency because the
async API is optional. To use async credentials, please install
[`aiohttp`](https://pypi.org/project/aiohttp/) or see
[azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md#transport)
for information about customizing the transport.
- Renamed `ClientSecretCredential` parameter "`secret`" to "`client_secret`"
- All credentials with `tenant_id` and `client_id` positional parameters now accept them in that order
- Changes to `InteractiveBrowserCredential` parameters
  - positional parameter `client_id` is now an optional keyword argument. If no value is provided,
the Azure CLI's client ID will be used.
  - Optional keyword argument `tenant` renamed `tenant_id`
- Changes to `DeviceCodeCredential`
  - optional positional parameter `prompt_callback` is now a keyword argument
  - `prompt_callback`'s third argument is now a `datetime` representing the
  expiration time of the device code
  - optional keyword argument `tenant` renamed `tenant_id`
- Changes to `ManagedIdentityCredential`
  - now accepts no positional arguments, and only one keyword argument:
  `client_id`
  - transport configuration is now done through keyword arguments as
  described in
  [`azure-core` documentation](https://github.com/Azure/azure-sdk-for-python/blob/azure-identity_1.0.0/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport)

### Fixes and improvements:
- Authenticating with a single sign-on shared with other Microsoft applications
only requires a username when multiple users have signed in
([#8095](https://github.com/Azure/azure-sdk-for-python/pull/8095))
- `DefaultAzureCredential` accepts an `authority` keyword argument, enabling
its use in national clouds
([#8154](https://github.com/Azure/azure-sdk-for-python/pull/8154))

### Dependency changes
- Adopted [`msal_extensions`](https://pypi.org/project/msal-extensions/) 0.1.2
- Constrained [`msal`](https://pypi.org/project/msal/) requirement to >=0.4.1,
<1.0.0


## 1.0.0b4 (2019-10-07)
### New features:
- `AuthorizationCodeCredential` authenticates with a previously obtained
authorization code. See Azure Active Directory's
[authorization code documentation](https://docs.microsoft.com/azure/active-directory/develop/v2-oauth2-auth-code-flow)
for more information about this authentication flow.
- Multi-cloud support: client credentials accept the authority of an Azure Active
Directory authentication endpoint as an `authority` keyword argument. Known
authorities are defined in `azure.identity.KnownAuthorities`. The default
authority is for Azure Public Cloud, `login.microsoftonline.com`
(`KnownAuthorities.AZURE_PUBLIC_CLOUD`). An application running in Azure
Government would use `KnownAuthorities.AZURE_GOVERNMENT` instead:
>```
>from azure.identity import DefaultAzureCredential, KnownAuthorities
>credential = DefaultAzureCredential(authority=KnownAuthorities.AZURE_GOVERNMENT)
>```

### Breaking changes:
- Removed `client_secret` parameter from `InteractiveBrowserCredential`

### Fixes and improvements:
- `UsernamePasswordCredential` correctly handles environment configuration with
no tenant information ([#7260](https://github.com/Azure/azure-sdk-for-python/pull/7260))
- user realm discovery requests are sent through credential pipelines
([#7260](https://github.com/Azure/azure-sdk-for-python/pull/7260))


## 1.0.0b3 (2019-09-10)
### New features:
- `SharedTokenCacheCredential` authenticates with tokens stored in a local
cache shared by Microsoft applications. This enables Azure SDK clients to
authenticate silently after you've signed in to Visual Studio 2019, for
example. `DefaultAzureCredential` includes `SharedTokenCacheCredential` when
the shared cache is available, and environment variable `AZURE_USERNAME`
is set. See the
[README](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md#single-sign-on)
for more information.

### Dependency changes:
- New dependency: [`msal-extensions`](https://pypi.org/project/msal-extensions/)
0.1.1

## 1.0.0b2 (2019-08-05)
### Breaking changes:
- Removed `azure.core.Configuration` from the public API in preparation for a
revamped configuration API. Static `create_config` methods have been renamed
`_create_config`, and will be removed in a future release.

### Dependency changes:
- Adopted [azure-core](https://pypi.org/project/azure-core/) 1.0.0b2
  - If you later want to revert to a version requiring azure-core 1.0.0b1,
  of this or another Azure SDK library, you must explicitly install azure-core
  1.0.0b1 as well. For example:
  `pip install azure-core==1.0.0b1 azure-identity==1.0.0b1`
- Adopted [MSAL](https://pypi.org/project/msal/) 0.4.1
- New dependency for Python 2.7: [mock](https://pypi.org/project/mock/)

### New features:
- Added credentials for authenticating users:
 - `DeviceCodeCredential`
 - `InteractiveBrowserCredential`
 - `UsernamePasswordCredential`
  - async versions of these credentials will be added in a future release

## 1.0.0b1 (2019-06-28)
Version 1.0.0b1 is the first preview of our efforts to create a user-friendly
and Pythonic authentication API for Azure SDK client libraries. For more
information about preview releases of other Azure SDK libraries, please visit
https://aka.ms/azure-sdk-preview1-python.

This release supports service principal and managed identity authentication.
See the
[documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md)
for more details. User authentication will be added in an upcoming preview
release.

This release supports only global Azure Active Directory tenants, i.e. those
using the https://login.microsoftonline.com authentication endpoint.
