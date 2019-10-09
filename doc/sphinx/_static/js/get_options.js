WINDOW_CONTENTS = window.location.href.split('/')
function currentVersion(){
    if (WINDOW_CONTENTS.includes('$web') && WINDOW_CONTENTS.length > 5)
    {
      return WINDOW_CONTENTS[6];
    }
    else {
      $('#versionSelector').hide();

      return ''
    }
}

function currentPackage(){
    if (WINDOW_CONTENTS.includes('$web') && WINDOW_CONTENTS.length > 5)
    {
      return WINDOW_CONTENTS[5];
    }
    else {
      $('#versionSelector').hide();

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

function populateOptions(){
    var versionRequestUrl = "https://azuresdkdocsdev.blob.core.windows.net/$web?restype=container&comp=list&prefix=python/" + currentPackage() + "/versions/"
    httpGetAsync(versionRequestUrl, populationCallback)
}

function populationCallback(response){
    if(response){
      data_stored = response

      parser = new DOMParser();
      xmlDoc = parser.parseFromString(response,"text/xml");
      
      nameElements = Array.from(xmlDoc.getElementsByTagName('Name'))
      options = []

      for (var i in nameElements){
        options.push(nameElements[i].textContent.split('/')[3])
      }

      console.log(options)

      populateVersionDropDown('#versionSelector', options)

      $('#versionSelector').change(function(){
        targetVersion = $(this).val()

        console.log(targetVersion)

        url = WINDOW_CONTENTS.slice()
        url[6] = targetVersion
        window.location.href = url.join('/')
      });
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

function populateIndexList(selector, packageName)
{
  console.log(selector)
  console.log(packageName)
}
