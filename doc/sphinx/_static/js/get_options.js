WINDOW_CONTENTS = window.location.href.split('/')

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

function populateOptions(optionSelector, otherSelectors){
  if(currentPackage()){
    var versionRequestUrl = "https://azuresdkdocs.blob.core.windows.net/$web?restype=container&comp=list&prefix=" + SELECTED_LANGUAGE + "/" + currentPackage() + "/versions/"
    
    httpGetAsync(versionRequestUrl, function(responseText){
      if(responseText){
        data_stored = responseText

        parser = new DOMParser();
        xmlDoc = parser.parseFromString(responseText,"text/xml");
        
        nameElements = Array.from(xmlDoc.getElementsByTagName('Name'))
        options = []

        for (var i in nameElements){
          options.push(nameElements[i].textContent.split('/')[3])
        }

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
      parser = new DOMParser();
      xmlDoc = parser.parseFromString(responseText,"text/xml");

      nameElements = Array.from(xmlDoc.getElementsByTagName('Name'))
      options = []

      for (var i in nameElements){
        options.push(nameElements[i].textContent.split('/')[3])
      }

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