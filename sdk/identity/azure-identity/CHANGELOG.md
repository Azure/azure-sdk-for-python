# Release History

## 1.5.0b3 (Unreleased)
### Breaking Changes
- Renamed optional `CertificateCredential` keyword argument `send_certificate`
  to `send_certificate_chain`

### Changed
- `DeviceCodeCredential` parameter `client_id` is now optional. When not
   provided, the credential will authenticate users to an Azure development
   application.
   ([#14354](https://github.com/Azure/azure-sdk-for-python/issues/14354))

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
[azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md#transport)
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
[README](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md#single-sign-on)
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
[documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md)
for more details. User authentication will be added in an upcoming preview
release.

This release supports only global Azure Active Directory tenants, i.e. those
using the https://login.microsoftonline.com authentication endpoint.
