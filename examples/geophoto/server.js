/**
* Module dependencies.
*/

var express = require('express')
  , pushpinController = require('./controllers/pushpinController')
  , socketio = require('socket.io');

var app = module.exports = express.createServer();
var io;

// Configuration

app.configure(function () {
  app.set('views', __dirname + '/views');
  app.set('view engine', 'ejs');
  app.use(express.bodyParser());
  app.use(express.methodOverride());
  app.use(app.router);
  app.use(express.static(__dirname + '/public'));
});

app.configure('development', function () {
  app.use(express.errorHandler({ dumpExceptions: true, showStack: true }));
});

app.configure('production', function () {
  app.use(express.errorHandler());
});

// Routes
app.get('/', pushpinController.showPushpins);
app.get('/setup', pushpinController.setup);
app.post('/setupPOST', pushpinController.setupPOST);
app.post('/createPushpin', pushpinController.createPushpin);

app.listen(process.env.PORT || 1337);
console.log("Express server listening on port %d in %s mode", app.address().port, app.settings.env);

// Setup socket.io
io = socketio.listen(app);
pushpinController.io = io;
io.set('transports', [ 'xhr-polling' ]);
io.sockets.on('connection', pushpinController.socketConnection);