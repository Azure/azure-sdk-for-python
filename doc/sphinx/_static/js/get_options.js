WINDOW_CONTENTS = window.location.href.split('/')
SPLIT_REGEX = /([a-zA-Z]+)|([0-9]+)/g;
REPLACE_REGEX = /[^a-zA-Z0-9]*/g

// this function compares the individual version specifiers of two different versions.
// If were comparing versions 1.0.0rc1 vs 1.1.2. This function compares
// 1 compared to 1
// 0 compared to 1
// 0rc1 vs 2
// the key here is that it removes all non alpha-numeric numbers, then splits by character TRANSITION
// Then it compares 1-1 for THOSE.
function comparePreviewSpecifer(v1, v2){
    var v1parts = v1.replace(REPLACE_REGEX, '').split(SPLIT_REGEX).filter(a => a)
    var v2parts = v2.replace(REPLACE_REGEX, '').split(SPLIT_REGEX).filter(a => a)

    if (v2parts.length === 0) {
        return 1;
    }

    for (var i = 0; i < v1parts.length; ++i) {
        if (v1parts[i] === v2parts[i]) {
            continue;
        }

        if (v1parts[i] > v2parts[i] && v2parts[i] !== undefined) {
            return 1;
        }

        if (v1parts[i] < v2parts[i] && v2parts[i] !== undefined){
            return -1;
        }
    }

    // we have broken out due to v2parts having additional preview parts
    if (v2parts.length > v1parts.length) {
      return 1
    }

    if (v1parts.length > v2parts.length) {
      return -1
    }

    return 0;
}

function compareVersionNumbers(v1, v2){
    var v1parts = v1.toLowerCase().split('.');
    var v2parts = v2.toLowerCase().split('.');

    // classic versions of this algorithm error if we all the values aren't entirely valid versions
    // given that we will have preview versions here, compare lexically when we hit that part.
    if (v2parts.length === 0) {
        return 1;
    }

    if (v1parts.length != v2parts.length) {
        return -1;
    }

    for (var i = 0; i < v1parts.length; ++i) {
        if (v1parts[i] === v2parts[i]) {
            continue;
        }

        return comparePreviewSpecifer(v1parts[i], v2parts[i])
    }

    return 0;
}

function currentVersion(){
    if (WINDOW_CONTENTS.includes('$web') && WINDOW_CONTENTS.length > 5)
    {
      return WINDOW_CONTENTS[6];
    }
    else {
      return ''
    }
}

function currentPackage(){
    if (WINDOW_CONTENTS.includes('$web') && WINDOW_CONTENTS.length > 5)
    {
      return WINDOW_CONTENTS[5];
    }
    else {
      return ''
    }
}

function httpGetAsync(targetUrl, callback)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
          callback(xmlHttp.responseText);
    }
    xmlHttp.open("GET", targetUrl, true); // true for asynchronous 
    xmlHttp.send(null);
}

function showSelectors(selectors){
  selectors.forEach(function(item, index){
    $(item).show()
  })
}

function hideSelectors(selectors){
  selectors.forEach(function(item, index){
    $(item).hide()
  })
}

function processResponse(responseText){
  parser = new DOMParser();
  xmlDoc = parser.parseFromString(responseText,"text/xml");
  
  nameElements = Array.from(xmlDoc.getElementsByTagName('Name'))
  options = []

  for (var i in nameElements){
    options.push(nameElements[i].textContent.split('/')[3])
  }

  var result = options.sort(compareVersionNumbers).reverse()

  return result
}

function populateOptions(optionSelector, otherSelectors){
  if(currentPackage()){
    var versionRequestUrl = "https://azuresdkdocs.blob.core.windows.net/$web?restype=container&comp=list&prefix=" + SELECTED_LANGUAGE + "/" + currentPackage() + "/versions/"
    
    httpGetAsync(versionRequestUrl, function(responseText){
      if(responseText){
        options = processResponse(responseText)

        populateVersionDropDown(optionSelector, options)
        showSelectors(otherSelectors)

        $(optionSelector).change(function(){
          targetVersion = $(this).val()

          url = WINDOW_CONTENTS.slice()
          url[6] = targetVersion
          window.location.href = url.join('/')
        });
      }
    })
  }
}

function populateVersionDropDown(selector, values){
    var select = $(selector);

    $('option', select).remove();

    $.each(values, function(index, text) {
      $('<option/>', { 'value' : text, 'text': text }).appendTo(select);
    });
    select.val(currentVersion());  
}

function getPackageUrl(language, package, version){
  return "https://azuresdkdocs.blob.core.windows.net/$web/" + language + "/" + package + "/"+ version + "/index.html"
}

function populateIndexList(selector, packageName)
{
  url = "https://azuresdkdocs.blob.core.windows.net/$web?restype=container&comp=list&prefix=" + SELECTED_LANGUAGE + "/" + packageName + "/versions/"

  httpGetAsync(url, function (responseText){
    if(responseText){
      options = processResponse(responseText)

      for (var i in options){
        $(selector).append('<li><a target="new" href="' + getPackageUrl(SELECTED_LANGUAGE, packageName, options[i]) + '">' + options[i] + '</a></li>')
      }
    }
    else {
      $(selector).append('<li>No discovered versions present in blob storage.</li>')
    }
  })
}

// language specific
SELECTED_LANGUAGE = 'python'
populateOptions('#versionSelector', ['#versionSelector', '#versionSelectorHeader'])