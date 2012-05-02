var path = require('path');
if (path.existsSync('./../../lib/azure.js')) {
  azure = require('./../../lib/azure');
} else {
  azure = require('azure');
}

var TableQuery = azure.TableQuery;

module.exports = Home;
var uuid = require('node-uuid');

function Home(client) {
  this.client = client;
};

Home.prototype = {
  showResults: function (res, taskList) {
    res.render('home', {
      locals: {
        title: 'Task list',
        layout: false,
        taskList: taskList
      }
    });
  },

  getItems: function (allItems, callback) {
    var query = TableQuery.select().from('tasks');
    if (!allItems) {
      query = query.where('completed eq ?', false);
    }

    this.client.queryEntities(query, callback);
  },

  showItems: function (req, res) {
    var self = this;
    this.getItems(false, function (resp, taskList) {
      if (!taskList) {
        self.taskList = [];
      }

      self.showResults(res, taskList);
    });
  },

  newItem: function (req, res) {
    var self = this;
    var createItem = function (resp, taskList) {
      if (!taskList) {
        self.taskList = [];
      }

      var item = req.body.item;
      item.RowKey = uuid();
      item.PartitionKey = 'partition1';
      item.completed = false;

      self.client.insertEntity('tasks', item, function () {
        self.showItems(req, res);
      });
    };

    this.getItems(true, createItem);
  },

  markCompleted: function (req, res) {
    var self = this;

    var postedItems = req.body.completed;
    if (!postedItems.forEach)
      postedItems = [postedItems];

    var process = {
      processNextItem: function (err) {
        var item = postedItems.pop();
        if (item) process.getItemToUpdate(item);
        else self.getItems(false, function (resp, taskitems) {
          self.showResults(res, taskitems);
        });
      },
      getItemToUpdate: function (item) {
        self.client.queryEntity('tasks', 'partition1', item, process.updateItem);
      },
      updateItem: function (resp, task) {
        if (task) {
          task.completed = true;
          self.client.updateEntity('tasks', task, process.processNextItem);
        }
      }
    };

    process.processNextItem();
  }
};