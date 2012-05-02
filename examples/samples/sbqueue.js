var path = require('path');
if (path.existsSync('./../../lib/azure.js')) {
  azure = require('./../../lib/azure');
} else {
  azure = require('azure');
}

var util = require('util');

var queue = 'queuesample';

var serviceBusClient = azure.createServiceBusService();

function createQueue() {
  // Step 0: Create queue.
  serviceBusClient.createQueue(queue, function (error) {
    if (error) {
      console.log(error);
    } else {
      console.log('Created the queue ' + queue);
      sendMessages();
    }
  });
}

function sendMessages() {
  // Step 1: Send a few messages to later be consumed.
  serviceBusClient.sendQueueMessage(queue, 'Send Message Works', function(error1) {
    if (error1) {
      console.log(error1);
    } else {
      console.log('Sent first Message');
      serviceBusClient.sendQueueMessage(queue, 'Send Message Still Works', function(error2) {
        if (error2) {
          console.log(error2);
        } else {
          console.log('Sent Second Message');
          receiveMessages();
        }
      });
    }
  });
}

function receiveMessages() {
  // Step 2: Receive the messages.
  serviceBusClient.receiveQueueMessage(queue, function (error1, message1) {
    if (error1) {
      console.log(error1);
    } else {
      console.log(message1.body);
      serviceBusClient.receiveQueueMessage(queue, function (error2, message2) {
        if (error2) {
          console.log(error2);
        } else {
          console.log(message2.body);
        }
      });
    }
  });
}

var arguments = process.argv;

if (arguments.length > 3) {
  console.log('Incorrect number of arguments');
}
else if (arguments.length == 3) {
  // Adding a third argument on the command line, whatever it is, will delete the container before running the sample.
  serviceBusClient.deleteQueue(queue, function (error) {
    if (error) {
      console.log(error);
    } else {
      createQueue();
    }
  });
}
else {
  createQueue();
}