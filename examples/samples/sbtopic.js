var path = require('path');
if (path.existsSync('./../../lib/azure.js')) {
  azure = require('./../../lib/azure');
} else {
  azure = require('azure');
}

var util = require('util');

var topic = 'topicsample';
var subscription1 = 'subscription1';
var subscription2 = 'subscription2';

var serviceBusClient = azure.createServiceBusService();

function createTopic() {
  // Step 0: Create topic.
  serviceBusClient.createTopic(topic, function (error) {
    if (error) {
      console.log(error);
    } else {
      console.log('Created the topic ' + topic);
      createSubscriptions();
    }
  });
}

function createSubscriptions() {
  // Step 1: Create subscriptions.
  serviceBusClient.createSubscription(topic, subscription1, function (error1) {
    if (error1) {
      console.log(error1);
    } else {
      serviceBusClient.createSubscription(topic, subscription2, function (error2) {
        if (error2) {
          console.log(error2);
        } else {
          sendMessages();
        }
      });
    }
  });
}

function sendMessages() {
  // Step 2: Send a few messages to later be consumed.
  serviceBusClient.sendTopicMessage(topic, 'Send Message Works', function(error1) {
    if (error1) {
      console.log(error1);
    } else {
      console.log('Sent first Message');
      serviceBusClient.sendTopicMessage(topic, 'Send Message Still Works', function (error2) {
        if (error2) {
          console.log(error2);
        } else {
          console.log('Sent Second Message');
          receiveMessagesSubscription1();
        }
      });
    }
  });
}

function receiveMessagesSubscription1() {
  // Step 3: Receive the messages for subscription 1.
  serviceBusClient.receiveSubscriptionMessage(topic, subscription1, function (error1, message1) {
    if (error1) {
      console.log(error1);
    } else {
      console.log(message1.body);
      serviceBusClient.receiveSubscriptionMessage(topic, subscription1, function (error2, message2) {
        if (error2) {
          console.log(error2);
        } else {
          console.log(message2.body);
          receiveMessagesSubscription2();
        }
      });
    }
  });
}

function receiveMessagesSubscription2() {
  // Step 3: Receive the messages for subscription 2.
  serviceBusClient.receiveSubscriptionMessage(topic, subscription2, function (error1, message1) {
    if (error1) {
      console.log(error1);
    } else {
      console.log(message1.body);
      serviceBusClient.receiveSubscriptionMessage(topic, subscription2, function (error2, message2) {
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
  serviceBusClient.deleteTopic(topic, function (error) {
    if (error) {
      console.log(error);
    } else {
      createTopic();
    }
  });
}
else {
  createTopic();
}