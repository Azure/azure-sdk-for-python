var azure = require('azure');
var uuid = require('node-uuid');

var ServiceClient = azure.ServiceClient;

// Table service 'constants'
var TABLE_NAME = 'pushpins';
var DEFAULT_PARTITION = 'pushpins';

// Blob service 'constants'
var CONTAINER_NAME = 'pushpins';

// Expose 'PushpinService'.
exports = module.exports = PushpinService;

function PushpinService(storageAccount, storageAccessKey) {
  this.tableClient = azure.createTableService(storageAccount, storageAccessKey);
  this.blobClient = azure.createBlobService(storageAccount, storageAccessKey);
}

PushpinService.prototype.initialize = function (callback) {
  var self = this;

  var createContainer = function () {
    // create blob container if it doesnt exist
    self.blobClient.createContainerIfNotExists(CONTAINER_NAME, function (createContainerError, created) {
      if (createContainerError) {
        callback(createContainerError);
      } else if (created) {
        self.blobClient.setContainerAcl(CONTAINER_NAME,
          azure.Constants.BlobConstants.BlobContainerPublicAccessType.BLOB,
          callback);
      } else {
        callback();
      }
    });
  };

  // create table if it doesnt exist
  self.tableClient.createTableIfNotExists(TABLE_NAME, function (createTableError) {
    if (createTableError) {
      callback(createTableError);
    } else {
      createContainer();
    }
  });
};

PushpinService.prototype.createPushpin = function (pushpinData, pushpinImage, callback) {
  var self = this;
  var rowKey = 'row' + uuid();

  function insertEntity(error, blob) {
    var entity = pushpinData;
    entity.RowKey = rowKey;
    entity.PartitionKey = DEFAULT_PARTITION;

    if (blob) {
      entity.imageUrl = self.blobClient.getBlobUrl(blob.container, blob.blob).url();
    }

    self.tableClient.insertEntity(TABLE_NAME, entity, callback);
  };

  if (pushpinImage) {
    self.blobClient.createBlockBlobFromFile(CONTAINER_NAME, rowKey, pushpinImage.path, insertEntity);
  } else {
    insertEntity();
  }
};

PushpinService.prototype.listPushpins = function (callback) {
  var self = this;
  var tableQuery = azure.TableQuery
    .select()
    .from(TABLE_NAME);

  self.tableClient.queryEntities(tableQuery, callback);
};

PushpinService.prototype.removePushpin = function (pushpin, callback) {
  var self = this;
  var tableQuery = azure.TableQuery
    .select()
    .from(TABLE_NAME)
    .where('latitude == ? && longitude == ?', pushpin.latitude, pushpin.longitude);

  self.tableClient.queryEntities(tableQuery, function (error, pushpins) {
    if (error) {
      callback(error);
    } else if (pushpins && pushpins.length > 0) {
      self.tableClient.deleteEntity(TABLE_NAME, pushpins[0], callback);
    } else {
      callback();
    }
  });
};

PushpinService.prototype.clearPushpins = function (callback) {
  var self = this;
  var deleteEntities = function (entities) {
    if (entities && entities.length > 0) {
      var currentEntity = entities.pop();
      self.tableClient.deleteEntity(TABLE_NAME, currentEntity, function (deleteError) {
        if (deleteError) {
          callback(error);
        } else if (currentEntity.imageUrl) {
          self.blobClient.deleteBlob(CONTAINER_NAME, currentEntity.RowKey, function (deleteBlobError) {
            if (deleteBlobError) {
              callback(deleteBlobError);
            } else {
              deleteEntities(entities);
            }
          });
        } else {
          deleteEntities(entities);
        }
      });
    } else {
      callback();
    }
  };

  exports.listPushpins(function (error, entities) {
    if (error) {
      callback(error);
    } else {
      deleteEntities(entities);
    }
  });
};