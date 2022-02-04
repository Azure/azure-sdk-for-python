# Troubleshooting Azure Identity Authentication Issues

The Azure Identity SDK offers various `TokenCredential` implementations. These implementations typically throw `CredentialUnavailableError` and `ClientAuthenticationError` exceptions.
The `CredentialUnavailableError` indicates that the credential cannot execute in the current environment setup due to lack of required configuration.
The `ClientAuthenticationError` indicates that the credential was able to run/execute but ran into an authentication issue from the server's end. This can happen due to invalid configuration/details passed in to the credential at construction time.
This troubleshooting guide covers mitigation steps to resolve these exceptions thrown by various `TokenCredential` implementations in the Azure Identity Python client library.

## Table of contents

- [Troubleshooting Default Azure Credential Authentication Issues](#troubleshooting-default-azure-credential-authentication-issues)
- [Troubleshooting Environment Credential Authentication Issues](#troubleshooting-environment-credential-authentication-issues)
- [Troubleshooting Service Principal Authentication Issues](#troubleshooting-service-principal-authentication-issues)
- [Troubleshooting Username Password Authentication Issues](#troubleshooting-username-password-authentication-issues)
- [Troubleshooting Managed Identity Authentication Issues](#troubleshooting-managed-identity-authentication-issues)
- [Troubleshooting Visual Studio Code Authentication Issues](#troubleshooting-visual-studio-code-authentication-issues)
- [Troubleshooting Azure CLI Authentication Issues](#troubleshooting-azure-cli-authentication-issues)
- [Troubleshooting Azure Powershell Authentication Issues](#troubleshooting-azure-powershell-authentication-issues)

## Troubleshooting Default Azure Credential Authentication Issues

### Credential Unavailable Error

The `DefaultAzureCredential` attempts to retrieve an access token by sequentially invoking a chain of credentials. The `ClientAuthenticationError` in this scenario signifies that all the credentials in the chain failed to retrieve the token in the current environment setup/configuration. You need to follow the configuration instructions for the respective credential you're looking to use via `DefaultAzureCredential` chain, so that the credential can work in your environment.

Please follow the configuration instructions in the `Credential Unavailable Error` section of the troubleshooting guidelines below for the respective credential/authentication type you want to use via `DefaultAzureCredential`:

| Credential Type | Troubleshoot Guide |
| --- | --- |
| Environment Credential | [Environment Credential Troubleshooting Guide](#troubleshooting-environment-credential-authentication-issues) |
| Managed Identity Credential | [Managed Identity Troubleshooting Guide](#troubleshooting-managed-identity-authentication-issues) |
| Visual Studio Code Credential | [Visual Studio Code Troubleshooting Guide](#troubleshooting-visual-studio-code-authentication-issues) |
| Azure CLI Credential | [Azure CLI Troubleshooting Guide](#troubleshooting-azure-cli-authentication-issues) |
| Azure Powershell Credential | [Azure Powershell Troubleshooting Guide](#troubleshooting-azure-powershell-authentication-issues) |

## Troubleshooting Environment Credential Authentication Issues

### Credential Unavailable Error

#### Environment variables not configured

The `EnvironmentCredential` supports Service Principal authentication and Username + Password authentication. To utilize the desired way of authentication via `EnvironmentCredential`, you need to ensure the environment variables below are configured properly and the application is able to read them.

##### Service principal with secret

| Variable Name | Value |
| --- | --- |
AZURE_CLIENT_ID | ID of an Azure Active Directory application. |
AZURE_TENANT_ID |ID of the application's Azure Active Directory tenant. |
AZURE_CLIENT_SECRET | One of the application's client secrets. |

##### Service principal with certificate

| Variable name | Value |
| --- | --- |
AZURE_CLIENT_ID |ID of an Azure Active Directory application. |
AZURE_TENANT_ID | ID of the application's Azure Active Directory tenant. |
AZURE_CLIENT_CERTIFICATE_PATH | Path to a PEM-encoded or PKCS12 certificate file including private key (without password protection). |

##### Username and password

| Variable name | Value |
| --- | --- |
AZURE_CLIENT_ID | ID of an Azure Active Directory application. |
AZURE_USERNAME | A username (usually an email address). |
AZURE_PASSWORD | The associated password for the given username. |

### Client Authentication Error

The `EnvironmentCredential` supports Service Principal authentication and Username + Password authentication.
Please follow the troubleshooting guidelines below for the respective authentication which you tried and failed.

| Authentication Type | Troubleshoot Guide |
| --- | --- |
| Service Principal | [Service Principal Auth Troubleshooting Guide](#troubleshooting-username-password-authentication-issues) |
| Username Password | [Username Password Auth Troubleshooting Guide](#troubleshooting-username-password-authentication-issues) |

## Troubleshooting Username Password Authentication Issues

### Two Factor Authentication Required Error

The `UsernamePassword` credential works only for users whose two factor authentication has been disabled in Azure Active Directory. You can change the Multi Factor Authentication in Azure Portal by following the steps [here](https://docs.microsoft.com/azure/active-directory/authentication/howto-mfa-userstates#change-the-status-for-a-user).

## Troubleshooting Service Principal Authentication Issues

### Illegal/Invalid Argument Issues

#### Client Id

The Client Id is the application Id of the registered application / service principal in Azure Active Directory.
It is a required parameter for `ClientSecretCredential` and `ClientCertificateCredential`. If you have already created your service principal
then you can retrieve the client/app id by following the instructions [here](https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal#get-tenant-and-app-id-values-for-signing-in).

#### Tenant Id

The tenant id is te Global Unique Identifier (GUID) that identifies your organization. It is a required parameter for
`ClientSecretCredential` and `ClientCertificateCredential`. If you have already created your service principal
then you can retrieve the client/app id by following the instructions [here](https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal#get-tenant-and-app-id-values-for-signing-in).

### Client Secret Credential Issues

#### Client Secret Argument

The client secret is the secret string that the application uses to prove its identity when requesting a token; this can also be referred to as an application password.
If you have already created a service principal you can follow the instructions [here](https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal#option-2-create-a-new-application-secret) to create a client secret for your application.

### Client Certificate Credential Issues

#### Client Certificate Argument

The `Client Certificate Credential` accepts `pfx` and `pem` certificates. The certificate needs to be associated with your registered application/service principal. To create and associate a certificate with your registered app, please follow the instructions [here](https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal#option-1-upload-a-certificate).

### Create a new service principal

Please follow the instructions [here](https://docs.microsoft.com/cli/azure/create-an-azure-service-principal-azure-cli) to create a new service principal.

## Troubleshooting Managed Identity Authentication Issues

### Credential Unavailable Error

#### Connection Timed Out / Connection could not be established / Target Environment could not be determined

Currently azure-identity supports [managed identity authentication](https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview)
in the below listed Azure services; ensure you're running your application on one of these resources and have enabled the Managed Identity on
them by following the instructions at their configuration links below.

Azure Service | Managed Identity Configuration
--- | --- |
[Azure Virtual Machines](https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/how-to-use-vm-token) | [Configuration Instructions](https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/qs-configure-portal-windows-vm)
[Azure App Service](https://docs.microsoft.com/azure/app-service/overview-managed-identity?tabs=python) | [Configuration Instructions](https://docs.microsoft.com/azure/app-service/overview-managed-identity?tabs=python)
[Azure Kubernetes Service](https://docs.microsoft.com/azure/aks/use-managed-identity) | [Configuration Instructions](https://docs.microsoft.com/azure/aks/use-managed-identity)
[Azure Cloud Shell](https://docs.microsoft.com/azure/cloud-shell/msi-authorization) |  |
[Azure Arc](https://docs.microsoft.com/azure/azure-arc/servers/managed-identity-authentication) | [Configuration Instructions](https://docs.microsoft.com/azure/azure-arc/servers/security-overview#using-a-managed-identity-with-arc-enabled-servers)
[Azure Service Fabric](https://docs.microsoft.com/azure/service-fabric/concepts-managed-identity) | [Configuration Instructions](https://docs.microsoft.com/azure/service-fabric/configure-existing-cluster-enable-managed-identity-token-service)

## Troubleshooting Visual Studio Code Authentication Issues

### Credential Unavailable Error

#### Failed To Read VS Code Credentials / Authenticate via Azure Tools plugin in VS Code

The `VS Code Credential` failed to read the credential details from the cache.

The Visual Studio Code authentication is handled by an integration with the Azure Account extension.
To use this form of authentication, ensure that you have installed the Azure Account extension,
then use View > Command Palette to execute the Azure: Sign In command. This command opens a browser window and displays a page that allows you 
to sign in to Azure. After you've completed the login process, you can close the browser as directed. Running your application
(either in the debugger or anywhere on the development machine) will use the credential from your sign-in.

If you already had the Azure Account extension installed and had logged in to your account. Then try logging out and logging in again, as
that will re-populate the cache on the disk and potentially mitigate the error you're getting.

#### Msal Interaction Required Error

THe `VS Code Credential` was able to read the cached credentials from the cache but the cached token is likely expired.
Log into the Azure Account extension by via View > Command Palette to execute the Azure: Sign In command in the VS Code IDE.

#### ADFS Tenant Not Supported

The ADFS Tenants are not supported via the Azure Account extension in VS Code currently.
The supported clouds are:

Azure Cloud | Cloud Authority Host
--- | --- |
AZURE PUBLIC CLOUD | https://login.microsoftonline.com/
AZURE GERMANY | https://login.microsoftonline.de/
AZURE CHINA | https://login.chinacloudapi.cn/
AZURE GOVERNMENT | https://login.microsoftonline.us/

## Troubleshooting Azure CLI Authentication Issues

### Credential Unavailable Error

#### Azure CLI Not Installed

To use Azure CLI credential, the Azure CLI needs to be installed, please follow the instructions [here](https://docs.microsoft.com/cli/azure/install-azure-cli)
to install it for your platform and then try running the credential again.

#### Azure account not logged in

`AzureCliCredential` authenticates as the identity currently logged in to Azure CLI.
You need to login to your account in Azure CLI via `az login` command. You can further read instructions to [Sign in with Azure CLI](https://docs.microsoft.com/cli/azure/authenticate-azure-cli).
Once logged in try running the credential again.

### Illegal State

#### Safe Working Directory Not Located

The `Azure CLI Credential` was not able to locate a value for System Environment property `SystemRoot` to execute in.
Please ensure the `SystemRoot` environment variable is configured to a safe working directory and then try running the credential again.

## Troubleshooting Azure Powershell Authentication Issues

### Credential Unavailable Error

#### Powershell not installed

Please ensure PowerShell is installed on your platform by following the instructions [here](https://docs.microsoft.com/powershell/scripting/install/installing-powershell?view=powershell-7.1).

#### Azure Az Module Not Installed

Please follow the instructions [here](https://docs.microsoft.com/powershell/azure/install-az-ps)
to install the Azure Az PowerShell module.

#### Azure account not logged in

Log in via the `Connect-AzAccount` command. See [Sign in with Azure Powershell](https://docs.microsoft.com/powershell/azure/authenticate-azureps) for more information.

#### Deserialization error

The `Azure Powershell Credential` was able to retrieve a response from the Azure Powershell when attempting to get an access token but failed
to parse that response.
In your local powershell window, run the following command to ensure that Azure Powershell is returning an access token in correct format.

```pwsh
Get-AzAccessToken -ResourceUrl "<Scopes-Url>"
```

In the event above command is not working properly, follow the instructions to resolve the Azure Powershell issue being faced and then try running the credential again.
