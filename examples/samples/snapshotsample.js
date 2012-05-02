/**
* This sample is used to provide an overview of blob snapshots and how to work with them.
* 
* 1. Upload 3 blocks and commit them.
* 
* 2. Take a snapshot for that blob.
* 
* 3. Re-upload one of the three blocks and commit them.
* 
* 4. Take a snapshot again.
* 
* 5. List blobs including snapshots.
* 
* 6. Promote the first snapshot.
* 
* 7. Delete the first snapshot.
* 
* 8. List all snapshots for this blob.
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

var container = 'snapshotsample';
var blob = 'snapshotsample';

var blockId1 = 'b1';
var blockId2 = 'b2';
var blockId3 = 'b3';

var blockContent1 = 'content1';
var blockContent2 = 'content2';
var blockContentAlternative2 = 'alternative2';
var blockContent3 = 'content3';

var blobClient = azure.createBlobService();

function createContainer() {
  // Step 0: Check if the target container exists.
  blobClient.createContainerIfNotExists(container, function (error) {
    if (error) {
      console.log(error);
    }
    else {
      console.log('Created the container ' + container);
      uploadblockBlobs();
    }
  });
}

function uploadblockBlobs() {
  // Step 1: Upload 3 blocks and commit them.
  var blockList = {
    LatestBlocks: [blockId1, blockId2, blockId3]
  };

  blobClient.createBlobBlockFromText(blockList.LatestBlocks[0], container, blob, blockContent1, blockContent1.length, function (error1) {
    if (error1) {
      console.log(error1);
    } else {
      console.log('Uploaded the block whose ID is ' + blockList.LatestBlocks[0]);
      blobClient.createBlobBlockFromText(blockList.LatestBlocks[1], container, blob, blockContent2, blockContent2.length, function (error2) {
        if (error2) {
          console.log(error2);
        } else {
          console.log('Uploaded the block whose ID is ' + blockList.LatestBlocks[1]);
          blobClient.createBlobBlockFromText(blockList.LatestBlocks[2], container, blob, blockContent3, blockContent3.length, function (error3) {
            if (error3) {
              console.log(error3);
            } else {
              console.log('Uploaded the block whose ID is ' + blockList.LatestBlocks[2]);
              blobClient.commitBlobBlocks(container, blob, blockList, function (error4) {
                if (error4) {
                  console.log(error4);
                }
                else {
                  console.log('Committed the blob ' + blob);
                  createSnapshot();
                }
              });
            }
          });
        }
      });
    }
  });
}

function createSnapshot() {
  // Step 2 : Creates a snapshot.
  blobClient.createBlobSnapshot(container, blob, function (error, snapshot1) {
    if (error) {
      console.log(error);
    } else {
      console.log('Created a snapshot for the blob ' + blob);

      createBlob(snapshot1);
    }
  });
}

function createBlob (snapshot) {
  // Step 3: Update the block 2, commit the blob again.
  blobClient.createBlobBlockFromText(blockId2, container, blob, blockContentAlternative2, blockContentAlternative2.length, function (error) {
    if (error) {
      console.log(error);
    } else {
      console.log('Uploaded the block whose ID is ' + blockId2);

      var blockList = {
        LatestBlocks: [blockId1, blockId2, blockId3]
      };

      blobClient.commitBlobBlocks(container, blob, blockList, function (error2) {
        if (error2) {
          console.log(error2);
        } else {
          console.log('Committed the blob ' + blob);
          createAnotherSnapshot(snapshot);
        }
      });
    }
  });
}

function createAnotherSnapshot (snapshot) {
  // Step 4 : Creates another snapshot.
  blobClient.createBlobSnapshot(container, blob, function (error) {
    if (error) {
      console.log(error);
    } else {
      console.log('Created a snapshot for the blob ' + blob);

      listSnapshots(snapshot);
    }
  });
};

function listSnapshots (snapshotId) {
  // Step 5 : List the blobs, including snapshots
  blobClient.listBlobs(container, { include: 'snapshots' }, function (error, blobResults) {
    if (error) {
      console.log(error);
    } else {
      console.log('Listing the blobs under the container ' + container);

      blobResults.forEach(function (blobResult) {
        console.log('  Blob: ' + blobResult.url);
      });

      promoteSnapshot(snapshotId);
    }
  });
};

function promoteSnapshot (snapshot) {
  // Step 6 : Promote, delete the snapshot1.
  blobClient.createBlockBlobFromText(container, blob, 'promoted', { snapshotId: snapshot }, function (error) {
    if (error) {
      console.log(error);
    } else {
      console.log('Promoted the snapshot ' + snapshot);
      deleteSnapshot(snapshot);
    }
  });
}

function deleteSnapshot (snapshot) {
  // Step 7 : Delete the first snapshot.
  blobClient.deleteBlob(container, blob, { snapshotId: snapshot }, function (error) {
    if (error) {
      console.log(error);
    } else {
      console.log('Deleted the snapshot ' + snapshot);

      listOnlySnapshots();
    }
  });
};

function listOnlySnapshots () {
  // Step 8 : List the snapshots.
  blobClient.listBlobs(container, { prefix: blob, include: 'snapshots' }, function (error, blobResults) {
    if (error) {
      console.log(error);
    } else {
      console.log('Listing snapshots for the blob ' + blob);

      blobResults.forEach(function (blobResult) {
        if (blobResult.snapshot) {
          console.log('  Snapshot: ' + blobResult.snapshot);
        }
      });
    }
  });
};

var arguments = process.argv;

if (arguments.length > 3) {
  console.log('Incorrect number of arguments');
}
else if (arguments.length == 3) {
  // Adding a third argument on the command line, whatever it is, will delete the container before running the sample.
  blobClient.deleteContainer(container, function (error) {
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