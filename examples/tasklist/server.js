// Module dependencies.
var path = require('path');
if (path.existsSync('./../../lib/azure.js')) {
  azure = require('./../../lib/azure');
} else {
  azure = require('azure');
}

var express = require('express');
var uuid = require('node-uuid');
var Home = require('./home');
var ServiceClient = azure.ServiceClient;

var app = module.exports = express.createServer();
var client = azure.createTableService(ServiceClient.DEVSTORE_STORAGE_ACCOUNT, ServiceClient.DEVSTORE_STORAGE_ACCESS_KEY, ServiceClient.DEVSTORE_TABLE_HOST);

// table creation
client.createTableIfNotExists("tasks", function (res, created) {
  if (created) {
    var item = {
      name: 'Add readonly todo list',
      category: 'Site work',
      date: '12/01/2011',
      RowKey: uuid(),
      PartitionKey: 'partition1',
      completed: false
    };

    client.insertEntity("tasks", item, null, function () {
      setupApplication();
    });
  } else {
    setupApplication();
  }
});

function setupApplication() {
  // Configuration
  app.configure(function () {
    app.set('views', __dirname + '/views');

    // NOTE: Uncomment this line and comment next one to use ejs instead of jade
    // app.set('view engine', 'ejs');

    app.set('view engine', 'jade');

    app.use(express.bodyParser());
    app.use(express.methodOverride());
    app.use(app.router);
    app.use(express.static(__dirname + '/public'));
  });

  app.configure('development', function() {
    app.use(express.errorHandler({ dumpExceptions: true, showStack: true }));
  });

  app.configure('production', function() {
    app.use(express.errorHandler());
  });

  var home = new Home(client);

  // Routes

  app.get('/', home.showItems.bind(home));
  app.get('/home', home.showItems.bind(home));
  app.post('/home/newitem', home.newItem.bind(home));
  app.post('/home/completed', home.markCompleted.bind(home));

  app.listen(process.env.PORT || 1337);
  console.log("Express server listening on port %d in %s mode", app.address().port, app.settings.env);
}