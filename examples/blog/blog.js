var path = require('path');
if (path.existsSync('./../../lib/azure.js')) {
  azure = require('./../../lib/azure');
} else {
  azure = require('azure');
}

var ServiceClient = azure.ServiceClient;
var TableQuery = azure.TableQuery;
var uuid = require('node-uuid');

var tableName = 'posts';
var partition = 'part1';

Blog = function () {
  this.tableClient = azure.createTableService(ServiceClient.DEVSTORE_STORAGE_ACCOUNT, ServiceClient.DEVSTORE_STORAGE_ACCESS_KEY, ServiceClient.DEVSTORE_TABLE_HOST);
};

Blog.prototype.findAll = function (callback) {
  var tableQuery = TableQuery.select()
    .from(tableName);

  this.tableClient.queryEntities(tableQuery, callback);
};

Blog.prototype.findById = function (id, callback) {
  this.tableClient.queryEntity(tableName, partition, id, callback);
};

Blog.prototype.destroy = function (id, callback) {
  var entity = { PartitionKey: partition, RowKey: id };
  this.tableClient.deleteEntity(tableName, entity, callback);
};

Blog.prototype.save = function (posts, callback) {
  if (!Array.isArray(posts)) {
    posts = [posts];
  }

  this.savePosts(posts, callback);
};

// this could be implemented using batch but for the sake of using both methods use the individual requests + callback.
Blog.prototype.savePosts = function (posts, callback) {
  if (posts.length === 0) {
    callback();
  }
  else {
    var post = posts.pop();
    post.created_at = new Date();

    if (post.comments === undefined)
      post.comments = [];

    for (var j = 0; j < post.comments.length; j++) {
      post.comments[j].created_at = new Date();
    }

    post.PartitionKey = partition;
    post.RowKey = uuid();

    var provider = this;
    this.tableClient.insertEntity(tableName, post, function () {
      // Insert remaining posts recursively
      provider.savePosts(posts, callback);
    });
  }
};

Blog.prototype.init = function () {
  var provider = this;
  this.tableClient.createTableIfNotExists(tableName, function (err, created) {
    if (created) {
      console.log('Setting up demo data ...');

      provider.tableClient.beginBatch();

      var now = new Date().toString();
      provider.tableClient.insertEntity(tableName, { PartitionKey: partition, RowKey: uuid(), title: 'Post one', body: 'Body one', created_at: now });
      provider.tableClient.insertEntity(tableName, { PartitionKey: partition, RowKey: uuid(), title: 'Post two', body: 'Body two', created_at: now });
      provider.tableClient.insertEntity(tableName, { PartitionKey: partition, RowKey: uuid(), title: 'Post three', body: 'Body three', created_at: now });
      provider.tableClient.insertEntity(tableName, { PartitionKey: partition, RowKey: uuid(), title: 'Post four', body: 'Body four', created_at: now });

      provider.tableClient.commitBatch(function () {
        console.log('Done');
      });
    }
  });
};

exports.Blog = Blog;
