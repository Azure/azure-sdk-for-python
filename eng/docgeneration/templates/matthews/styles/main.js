// Use container fluid
var containers = $(".container");
containers.removeClass("container");
containers.addClass("container-fluid");

var SELECTED_LANGUAGE = 'python'

// Navbar Hamburger
$(function () {
    $(".navbar-toggle").click(function () {
        $(this).toggleClass("change");
    })
})

// Select list to replace affix on small screens
$(function () {
    var navItems = $(".sideaffix .level1 > li");

    if (navItems.length == 0) {
        return;
    }

    var selector = $("<select/>");
    selector.addClass("form-control visible-sm visible-xs");
    var form = $("<form/>");
    form.append(selector);
    form.prependTo("article");

    selector.change(function () {
        window.location = $(this).find("option:selected").val();
    })

    function work(item, level) {
        var link = item.children('a');

        var text = link.text();

        for (var i = 0; i < level; ++i) {
            text = '&nbsp;&nbsp;' + text;
        }

        selector.append($('<option/>', {
            'value': link.attr('href'),
            'html': text
        }));

        var nested = item.children('ul');

        if (nested.length > 0) {
            nested.children('li').each(function () {
                work($(this), level + 1);
            });
        }
    }

    navItems.each(function () {
        work($(this), 0);
    });
})

// Inject line breaks and spaces into the code sections
$(function () {
    $(".lang-csharp").each(function () {
        var text = $(this).html();
        text = text.replace(/, /g, ",</br>&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;");
        $(this).html(text);
    });
})

function httpGetAsync(targetUrl, callback) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    }
    xmlHttp.open("GET", targetUrl, true); // true for asynchronous 
    xmlHttp.send(null);
}

function httpGetLatestAsync(targetUrl, latestVersions, packageName) {
    httpGetAsync(targetUrl, function (responseText) {
      if (responseText) {
        version = responseText.match(/[^\r\n]+/g)
        $(latestVersions).append('<li><a href="' + getPackageUrl(SELECTED_LANGUAGE, packageName, version) + '" target="_blank">' + version + '</a></li>')
      }
    })
}
  
function populateIndexList(selector, packageName) {
    var url = "https://azuresdkdocs.blob.core.windows.net/$web/" + SELECTED_LANGUAGE + "/" + packageName + "/versioning/versions"
    var latestGAUrl = "https://azuresdkdocs.blob.core.windows.net/$web/" + SELECTED_LANGUAGE + "/" + packageName + "/versioning/latest-ga"
    var latestPreviewUrl = "https://azuresdkdocs.blob.core.windows.net/$web/" + SELECTED_LANGUAGE + "/" + packageName + "/versioning/latest-preview"
    var latestVersions = document.createElement("ul")
    httpGetLatestAsync(latestGAUrl, latestVersions, packageName)
    httpGetLatestAsync(latestPreviewUrl, latestVersions, packageName)
    var publishedVersions = $('<ul style="display: none;"></ul>')
    var collapsible = $('<div class="versionarrow">&nbsp;&nbsp;&nbsp;Other versions</div>')
  
    $(selector).after(latestVersions)
    $(latestVersions).after(collapsible)
    $(collapsible).after(publishedVersions)
  
    // Add collapsible arrow on other versions.
    $(collapsible).on('click', function (event) {
      event.preventDefault();
      if (collapsible.hasClass('disable')) {
        return
      }
      $(this).toggleClass('down')
      if ($(this).hasClass('down')) {
        if (!$(selector).hasClass('loaded')) {
          httpGetAsync(url, function (responseText) {
            if (responseText) {
              options = responseText.match(/[^\r\n]+/g)
              for (var i in options) {
                $(publishedVersions).append('<li><a href="' + getPackageUrl(SELECTED_LANGUAGE, packageName, options[i]) + '" target="_blank">' + options[i] + '</a></li>')
  
              }
            }
            else {
              $(publishedVersions).append('<li>No discovered versions present in blob storage.</li>')
            }
            $(selector).addClass("loaded")
          })
        }
        $(publishedVersions).show()
      } else {
        $(publishedVersions).hide()
      }
    });
}
  
function getPackageUrl(language, package, version) {
    return "https://azuresdkdocs.blob.core.windows.net/$web/" + language + "/" + package + "/" + version + "/index.html"
}

// Populate Index
$(function () {
    $('h4').each(function () {
        var pkgName = $(this).text()
        populateIndexList($(this), pkgName)
    });
})