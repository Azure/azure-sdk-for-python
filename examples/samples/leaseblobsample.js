/**
* This sample demonstrates how multiple clients can attempt to acquire a lease in order to provide a locking mechanism
* over write operations on a given blob.
*
* To simulate N workers please run multiple instances of this sample. Each instance will :
*
* 1. Try to acquire a lease on a uploaded blob.
*
* 2. If succeed, then renew the lease, print out the current process holds the lease every 40 seconds until the process
* is killed.
*
* 3. If fail, then sleep for 10 seconds and go back to step 1.
*
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

var workerWithLeaseSleepTimeInMs = 40 * 1000;
var workerWithoutLeaseSleepTimeInMs = 10 * 1000;

var container = 'leasesample';
var blob = 'leasesample';
var leaseId;

var blobClient = azure.createBlobService();

function createContainer(callback) {
  // Step 0: Check if the target container exists.
  blobClient.createContainerIfNotExists(container, function () {
    console.log('Created the container ' + container);
    callback();
  });
};

function uploadBlob(callback) {
  // Step 1: Create text blob.
  blobClient.createBlockBlobFromText(container, blob, 'Hello world!', function () {
    console.log('Created the blob ' + blob);
    callback();
  });
};

function getLease(currentLease) {
  if (currentLease == null) {
    // Step 2a: this worker doesn't hold a lease, then try to acquire the lease.
    blobClient.acquireLease(container, blob, function (leaseError, lease) {
      if (lease != null) {
        leaseId = lease.id;

        // Succeed in acquiring a lease.
        console.log('Worker acquired the lease whose ID is ' + leaseId);

        setTimeout(function () {
          getLease(lease);
        }, workerWithLeaseSleepTimeInMs);
      }
      else {
        // Fail in acquiring a lease.
        console.log('Worker failed in acquiring the lease.');

        setTimeout(function () {
          getLease(null);
        }, workerWithoutLeaseSleepTimeInMs);
      }
    });
  }
  else {
    // Step 2b: This worker holds a lease, then renew the lease.

    // Traditionally there is some work this worker must do while it 
    // holds the lease on the blob prior to releasing it.
    blobClient.renewLease(container, blob, leaseId, function (leaseError, lease) {
      if (lease) {
        console.log('Worker renewed the lease whose ID is ' + lease.id);
      }
      else {
        console.log('Worker failed in renewing the lease.');
      }

      setTimeout(function () {
        getLease(lease);
      }, workerWithLeaseSleepTimeInMs);
    });
  }
};

var arguments = process.argv;

if (arguments.length > 3) {
  console.log('Incorrect number of arguments');
}
else if (arguments.length == 3) {
  // Adding a third argument on the command line, whatever it is, will delete the container before running the sample.
  blobClient.deleteContainer(container, function () {
    createContainer(function () {
      uploadBlob(function () {
        getLease(null);
      });
    });
  });
}
else {
  createContainer(function () {
    uploadBlob(function () {
      getLease(null);
    });
  });
}