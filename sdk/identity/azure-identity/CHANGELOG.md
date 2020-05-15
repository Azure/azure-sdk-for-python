# Release History

## 1.4.0b4 (Unreleased)
- `azure.identity.aio.AuthorizationCodeCredential.get_token()` no longer accepts
  optional keyword arguments `executor` or `loop`. Prior versions of the method
  didn't use these correctly, provoking exceptions, and internal changes in this
  version have made them obsolete.
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
  [`azure-core` documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/docs/configuration.md)

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
[authorization code documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)
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
[`DeviceCodeCredential`](https://azure.github.io/azure-sdk-for-python/ref/azure.identity.html#azure.identity.DeviceCodeCredential),
[`InteractiveBrowserCredential`](https://azure.github.io/azure-sdk-for-python/ref/azure.identity.html#azure.identity.InteractiveBrowserCredential),
[`UsernamePasswordCredential`](https://azure.github.io/azure-sdk-for-python/ref/azure.identity.html#azure.identity.UsernamePasswordCredential)
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
