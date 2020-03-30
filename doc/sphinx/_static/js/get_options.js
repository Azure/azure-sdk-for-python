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
    var versionRequestUrl = "https://azuresdkdocs.blob.core.windows.net/$web/" + SELECTED_LANGUAGE + "/" + currentPackage() + "/versioning/versions"
    
    httpGetAsync(versionRequestUrl, function(responseText){
      if(responseText){
        options = responseText.match(/[^\r\n]+/g)

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
    var select = $(selector)
    
    $('option', select).remove()

    $.each(values, function(index, text) {
      $('<option/>', { 'value' : text, 'text': text }).appendTo(select)
    });

    var version = currentVersion()
    if(version==='latest'){
      select.selectedIndex = 0
    }
    else {
      select.val(version)  
    }
}

function getPackageUrl(language, package, version){
  return "https://azuresdkdocs.blob.core.windows.net/$web/" + language + "/" + package + "/"+ version + "/index.html"
}

function populateIndexList(selector, packageName)
{
  url = "https://azuresdkdocs.blob.core.windows.net/$web/" + SELECTED_LANGUAGE + "/" + packageName + "/versioning/versions"

  httpGetAsync(url, function (responseText){
    if(responseText){
      options = responseText.match(/[^\r\n]+/g)

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