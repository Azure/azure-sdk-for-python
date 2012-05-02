/**
* In this sample, we demonstrate how to generate and use the blob level shared access signature and the container level
* shared access signature.
* 
* In the blob level shared access signature sample, there are the following steps: 
* 
* a. Create a container and a blob.
*
* b. Generate a shared access signature URL for the blob.
*
* c. Download that blob through that URL (should fail as the policy was never uploaded).
* 
* In the container level shared access signature sample, there are the following steps:
*
* a. Create a container and a blob.
*
* b. Upload a "ReadWrite" policy and a "Read" permission to the container, generate their shared access
* signatures.
*
* c. Use both shared access signatures to read that blob (Expect a failure from the "Read" permission shared access signature since it has already expired.).
*/

var path = require('path');
if (path.existsSync('./../../lib/azure.js')) {
  azure = require('./../../lib/azure');
} else {
  azure = require('azure');
}

var BlobConstants = azure.Constants.BlobConstants;
var ServiceClient = azure.ServiceClient;
var CloudBlobClient = azure.CloudBlobClient;

var util = require('util');
var ISO8061Date = require('../../lib/util/iso8061date');

var container = 'sassample';
var blob = 'sassample';

var blobService = azure.createBlobService();

function createContainer() {
  // Step 0: Create the container.
  blobService.createContainerIfNotExists(container, function (error) {
    if (error) {
      console.log(error);
    }
    else {
      console.log('Created the container ' + container);
      createBlob();
    }
  });
}

function createBlob() {
  // Step 1: Create the blob
  blobService.createBlockBlobFromText(container, blob, 'test blob', function (error) {
    if (error) {
      console.log(error);
    }
    else {
      console.log('Created the blob ' + container);
      downloadBlobUsingSharedAccessSignature();
    }
  });
}

function downloadBlobUsingSharedAccessSignature() {
  var startDate = new Date();
  var expiryDate = new Date(startDate);
  expiryDate.setMinutes(startDate.getMinutes() + 5);

  var sharedAccessPolicy = {
    AccessPolicy: {
      Permissions: azure.Constants.BlobConstants.SharedAccessPermissions.READ,
      Start: startDate,
      Expiry: expiryDate
    }
  };

  var signature = blobService.generateSharedAccessSignature(container, blob, sharedAccessPolicy);

  var sharedBlobService = azure.createBlobService();
  var sharedAccessSignature = new azure.SharedAccessSignature(sharedBlobService.storageAccount, sharedBlobService.storageAccessKey);
  sharedBlobService.authenticationProvider = sharedAccessSignature;

  sharedAccessSignature.permissionSet = [signature];

  // Step 3: Download the blob by using the shared access signature URL. Since the read policy was never uploaded this should fail.
  sharedBlobService.getBlobProperties(container, blob, function (error) {
    if (error) {
      console.log('Failed to download the blob since the permission was invalid.');
    } else {
      console.log('Downloaded the blob ' + blob + ' by using the shared access signature URL ' + signature.url());
    }

    createPolicies();
  });
}

function createPolicies() {
  // Step 4: Create a "ReadWrite" policy and a "Read" policy.
  var readWriteStartDate = new Date();
  var readWriteExpiryDate = new Date(readWriteStartDate);
  readWriteExpiryDate.setMinutes(readWriteStartDate.getMinutes() + 10);

  var readWriteSharedAccessPolicy = {
    Id: 'readwrite',
    AccessPolicy: {
      Start: readWriteStartDate,
      Expiry: readWriteExpiryDate,
      Permissions: 'rw'
    }
  };

  var readSharedAccessPolicy = {
    Id: 'read',
    AccessPolicy: {
      Expiry: readWriteStartDate,
      Permissions: 'r'
    }
  };

  var options = {};
  options.signedIdentifiers = [readWriteSharedAccessPolicy, readSharedAccessPolicy];

  blobService.setContainerAcl(container, BlobConstants.BlobContainerPublicAccessType.CONTAINER, options, function(error) {
    if (error) {
      console.log(error);
    } else {
      console.log('Uploaded the permissions for the container ' + container);
      usePermissions(readWriteSharedAccessPolicy, readSharedAccessPolicy);
    }
  });
}

function usePermissions(readWriteSharedAccessPolicy, readSharedAccessPolicy) {
  // Step 5: Read, write the blob using the shared access signature from "ReadWrite" policy.
  var sharedAccessSignature = blobService.generateSharedAccessSignature(container, null, readWriteSharedAccessPolicy);

  var sharedBlobService = azure.createBlobService();
  var sharedAccessSignatureProvider = new azure.SharedAccessSignature(sharedBlobService.storageAccount, sharedBlobService.storageAccessKey);
  sharedBlobService.authenticationProvider = sharedAccessSignatureProvider;

  sharedAccessSignatureProvider.permissionSet = [sharedAccessSignature];

  sharedBlobService.getBlobProperties(container, blob, function (error) {
    if (error) {
      console.log('Failed to download the blob since the permission was invalid.');
    } else {
      console.log('Downloaded the blob ' + blob + ' by using the shared access signature URL ' + sharedAccessSignature.url());
    }

    useIncorrectPermission(readSharedAccessPolicy);
  });
}

function useIncorrectPermission(readSharedAccessPolicy) {
  // Step 6: Expect an exception from using the already expired "Read" permission to read the blob.
  var sharedAccessSignature = blobService.generateSharedAccessSignature(container, null, readSharedAccessPolicy);

  var sharedBlobService = azure.createBlobService();
  var sharedAccessSignatureProvider = new azure.SharedAccessSignature(sharedBlobService.storageAccount, sharedBlobService.storageAccessKey);
  sharedBlobService.authenticationProvider = sharedAccessSignatureProvider;

  sharedAccessSignatureProvider.permissionSet = [sharedAccessSignature];

  sharedBlobService.getBlobProperties(container, blob, function (error) {
    if (error) {
      console.log('Failed to download the blob since the permission was invalid.');
    } else {
      console.log('Downloaded the blob ' + blob + ' by using the shared access signature URL ' + sharedAccessSignature.url());
    }
  });
}

var arguments = process.argv;

if (arguments.length > 3) {
  console.log('Incorrect number of arguments');
}
else if (arguments.length == 3) {
  // Adding a third argument on the command line, whatever it is, will delete the container before running the sample.
  blobService.deleteContainer(container, function (error) {
    if (error) {
      console.log(error);
    } else {
      createContainer();
    }
  });
}
else {
  createContainer();
}