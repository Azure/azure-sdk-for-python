/**
* Demonstrates how to define a customized retry policy.
* 
* In this sample, we define a customized retry policy which retries on the "The specified container is being deleted"
* exception besides the server exceptions.
* 
* Note that only in the cloud(not the storage emulator), "The specified container is being deleted" exceptions will be
* sent if users immediately recreate a container after delete it.
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
var ExponentialRetryPolicyFilter = azure.ExponentialRetryPolicyFilter;

var util = require('util');

var container = 'retrypolicysample';

var blobServiceNoRetry = azure.createBlobService();
var blobService;

function setRetryPolicy() {
  // Step 1 : Set the retry policy to customized retry policy which will
  // retry on any status code other than the excepted one, including
  // the "The specified container is being deleted" exception .

  var retryOnContainerBeingDeleted = new ExponentialRetryPolicyFilter();
  retryOnContainerBeingDeleted.retryCount = 3;
  retryOnContainerBeingDeleted.retryInterval = 30000;

  retryOnContainerBeingDeleted.shouldRetry = function(statusCode, retryData) {
    console.log('Made the request at ' + new Date().toUTCString() + ', received StatusCode: ' + statusCode);

    var currentCount = (retryData && retryData.retryCount) ? retryData.retryCount : 0;

    return (currentCount < this.retryCount);
  };

  blobService = blobServiceNoRetry.withFilter(retryOnContainerBeingDeleted);
  createContainer();
}

function createContainer() {
  // Step 2: Create a container with a random name.
  blobService.createContainer(container, function(error) {
    if (error) {
      console.log(error);
    } else {
      console.log('Created the container ' + container);
      deleteContainer();
    }
  });
}

function deleteContainer() {
  // Step 3 : Delete a container.
  blobService.deleteContainer(container, function (error) {
    if (error) {
      console.log(error);
    } else {
      console.log('Deleted the container ' + container);
      createContainerAgain();
    }
  });
};

function createContainerAgain() {
  // Step 4 : Attempt to create the container immediately while it was still beeing deleted.
  blobService.createContainer(container, function (error) {
    if (error) {
      console.log(error);
    } else {
      console.log('Created the container ' + container);
    }
  });
};

var arguments = process.argv;

if (arguments.length > 3) {
  console.log('Incorrect number of arguments');
}
else if (arguments.length == 3) {
  // Adding a third argument on the command line, whatever it is, will delete the container before running the sample.
  blobServiceNoRetry.deleteContainer(container, function (error) {
    if (error) {
      console.log(error);
    } else {
      setRetryPolicy();
    }
  });
}
else {
  setRetryPolicy();
}