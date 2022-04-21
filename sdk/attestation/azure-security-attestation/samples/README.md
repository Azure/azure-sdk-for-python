---
page_type: sample
languages:
    - python
products:
    - azure
    - azure-security-attestation
urlFragment: attestation-samples
---

# Samples for the Microsoft Azure Attestation client library for Python

These code samples show common scenario operations with the Azure Attestation client library.

The Async versions of the samples require Python 3.6 or later.

You can authenticate your client with a [TokenCredential](https://docs.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python).

See [sample_authentication.py][sample_authentication] and [sample_authentication_async.py][sample_authentication_async]

## Service operational modes

As was mentioned in the [README.md file][readme_md], the attestation service
operates in three different modes:

* Shared
* AAD
* Isolated

The core difference between the three modes of operation is the operations which
are permitted on each, and whether or not the customer needs to create an
instance of the provider.

Service Mode | Instance Creation  | Attestation | Policy Get | Policy Set | Signed Policies| Policy Management Certificate
------ | --- | ---- | ----  | --- | --- | ---
Shared | No | Yes | Yes (default always)| No | No | No
AAD | Yes | Yes | Yes | Yes | Optional | No
Isolated | Yes| Yes | Yes | Yes | Yes | Yes

### Shared Mode

Each region in which the MAA service operates has a "shared" attestation instance
which allows customers to perform basic attestation operations on their enclaves
without having to set up an attestation instance.
That instance is limited in what actions it can perform: The shared instance has
a "default" attestation policy which simply attests the correctness of the SGX
attestation collateral. It cannot be used for attestation types like `TPM` which
require that the customer provide an attestation policy. However, for customers
who simply need to perform attestation operations on an SGX enclave, they can use the shared instance without creating their own instance.

Examples of shared instances are:

* sharedeus2.eus2.attest.azure.net
* sharedcae.cae.attest.azure.net
* shareduks.uks.attest.azure.net

### AAD Mode

AAD mode instances are intended for customers who trust ARM RBAC for authorization
decisions related to policy management. Attestation policies are allowed to be
either be signed or unsigned.

### Isolated Mode

Isolated mode instances are intended for customers who desire an additional level
of authorization beyond that which is allowed by ARM RBAC authorization. When a
customer creates an isolated attestation instance, they also need to create an
RSA asymmetric key pair and an X.509 certificate which contains that asymmetric
key (the certificate can be self signed, or it can be issued by a certificate
authority). Attestation policies MUST be signed with one of the private keys
associated with the instance (either at instance creation or added with the [add_policy_management_certificate][add_policy_management_cert] API.

## Sample Requirements

These samples are written with the assumption that the following environment
variables have been set by the user:

* ATTESTATION_AAD_URL - the base URL for an attestation service instance in AAD mode.
* ATTESTATION_ISOLATED_URL - the base URL for an attestation service instance in Isolated mode.
* ATTESTATION_LOCATION_SHORT_NAME - the short name for the region in which the
    sample should be run - used to interact with the shared endpoint for that
    region.
* ATTESTATION_ISOLATED_SIGNING_CERTIFICATE - The DER encoded form of the signing
    certificate used to create an isolated attestation instance, Base64 encoded.
* ATTESTATION_ISOLATED_SIGNING_KEY - The DER encoded of an RSA Private key,
    Base64 encoded, which was used to create an isolated attestation service instance.

The tests also assume that the currently logged on user is authorized to call
into the attestation service instance because they use [DefaultAzureCredential](https://docs.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python) for authorization.

## Samples descriptions

**File Name** | **Description**
|-----|-------|
| [sample_authentication](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/attestation/azure-security-attestation/samples/sample_authentication.py) and [sample_authentication_async](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/attestation/azure-security-attestation/samples/sample_authentication_async.py) | Authenticate a connection with the attestation service (also retrieves the OpenID metadata configuration for the service instance).|
| [sample_attest_enclave](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/attestation/azure-security-attestation/samples/sample_attest_enclave.py) and [sample_attest_enclave_async](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/attestation/azure-security-attestation/samples/sample_attest_enclave_async.py) | Attest an SGX and OpenEnclave enclave with the attestation service. Also shows how to use the TokenValidationOptions to perform additional validation of the returned attestation token and validation keys.|
|[sample_get_set_policy](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/attestation/azure-security-attestation/samples/sample_get_set_policy.py) and [sample_get_set_policy_async](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/attestation/azure-security-attestation/samples) | Policy manipulation operations - Get, Set, Reset on different attestation types.|

### Prerequisites

* Python 2.7, or 3.6 or later is required to use this package.
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and either an
[Azure storage account](https://docs.microsoft.com/azure/storage/common/storage-account-overview) or an [Azure Cosmos Account](https://docs.microsoft.com/azure/cosmos-db/account-overview) to use this package.

## Setup

1. Install the Azure Attestation client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install --pre azure-security-attestation
```

1. Clone or download this sample repository
1. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
1. Set the environment variables specified in the sample file you wish to run.
1. Follow the usage described in the file, e.g. `python sample_attest_enclave.py`

## Additional Information

### Attestation Policy

An attestation policy is a document which defines authorization and claim generation
rules for attestation operations.

The following is an example of an attestation policy document for an SGX enclave:

```text
version= 1.0;
authorizationrules
{
    [ type=="x-ms-sgx-is-debuggable", value==false ] &&
    [ type=="x-ms-sgx-product-id", value==<product-id> ] &&
    [ type=="x-ms-sgx-svn", value>= 0 ] &&
    [ type=="x-ms-sgx-mrsigner", value=="<mrsigner>"]
        => permit();
};
issuancerules {
    c:[type=="x-ms-sgx-mrsigner"] => issue(type="<custom-name>", value=c.value);
};
```

There are two sections to the document: `authorizationrules` and `issuancerules`.
`authorizationrules` are rules which control whether or not an attestation token
should be issued. `issuancerules` are rules which cause claims to be issued in an
attestation token.

In the example, the attestation service will issue an attestation token if an only if
the SGX enclave is configured as follows:

* Not-Debuggable
* Enclave product ID: `<product-id>`.
* Enclave SVN: `<svn value>` greater or equal to zero.
* Enclave signer: matches `<mrsigner>`.

Assuming a token is issued, this policy will cause a claim named `<custom-name>`
to be issued with a value which matches the `x-ms-sgx-mrsigner` claim.

For more information on authoring attestation policy documents, see: [Authoring an attestation policy](https://docs.microsoft.com/azure/attestation/author-sign-policy)

## Next Steps

For more information about the Microsoft Azure Attestation service, please see our [documentation page](https://docs.microsoft.com/azure/attestation/) .

<!-- LINKS -->
<!-- links are known to be broken, they will be fixed after this initial pull
    request completes. -->
[readme_md]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/attestation/azure-security-attestation/README.md
[sample_authentication]:https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/attestation/azure-security-attestation/samples/sample_authentication.py
[sample_authentication_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/attestation/azure-security-attestation/samples/sample_authentication_async.py
[add_policy_management_cert]: https://docs.microsoft.com/python/api/azure-security-attestation/azure.security.attestation.attestationadministrationclient?view=azure-python-preview#add-policy-management-certificate-certificate-to-add--signing-key----kwargs-
