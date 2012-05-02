var map;
var socket;

var newPushpin;

var currentPushpin;
var currentPushpinInfobox;

var pushpins = [];

function initialize() {
  initializeMaps();
  initializeSockets();
  initializeInputs();
}

function initializeMaps() {
  map = new Microsoft.Maps.Map(document.getElementById('map'), {
    credentials: bingMapsCredentials,
    center: new Microsoft.Maps.Location(47.6, -122.2),
    zoom: 8
  });

  Microsoft.Maps.Events.addHandler(map, 'click', openPushpinDialog);

  if (initialPushpins) {
    addPushpins(initialPushpins);
  }
}

function initializeSockets() {
  socket = io.connect();

  socket.on('addPushpin', function (pushpin) {
    addPushpin(pushpin);
  });

  socket.on('removePushpin', function(entity) {
    removePushpin(entity);
  });

  socket.on('clearPushpins', function () {
    clearPushpins();
  });
}

function initializeInputs() {
  $('#clearButton').click(emitClearPushpins);
}

function addPushpins(pushpinList) {
  for (var pushpin in pushpinList) {
    var currentPushpin = pushpinList[pushpin];
    addPushpin(currentPushpin);
  }
}

function addPushpin(pushpin) {
  var previousPushpin = findPushpinData(pushpin.latitude, pushpin.longitude);
  if (!previousPushpin) {
    var mapPushpin = new Microsoft.Maps.Pushpin(pushpin, null);
    attachInfobox(mapPushpin);
    map.entities.push(mapPushpin);
    pushpins.push(pushpin);
  }
}

function openPushpinDialog(event) {
  if (event.targetType === 'map') {
    if (currentPushpinInfobox) {
      if (currentPushpin) {
        currentPushpin = null;
      }

      map.entities.remove(currentPushpinInfobox);
      currentPushpinInfobox = null;
    } else {
      if (newPushpin) {
        map.entities.remove(newPushpin);
        newPushpin = null;
      }

      if (currentPushpin) {
        currentPushpin = null;
      }

      if (currentPushpinInfobox) {
        map.entities.remove(currentPushpinInfobox);
        currentPushpinInfobox = null;
      }

      // Set location into the dialog form
      var point = new Microsoft.Maps.Point(event.getX(), event.getY());
      var location = event.target.tryPixelToLocation(point);

      $("#title").val('');
      $("#description").val('');
      $("#latitude").val(location.latitude);
      $("#longitude").val(location.longitude);

      // Add pushpin
      newPushpin = new Microsoft.Maps.Pushpin(location, null);
      map.entities.push(newPushpin);

      // Open dialog to add the pushpin
      $("#map-dialog").dialog({
        autoOpen: true,
        modal: true,
        width: 500,
        height: 350,
        resizable: true,
        buttons: {
          Save: savePushpin,
          Cancel: cancelPushpin
        },
        close: closePushpin
      });
    }
  }
}

function savePushpin() {
  $('#addPushpinForm').submit();
}

function cancelPushpin() {
  map.entities.remove(newPushpin);
  $(this).dialog("close");
}

function closePushpin() {
  map.entities.remove(newPushpin);
}

function clearPushpins() {
  map.entities.clear();
  pushpins = [];
  newPushpin = null;
  currentPushpin = null;
  currentPushpinInfobox = null;
}

function emitRemovePushpin() {
  socket.emit('removePushpin', currentPushpin);
}

function emitClearPushpins() {
  socket.emit('clearPushpins');
}

function removePushpin(pushpinData) {
  var pushpinEntry = findPushpinData(pushpinData.latitude, pushpinData.longitude);
  if (pushpinEntry) {
    removeByElement(pushpins, pushpinEntry);

    var pushpin = findPushpin(pushpinData.latitude, pushpinData.longitude);
    if (pushpin) {
      map.entities.remove(pushpin);
    }

    if (currentPushpinInfobox) {
      map.entities.remove(currentPushpinInfobox);
      currentPushpinInfobox = null;
    }
  }
}

function attachInfobox(pushpin) {
  Microsoft.Maps.Events.addHandler(pushpin, 'click', showPushpinInfo);
}

function showPushpinInfo(event) {
  if (event.targetType == "pushpin") {
    var pushpin = event.target;
    currentPushpin = findPushpinData(pushpin.getLocation().latitude, pushpin.getLocation().longitude);
    if (currentPushpin) {
      if (currentPushpinInfobox) {
        map.entities.remove(currentPushpinInfobox);
        currentPushpinInfobox = null;
      }

      var infoboxOptions = {
        title: currentPushpin.title,
        description: currentPushpin.description,
        width: 250,
        height: 300,
        offset: new Microsoft.Maps.Point(0, 40),
        actions: [{ label: 'Remove', eventHandler: emitRemovePushpin }]
      };

      infoboxOptions.description = '<p>' + currentPushpin.description + '</p>';

      if (currentPushpin.imageUrl) {
        infoboxOptions.description += '<img src="' + currentPushpin.imageUrl + '" width="100%" />';
      } else {
        infoboxOptions.description += '<p>No image.</p>';
      }

      currentPushpinInfobox = new Microsoft.Maps.Infobox(pushpin.getLocation(), infoboxOptions);
      map.entities.push(currentPushpinInfobox);
    }
  }
}

function findPushpinData(latitude, longitude) {
  for (var i = 0; i < pushpins.length; i++) {
    if (latitude  == pushpins[i].latitude &&
        longitude == pushpins[i].longitude) {
      return pushpins[i];
    }
  }

  return null;
}

function findPushpin(latitude, longitude) {
  for (var i = 0; i < map.entities.getLength(); i++) {
    if (latitude  == map.entities.get(i).getLocation().latitude &&
        longitude == map.entities.get(i).getLocation().longitude) {
      return map.entities.get(i);
    }
  }

  return null;
}

function removeByElement(arrayName, arrayElement) {
  for (var i = 0; i < arrayName.length; i++) {
    if (arrayName[i] === arrayElement) {
      arrayName.splice(i, 1);
    }
  }
}