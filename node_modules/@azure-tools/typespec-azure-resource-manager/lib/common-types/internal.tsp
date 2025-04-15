namespace Azure.ResourceManager.CommonTypes;

/**
 * An internal enum to indicate the resource support for various path types
 */
enum ResourceHome {
  @doc("The resource is bound to a tenant")
  Tenant,

  @doc("The resource is bound to a subscription")
  Subscription,

  @doc("The resource is bound to a location")
  Location,

  @doc("The resource is bound to a resource group")
  ResourceGroup,

  @doc("The resource is bound to an extension")
  Extension,
}

/** Alias of keyEncryptionKeyIdentity for back compatibility. Please change to keyEncryptionKeyIdentity. */
alias KeyEncryptionIdentity = KeyEncryptionKeyIdentity;
