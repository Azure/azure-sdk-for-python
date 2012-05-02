/**
* 1. Demonstrates how to upload all files from a given directory in parallel
* 
* 2. Demonstrates how to download all files from a given blob container to a given destination directory.
* 
* 3. Demonstrate making requests using AccessConditions.
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
var fs = require('fs');

var container = 'updownsample';
var blob = 'updownsample';
var blobAccess = 'updownaccesssample';

var blobService = azure.createBlobService();

var processArguments = process.argv;

function createContainer() {
  // Step 0: Create the container.
  blobService.createContainerIfNotExists(container, function (error) {
    if (error) {
      console.log(error);
    }
    else {
      console.log('Created the container ' + container);
      uploadSample();
    }
  });
}

function uploadSample() {
  // Sample 1 : Demonstrates how to upload all files from a given directoy
  uploadBlobs(processArguments[2], container, function () {

    // Sample 2 : Demonstrates how to download all files from a given
    // blob container to a given destination directory.
    downloadBlobs(container, processArguments[3], function () {

      // Sample 3 : Demonstrate making requests using AccessConditions.
      requestAccessConditionSample(container);
    });
  });
}

function uploadBlobs(sourceDirectoryPath, containerName, callback) {
  // Step 0 : validate directory is valid.
  if (!path.existsSync(sourceDirectoryPath)) {
    console.log(sourceDirectoryPath + ' is an invalid directory path.');
  } else {
    listFilesUpload(sourceDirectoryPath, containerName, callback);
  }
}

function listFilesUpload(sourceDirectoryPath, containerName, callback) {
  // Step 1 : Search the directory and generate a list of files to upload.
  walk(sourceDirectoryPath, function (error, files) {
    if (error) {
      console.log(error);
    } else {
      uploadFilesParallel(files, containerName, callback);
    }
  });
}

function uploadFilesParallel(files, containerName, callback) {
  var finished = 0;

  // Step 3 : generate and schedule an upload for each file
  files.forEach(function (file) {
    var blobName = file.replace(/^.*[\\\/]/, '');

    blobService.createBlockBlobFromFile(containerName, blobName, file, function (error) {
      finished++;

      if (error) {
        console.log(error);
      } else {
        console.log('Blob ' + blobName + ' upload finished.');

        if (finished === files.length) {
          // Step 4 : Wait until all workers complete and the blobs are uploaded
          // to the server.
          console.log('All files uploaded');
          callback();
        }
      }
    });
  });
}

function downloadBlobs(containerName, destinationDirectoryPath, callback) {
  // Step 0. Validate directory
  if (!path.existsSync(destinationDirectoryPath)) {
    console.log(destinationDirectoryPath + ' is an invalid directory path.');
  } else {
    downloadFilesParallel(containerName, destinationDirectoryPath, callback);
  }
}

function downloadFilesParallel(containerName, destinationDirectoryPath, callback) {
  // NOTE: does not handle pagination.
  blobService.listBlobs(containerName, function (error, blobs) {
    if (error) {
      console.log(error);
    } else {
      var blobsDownloaded = 0;

      blobs.forEach(function (blob) {
        blobService.getBlobToFile(containerName, blob.name, destinationDirectoryPath + '/' + blob.name, function (error2) {
          blobsDownloaded++;

          if (error2) {
            console.log(error2);
          } else {
            console.log('Blob ' + blob.name + ' download finished.');

            if (blobsDownloaded === blobs.length) {
              // Step 4 : Wait until all workers complete and the blobs are downloaded
              console.log('All files downloaded');
              callback();
            }
          }
        });
      });
    }
  });
}

function requestAccessConditionSample(containerName) {
  // Step 1: Create a blob.
  blobService.createBlockBlobFromText(containerName, blobAccess, 'hello', function (error) {
    if (error) {
      console.log(error);
    } else {
      console.log('Created the blob ' + blobAccess);
      downloadBlobProperties(containerName, blobAccess);
    }
  });
}

function downloadBlobProperties(containerName, blobName) {
  // Step 2 : Download the blob attributes to get the ETag.
  blobService.getBlobProperties(containerName, blobName, function (error, blob) {
    if (error) {
      console.log(error);
    } else {
      console.log('Blob Etag is: ' + blob.etag);
      testAccess(containerName, blobName, blob.etag);
    }
  });
}

function testAccess(containerName, blobName, etag) {
  // Step 2: Use the If-not-match ETag condition to access the blob. By
  // using the IfNoneMatch condition we are asserting that the blob needs
  // to have been modified in order to complete the request. In this
  // sample no other client is accessing the blob, so this will fail as
  // expected.

  var options = { accessConditions: { 'If-None-Match': etag} };
  blobService.createBlockBlobFromText(containerName, blobName, 'new hello', options, function (error) {
    if (error) {
      console.log('Got an expected exception. Details:');
      console.log(error);
    } else {
      console.log('Blob was incorrectly updated');
    }
  });
}

if (processArguments.length > 5 || processArguments.length < 4) {
  console.log('Incorrect number of arguments');
}
else if (processArguments.length == 5) {
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

// Utilitary functions

var walk = function (dir, done) {
  var results = [];
  fs.readdir(dir, function (err, list) {
    if (err) return done(err);
    var i = 0;
    (function next() {
      var file = list[i++];
      if (!file) return done(null, results);
      file = dir + '/' + file;
      fs.stat(file, function (err2, stat) {
        if (stat && stat.isDirectory()) {
          walk(file, function (err3, res) {
            results = results.concat(res);
            next();
          });
        } else {
          results.push(file);
          next();
        }
      });
    })();
  });
};