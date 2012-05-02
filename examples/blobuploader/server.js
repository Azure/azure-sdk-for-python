var path = require('path');
if (path.existsSync('./../../lib/azure.js')) {
  azure = require('./../../lib/azure');
} else {
  azure = require('azure');
}

var express = require('express');
var formidable = require('formidable');
var helpers = require('./helpers.js');

var app = module.exports = express.createServer();
// Global request options, set the retryPolicy
var blobClient = azure.createBlobService(azure.ServiceClient.DEVSTORE_STORAGE_ACCOUNT, azure.ServiceClient.DEVSTORE_STORAGE_ACCESS_KEY, azure.ServiceClient.DEVSTORE_BLOB_HOST).withFilter(new azure.ExponentialRetryPolicyFilter());
var containerName = 'webpi';

//Configuration
app.configure(function () {
  app.set('views', __dirname + '/views');
  app.set('view engine', 'ejs');
  app.use(express.methodOverride());
  // app.use(express.logger());
  app.use(app.router);
  app.use(express.static(__dirname + '/public'));
});

app.configure('development', function () {
  app.use(express.errorHandler({ dumpExceptions: true, showStack: true }));
});

app.configure('production', function () {
  app.use(express.errorHandler());
});

app.param(':id', function (req, res, next) {
  next();
});

//Routes
app.get('/', function (req, res) {
  res.render('index.ejs', { locals: {
    title: 'Welcome'
  }
  });
});

app.get('/Upload', function (req, res) {
  res.render('upload.ejs', { locals: {
    title: 'Upload File'
  }
  });
});

app.get('/Display', function (req, res) {
  blobClient.listBlobs(containerName, function (error, blobs) {
    res.render('display.ejs', { locals: {
      title: 'List of Blobs',
      serverBlobs: blobs
    }
    });
  });
});

app.get('/Download/:id', function (req, res) {
  blobClient.getBlobProperties(containerName, req.params.id, function (err, blobInfo) {
    if (err === null) {
      res.header('content-type', blobInfo.contentType);
      res.header('content-disposition', 'attachment; filename=' + blobInfo.metadata.filename);
      blobClient.getBlobToStream(containerName, req.params.id, res, function () { });
    } else {
      helpers.renderError(res);
    }
  });
});

app.post('/uploadhandler', function (req, res) {
  var form = new formidable.IncomingForm();

  form.parse(req, function (err, fields, files) {
    var formValid = true;
    if (fields.itemName === '') {
      helpers.renderError(res);
      formValid = false;
    }

    if (formValid) {
      var extension = files.uploadedFile.name.split('.').pop();
      var newName = fields.itemName + '.' + extension;

      var options = {
        contentType: files.uploadedFile.type,
        metadata: { fileName: newName }
      };

      blobClient.createBlockBlobFromFile(containerName, fields.itemName, files.uploadedFile.path, options, function (error) {
        if (error != null) {
          helpers.renderError(res);
        } else {
          res.redirect('/Display');
        }
      });
    } else {
      helpers.renderError(res);
    }
  });
});

app.post('/Delete/:id', function (req, res) {
  blobClient.deleteBlob(containerName, req.params.id, function (error) {
    if (error != null) {
      helpers.renderError(res);
    } else {
      res.redirect('/Display');
    }
  });
});

blobClient.createContainerIfNotExists(containerName, function (error) {
  if (error) {
    console.log(error);
  } else {
    setPermissions();
  }
});

function setPermissions() {
  blobClient.setContainerAcl(containerName, azure.Constants.BlobConstants.BlobContainerPublicAccessType.BLOB, function (error) {
    if (error) {
      console.log(error);
    } else {
      app.listen(process.env.port || 1337);
      console.log("Express server listening on port %d in %s mode", app.address().port, app.settings.env);
    }
  });
}