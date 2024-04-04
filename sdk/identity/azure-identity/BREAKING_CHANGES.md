# Breaking Changes

## 1.16.0

### Behavioral change to `ManagedIdentityCredential` in IMDS managed identity scenarios

As of `azure-identity` 1.16.0, `ManagedIdentityCredential` makes a minor change to the retry behavior in environments where Instance Metadata Service (IMDS) managed identity is used. The retry backoff factor for IMDS requests was reduced to `0.8` from `2` to prevent excessive delays during retries and to improve responsiveness. This change might affect workloads that rely on the previous retry behavior.

If retry settings need to be customized for IMDS managed identity scenarios, users can pass in `RetryPolicy` parameters noted in the [Azure Core Client library developer reference](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies) to the `ManagedIdentityCredential` constructor. For example:

```python
credential = ManagedIdentityCredential(retry_connect=8, retry_backoff_factor=2)
```

## 1.11.0

### Behavioral change to credential types supporting multi-tenant authentication

As of `azure-identity` 1.11.0, the default behavior of credentials supporting multi-tenant authentication has changed. Each of these credentials will throw an `ClientAuthenticationError` if the requested `tenant_id` doesn't match the tenant ID originally configured on the credential. Apps must now do one of the following things:

- Add all IDs, of tenants from which tokens should be acquired, to the `additionally_allowed_tenants` list in the credential options. For example:

```py
credential = DefaultAzureCredential(additionally_allowed_tenants = ["<tenant_id_1>", "<tenant_id_2>"])
```

- Add `*` to enable token acquisition from any tenant. This is the original behavior and is compatible with previous versions supporting multi tenant authentication. For example:

```py
credential = DefaultAzureCredential(additionally_allowed_tenants=['*'])
```

Note: Credential types which do not require a `tenant_id` on construction will only throw `ClientAuthenticationError` when the application has provided a value for `tenant_id` in the constructor. If no `tenant_id` is specified when constructing the credential, the credential will acquire tokens for any requested `tenant_id` regardless of the value of `additionally_allowed_tenants`.

More information on this change and the consideration behind it can be found [here](https://aka.ms/azsdk/blog/multi-tenant-guidance).
