## Token caching in the Azure Identity client library

*Token caching* is a feature provided by the Azure Identity library that allows apps to:

- Improve their resilience and performance.
- Reduce the number of requests made to Azure Active Directory (Azure AD) to obtain access tokens.
- Reduce the number of times the user is prompted to authenticate.

When an app needs to access a protected Azure resource, it typically needs to obtain an access token from Azure AD. Obtaining that token involves sending a request to Azure AD and may also involve prompting the user. Azure AD then validates the credentials provided in the request and issues an access token.

Token caching, via the Azure Identity library, allows the app to store this access token [in memory](#in-memory-token-caching), where it's accessible to the current process, or [on disk](#persistent-token-caching) where it can be accessed across application or process invocations. The token can then be retrieved quickly and easily the next time the app needs to access the same resource. The app can avoid making another request to Azure AD, which reduces network traffic and improves resilience. Additionally, in scenarios where the app is authenticating users, token caching also avoids prompting the user each time new tokens are requested.

### In-memory token caching

*In-memory token caching* is the default option provided by the Azure Identity library. This caching approach allows apps to store access tokens in memory. With in-memory token caching, the library first determines if a valid access token for the requested resource is already stored in memory. If a valid token is found, it's returned to the app without the need to make another request to Azure AD. If a valid token isn't found, the library will automatically acquire a token by sending a request to Azure AD.

The in-memory token cache provided by the Azure Identity library can be used by multiple threads concurrently.

**Note:** When Azure Identity library credentials are used with Azure service libraries (for example, Azure Blob Storage), the in-memory token caching is active in the `HttpPipeline` layer as well. All `TokenCredential` implementations are supported there, including custom implementations external to the Azure Identity library.

### Persistent token caching

*Persistent disk token caching* is an opt-in feature in the Azure Identity library. The feature allows apps to cache access tokens in an encrypted, persistent storage mechanism. As indicated in the following table, the storage mechanism differs across operating systems.

| Operating system | Storage mechanism |
|------------------|-------------------|
| Linux            | Keyring           |
| macOS            | Keychain          |
| Windows          | DPAPI             |

Users can enable the cache to fall back to storing data in plaintext by setting the `allow_unencrypted_storage argument` to `True` in `TokenCachePersistenceOptions`. Enabling this does not disable encryption, but does allow plaintext storage as a fallback if encryption attempts fail. This is substantially less secure since tokens aren't encrypted to the current user, and anyone with access to the system could potentially access tokens from the cache. As such, enabling this setting is not recommended.

With persistent disk token caching enabled, the library first determines if a valid access token for the requested resource is already stored in the persistent cache. If a valid token is found, it's returned to the app without the need to make another request to Azure AD. Additionally, the tokens are preserved across app runs, which:

- Makes the app more resilient to failures.
- Ensures the app can continue to function during an Azure AD outage or disruption.
- Avoids having to prompt users to authenticate each time the process is restarted.

#### Code sample

The sample showcases how to activate persistence token caching in the credentials offered by the Azure Identity library. You need to specify `TokenCachePersistenceOptions` when creating the credential to activate persistent token caching.

```python
ClientSecretCredential(
    "tenant", "client-id", "secret", cache_persistence_options=TokenCachePersistenceOptions()
)
```

#### Persist user authentication record

When authenticating a user via `InteractiveBrowserCredential`, `DeviceCodeCredential`, or `UsernamePasswordCredential`, an `AuthenticationRecord` can be persisted as well. The authentication record is:

- Returned from the `authenticate` API and contains data identifying an authenticated account.
- Needed to identify the appropriate entry in the persisted token cache to silently authenticate on subsequent executions.

There's no sensitive data in the `AuthenticationRecord`, so it can be persisted in a non-protected state. Here's an example of an app storing the `AuthenticationRecord` to the local file system after authenticating the user:

```python
credential = InteractiveBrowserCredential(cache_persistence_options=TokenCachePersistenceOptions())
record = credential.authenticate()
record_json = record.serialize()
# Store the record_json to the local file system
```

#### Silently authenticating a user with AuthenticationRecord and TokenCachePersistenceOptions

Once an app has configured an `InteractiveBrowserCredential`, `DeviceCodeCredential`, or `UsernamePasswordCredential` to persist token data and an `AuthenticationRecord`, it's possible to silently authenticate. This example demonstrates an app setting the `TokenCachePersistenceOptions` and retrieving an `AuthenticationRecord` from the local file system to create an `InteractiveBrowserCredential` capable of silent authentication:

```python
deserialized_record = AuthenticationRecord.deserialize(record_json)
new_credential = InteractiveBrowserCredential(
    cache_persistence_options=TokenCachePersistenceOptions(), authentication_record=deserialized_record
)
```

The credential created in this example will silently authenticate given that a valid token for corresponding to the `AuthenticationRecord` still exists in the persisted token data. There are some cases where interaction will still be required such as on token expiry, or when additional authentication is required for a particular resource.

### Credentials supporting token caching

The following table indicates the state of in-memory and persistent caching in each credential type.

**Note:** In-memory caching is activated by default. Persistent token caching needs to be enabled as shown in this [code sample](#code-sample).

| Credential                     | In-memory token caching                                                | Persistent disk token caching |
|--------------------------------|------------------------------------------------------------------------|-------------------------------|
| `AuthorizationCodeCredential`  | Supported                                                              | Supported                     |
| `AzureCliCredential`           | Not Supported                                                          | Not Supported                 |
| `AzureDeveloperCliCredential`  | Not Supported                                                          | Not Supported                 |
| `AzurePowershellCredential`    | Not Supported                                                          | Not Supported                 |
| `ClientAssertionCredential`    | Supported                                                              | Not Supported                 |
| `CertificateCredential`        | Supported                                                              | Supported                     |
| `ClientSecretCredential`       | Supported                                                              | Supported                     |
| `DefaultAzureCredential`       | Supported if the target credential in the credential chain supports it | Not Supported                 |
| `DeviceCodeCredential`         | Supported                                                              | Supported                     |
| `InteractiveBrowserCredential` | Supported                                                              | Supported                     |
| `ManagedIdentityCredential`    | Supported                                                              | Not Supported                 |
| `OnBehalfOfCredential`         | Supported                                                              | Supported                     |
| `UsernamePasswordCredential`   | Supported                                                              | Supported                     |
| `WorkloadIdentityCredential`   | Supported                                                              | Not Supported                 |
