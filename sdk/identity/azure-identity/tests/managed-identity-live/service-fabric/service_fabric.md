# Testing azure-identity in Service Fabric

Setup for a Service Fabric cluster and two apps, used for testing managed identity using Azure.Identity.

The `sfmitestsystem` and `sfmitestuser` directories contain mock applications that use Azure.Identity's `ServiceFabricCredential` to request and verify Key Vault access tokens. The former application uses a system-assigned managed identity to do so, and the latter application uses a user-assigned managed identity.

The `arm-templates` directory contains Azure resource templates for creating these applications as well as a Service Fabric cluster to host them. The cluster template also deploys other resources that are necessary for running a cluster: a load balancer, public IP address, virtual machine scale set, virtual network, and two storage accounts.

### Environment requirements

> **Note:** All Azure resources used in the sample should be in the same region & resource group.

- This sample requires access to an Azure subscription and required privileges to create resources.
- [An SSH key pair is required.](https://docs.microsoft.com/azure/virtual-machines/linux/mac-create-ssh-keys#provide-an-ssh-public-key-when-deploying-a-vm)
- [Azure CLI is used to deploy resources and applications.](https://docs.microsoft.com/cli/azure/install-azure-cli?view=azure-cli-latest)
- Docker is needed to build and push the sample containerized services. Docker should be using Linux containers for building the application images that are provided.

### Clone this repository

From a command prompt window, run
```
git clone https://github.com/Azure/azure-sdk-for-python --single-branch --branch main --depth 1
cd azure-sdk-for-python/sdk/identity/azure-identity/tests/managed-identity-live/service-fabric
```

### Sections
- [Resource setup](#set-up-resources)
- [Application deployment](#set-up-and-deploy-the-applications)
- [Test validation](#run-the-tests)
- [Troubleshooting](#troubleshooting)

## Set up resources

You can skip to [Set Up and Deploy the Applications](#set-up-and-deploy-the-applications) if you have an existing Service Fabric cluster, key vault, storage account, container registry, and managed identity named "AdminUser".

### Log in and set the subscription

First, we need to log in to the Azure CLI and set the subscription that we want our resources to live in, to make the following steps easier. From a command prompt window, run:
```
az login
az account set -n $SUBSCRIPTION_NAME
```

### Create a resource group

This is only necessary if you don't have a resource group in this location and subscription. From your command prompt window, run:
```
az group create -n $RESOURCE_GROUP -l $LOCATION
```

### Create a user-assigned managed identity

From your command prompt window, run:
```
az identity create -g $RESOURCE_GROUP -n AdminUser
```

You will be prompted for this identity's principal ID and client ID in later steps. You can get these IDs by running:
```
az identity show -g $RESOURCE_GROUP -n AdminUser
```

### Create a key vault, certificate, and secret

Create your key vault:
```
az keyvault create -g $RESOURCE_GROUP -n $KEY_VAULT_NAME -l $LOCATION --sku standard --enabled-for-deployment true --enabled-for-template-deployment true
```

After creating the vault, [create a self-signed certificate](https://docs.microsoft.com/azure/key-vault/certificates/quick-create-portal#add-a-certificate-to-key-vault) in it using the [Azure Portal](https://portal.azure.com). You'll need to insert some of this certificate's properties into the cluster template later on.

### Create an Azure Container Registry

From your command prompt window, run:
```
az acr create -g $RESOURCE_GROUP -n $ACR_NAME -l $LOCATION --admin-enabled --sku basic
```

> **NOTE:** Don't use upper-case letters in the name of the container registry. A registry can be created with a name
> that includes upper-case letters, but you may be unable to authenticate to it.

### Deploy a managed identity-enabled cluster

At the time of writing, Service Fabric clusters must be deployed using the Azure Resource Manager in order to enable managed identity. Provided is a cluster ARM template that can be used to create a managed identity-enabled cluster once some required fields are completed. The template uses the cluster certificate provided by your key vault, creates a system-assigned identity, and enables the managed identity token service so deployed applications can access their identities.

To use the provided template:

1. Open `arm-templates/cluster.parameters.json` and complete the fields `clusterLocation`, `adminUserName`, `adminPassword`, `sourceVaultValue`, `certificateUrlValue`, `certificateThumbprint`, and `sshKeyData`. The placeholder values will describe how they should be completed.
2. In `arm-templates/cluster.parameters.json`, change all instances of `sfmi-test` to a unique name, like `<myusername>-sfmi-test`. Also, change the values of `applicationDiagnosticsStorageAccountName` and `supportLogStorageAccountName` to be similarly unique, but without hyphens. This will help ensure the deployment resource names do not conflict with the names of other public resources.
3. Start the deployment by running the following command in your command prompt:
```
az deployment group create -g $RESOURCE_GROUP -f arm-templates\cluster.template.json -p arm-templates\cluster.parameters.json
```

This will begin to deploy a Service Fabric cluster as well as other necessary resources: a load balancer, public IP address, virtual machine scale set, virtual network, and two storage accounts.

## Set up and deploy the applications

### Build and publish a Docker image for each application

For this manual test, each application will use a Docker image to run managed identity tests. To make these images available to Service Fabric, you need to publish them to a container registry.

1. Ensure Docker is running and is using Linux containers.
2. Authenticate to ACR:
```
az acr login -n $ACR_NAME
```
3. Build the images:
```
docker build --no-cache -t $ACR_NAME.azurecr.io/sfmitestsystem ..
docker build --no-cache -t $ACR_NAME.azurecr.io/sfmitestuser ..
```
4. Publish the images:
```
docker push $ACR_NAME.azurecr.io/sfmitestsystem
docker push $ACR_NAME.azurecr.io/sfmitestuser
```

### Package each application

Your Service Fabric cluster will target each application by referencing a `.sfpkg` in a storage account. First, you need to target your application images and create the package files.

1. In `sfmitestsystem/ApplicationManifest.xml` and `sfmitestuser/ApplicationManifest.xml`, fill in the values for your Azure Container Registry name and password in
```xml
<RepositoryCredentials AccountName="<ACR_NAME>" Password="<found in Access keys page of registry in Portal>" PasswordEncrypted="false"/>
```
2. In `sfmitestsystem/sfmitestsystemfrontPkg/ServiceManifest.xml`, replace `{ACR_NAME}` with your Azure Container Registry name in
```xml
<ImageName>{ACR_NAME}.azurecr.io/sfmitestsystem</ImageName>
```
3. Also in `sfmitestsystem/sfmitestsystemfrontPkg/ServiceManifest.xml`, replace `<KEY_VAULT_URL>` with your key vault's vault URI in
```xml
<EnvironmentVariable Name="AZURE_IDENTITY_TEST_VAULT_URL" Value="<KEY_VAULT_URL>"/>
```
4. Open the `sfmitestsystem` directory in File Explorer, select `sfmitestsystemfrontPkg` and `ApplicationManifest.xml`, and compress them into a zip file.
5. Rename the zip file `sfmitestsystem.sfpkg`.
6. In `sfmitestuser/sfmitestuserfrontPkg/ServiceManifest.xml`, replace `{ACR_NAME}` with your Azure Container Registry name in
```xml
<ImageName>{ACR_NAME}.azurecr.io/sfmitestuser</ImageName>
```
7. Also in `sfmitestuser/sfmitestuserfrontPkg/ServiceManifest.xml`, replace `<KEY_VAULT_URL>` with your key vault's vault URI and `<AdminUser client ID>` with the user-assigned managed identity's client ID in
```xml
<EnvironmentVariable Name="AZURE_IDENTITY_TEST_VAULT_URL" Value="<KEY_VAULT_URL>"/>
<EnvironmentVariable Name="AZURE_IDENTITY_TEST_MANAGED_IDENTITY_CLIENT_ID" Value="<AdminUser client ID>"/>
```
8. Open the `sfmitestuser` directory in File Explorer, select `sfmitestuserfrontPkg` and `ApplicationManifest.xml`, and compress them into a zip file.
9. Rename the zip file `sfmitestuser.sfpkg`.

### Upload the application packages to a storage account

If using an existing cluster, ensure your resource group has a storage account connected to your cluster. If you deployed a cluster using the template provided, two storage accounts were created but only one needs to store the `.sfpkg` files for the applications (the one with the name corresponding to `applicationDiagnosticsStorageAccountName` in the template).

Go to your resource group in the [Azure Portal](https://portal.azure.com) and click on the storage account. Go to the "Containers" page and create a new container named "apps" -- be sure the set the public access level to Blob.

Open the apps container and upload the `.sfpkg` files you created earlier in the walkthrough. The container should now contain `sfmitestsystem.sfpkg` and `sfmitestuser.sfpkg`. Keep this page open to complete the next step.

### Deploy the applications

This sample also provides templates for deploying Service Fabric applications with Azure CLI.

To use the provided templates:

1. Open `arm-templates/sfmitestsystem.parameters.json` and complete the fields `clusterName`, `clusterLocation`, and `applicationPackageUrl`. `clusterName` and `clusterLocation` should match the name and location of your Service Fabric cluster. `applicationPackageUrl` is the URL of the `.sfpkg` you uploaded to a storage account in the previous step. To find the URL, click on `sfmitestsystem.sfpkg` in the Portal to view its properties.
2. Open `arm-templates/sfmitestuser.parameters.json` and complete the same fields, using the URL of `sfmitestuser.sfpkg` for `applicationPackageUrl`.
3. Start the deployment by running the following commands in your command prompt:
```
az deployment group create -g $RESOURCE_GROUP -f arm-templates\sfmitestsystem.template.json -p arm-templates\sfmitestsystem.parameters.json
az deployment group create -g $RESOURCE_GROUP -f arm-templates\sfmitestuser.template.json -p arm-templates\sfmitestuser.parameters.json
```

### Give the applications access to your key vault

If the applications were accessed now, they would report an error. This is because their managed identities don't have permission to access secrets in the key vault you created.

To grant them access:

1. Get the object ID (`objectId`) of `sfmitestsystem`'s system-assigned managed identity. In your command prompt, run:
```
az ad sp list --display-name $CLUSTER_NAME/applications/sfmitestsystem
```
2. Give the application secret list permissions by setting an access policy:
```
az keyvault set-policy -n $KEY_VAULT_NAME --secret-permissions list --object-id $OBJECT_ID
```
3. Get the principal ID (`principalId`) of `sfmitestuser`'s user-assigned managed identity. In your command prompt, run:
```
az identity show -g $RESOURCE_GROUP -n AdminUser
```
4. Give the application secret list permissions by setting an access policy:
```
az keyvault set-policy -n $KEY_VAULT_NAME --secret-permissions list --object-id $PRINCIPAL_ID
```

## Run the tests

### Connect to your cluster on Service Fabric Explorer

Instructions on connecting to the Explorer can be found
[here](https://docs.microsoft.com/azure/service-fabric/service-fabric-connect-to-secure-cluster#connect-to-a-secure-cluster-using-service-fabric-explorer).
Adding a certificate to your local machine's browser is the recommended method of easily connecting to the Explorer;
instructions are below.

#### Add your self-signed certificate to your certificate store

First, go to the Key Vault you created earlier in the Azure Portal. Go to the "Certificates" page in the sidebar and
click on the certificate that you created earlier. Click on the current version of the certificate, and then click
"Download in PFX/PEM format" at the top of the following page.

After the certificate finishes downloading, open your browser's settings and find the option to manage HTTPS/SSL
certificates. On Windows, you should see a window open with a list of certificates in your Personal store -- click
"Import..." to open the Certificate Import Wizard. Browse your files to find the PFX certificate you downloaded from
Key Vault -- you may need to change the file extension filter to "Personal Information Exchange (\*.pfx;\*.p12)".
Import the certificate into your Personal store.

#### Troubleshooting: gain access to the Explorer endpoint

If you're using a corporate VPN and your browser can't connect to the Explorer endpoint because your request times out,
you may have to add a security rule to the network security group resource in your resource group (its name should
begin with "NRMS"). Be sure to first comply with
[security rules for ARM subnets](https://strikecommunity.azurewebsites.net/articles/3427/faq-simply-secure-network-security-rules-for-new-a.html).
[Here](https://strikecommunity.azurewebsites.net/articles/4889/can-not-access-my-non-production-resources-from-so-1.html)
is a page that discusses the known issue with VPN access to some resources.

To add a security rule, open the resource in the Azure Portal, and then go to the "Inbound security rules" page in the
sidebar. Click "Add" to add a new rule, and fill in the following settings:

- **Source:** IP Addresses
- **Source IP addresses/CIDR ranges:** [Your IP address]
- **Source port ranges:** *
- **Destination:** Any
- **Service:** Custom
- **Destination port ranges:** *
- **Protocol:** Any
- **Action:** Allow
- **Priority:** [Lower number than the priority of other rules -- most likely 100]
- **Name:** Allow-My-Machine

#### Connect to Service Fabric Explorer

After adding the certificate to your Personal store (and possibly adding a security rule), going to the Explorer
endpoint in your browser should present you with a page saying that the website is unsafe. This is because the Service
Fabric cluster is providing the self-signed certificate you created with your Key Vault, so this isn't an issue.
Proceed to the website (you may have to expand "Advanced" settings to do this).

You should be prompted for a certificate. Provide the certificate from your Key Vault that you imported to your
machine's certificate store.

### Verify test output

Once running on your cluster, the applications should each perform the same task: using a `ManagedIdentityCredential` to list your key vault's secret properties. One uses a system-assigned managed identity to do so, while the other uses a user-assigned managed identity. To verify that they have each done their job correctly, you can access the application logs in your cluster's Service Fabric Explorer page.

Verify in a browser:

1. Connect to your cluster on Service Fabric Explorer.
2. In the Explorer, you should see the applications running under the Applications tab. Otherwise, you may need to double check your deployment process.
3. Under the Nodes tab, expand each node tab to see if it hosts an application ("fabric:/sfmitestsystem" or "fabric:/sfmitestuser").
4. When you find an application entry, click the "+" sign by the name to expand it. There should be a "code" entry -- click on that to bring up a page that has a "Container Logs" tab.
5. Go to the "Container Logs" tab to see the test output. The tests will re-run every so often, so you may have to watch the page for a short while to see the output. Verify that `test_managed_identity_live` and `test_managed_identity_live_async` show `PASSED`.

This shows that the `ManagedIdentityCredential` works for Python 2.7. To test on Python 3.9, you'll need to re-build the Docker images and re-deploy the applications so they can target the new images.

1. Remove each application from the cluster. In the Service Fabric Explorer, expand the Applications tab and sfmitestsystemType tab. Click on "fabric:/sfmitestsystem", and in the application page, use the "Actions" tab at the top right to delete the application.
2. Now, remove the other application. Click on "fabric:/sfmitestuser" and use the "Actions" tab to delete the application.
3. Re-build the docker images, targeting Python 3.9 with `--build-arg`. In your command prompt, run:
```
docker build --no-cache --build-arg PYTHON_VERSION=3.9 -t $ACR_NAME.azurecr.io/sfmitestsystem ..
docker build --no-cache --build-arg PYTHON_VERSION=3.9 -t $ACR_NAME.azurecr.io/sfmitestuser ..
```
4. Publish the new images to your ACR:
```
docker push $ACR_NAME.azurecr.io/sfmitestsystem
docker push $ACR_NAME.azurecr.io/sfmitestuser
```
5. Re-deploy the applications:
```
az deployment group create -g $RESOURCE_GROUP -f arm-templates\sfmitestsystem.template.json -p arm-templates\sfmitestsystem.parameters.json
az deployment group create -g $RESOURCE_GROUP -f arm-templates\sfmitestuser.template.json -p arm-templates\sfmitestuser.parameters.json
```
6. Verify the test output again, as you did above. You should now also see that `test_managed_identity_live_async` shows `PASSED`.

## Troubleshooting

**Applications and/or nodes are in an error state**

This usually means that the applications are crashing or the Docker image is broken.
- Validate that you can run the tests locally and only see expected failures/errors for your environment.
- Validate that your Dockerfile has installed all necessary packages for the commands it attempts to run and that it
builds properly. Ensure any endpoints that are referenced by the Dockerfile are available (i.e. make sure URLs
are correct and that install commands will succeed locally). Double-check that commands are formatted correctly.

To push updates to the applications, deployed applications will first need to be deleted.
- In the Explorer, navigate down the "Applications" tab on the sidebar and expand "sfmitestsystemType". Click on
"fabric:/sfmitestsystem". In the top right of the following page, click on "Actions" and then "Delete
Application".
- After the application is deleted, click on "sfmitestsystemType" and in the top right of the following page, click
on "Actions" and then "Unprovision Type".
- Repeat the above steps for `sfmitestuser`.
- Re-deploy the applications after making any changes to your test and/or Docker images, using the deployment
commands in [Deploy the applications](#deploy-the-applications).

**The container logs page is showing an Error 404 upon refresh**

This is normal behavior, and just means that logs aren't available at that time. After refreshing for a while, logs
should appear.

**The Explorer page won't connect or the browser is blocking the endpoint**

Refer to [Connect to your cluster on Service Fabric Explorer](#connect-to-your-cluster-on-service-fabric-explorer).

If you're unable to get any information from the Explorer, there are also cluster logs that can be downloaded from one of the storage accounts that was deployed with the ARM template. These logs are composed of large text files that are very dense, but they can contain information about cluster failures that may help to diagnose problems.

- First, go to the resource group containing the Service Fabric cluster in the Azure Portal.
- Open up the storage account that's dedicated to logs. Its name matches `supportLogStorageAccountName` from `arm-templates/cluster.parameters.json`.
- Open the page of containers in the account. There should be a container with a name indicating that it contains cluster logs.
- Open the logs container. There should be a number of `.dtr` files. Each of these is a log file for a particular time range.
- Download a log file from a time when the cluster should have been attempting to run the test application.
- Open the log file locally using a text reader like Notepad (you may need to unzip it from a compressed folder first).
- Search for phrases that may be associated with an application event or failure. For example, you may want to search for the string "error" and iterate through instances until an event suggests that it was associated with the test application.
