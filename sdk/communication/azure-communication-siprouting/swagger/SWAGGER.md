# API-NAME
> see https://aka.ms/autorest

This is the AutoRest configuration file for the API-NAME.

---
## Getting Started
To build the SDK for API-NAME, simply Install AutoRest and in this folder, run:

> `autorest`

To see additional help and options, run:

> `autorest --help`
---

## Configuration for generating APIs

...insert-some-meanigful-notes-here...

---
#### Basic Information
These are the global settings for the API.

``` yaml
input-file: swagger.json
tag: package-sip-2021-05-01
output-folder: ../azure/communication/siprouting/_generated
namespace: azure.communication.siprouting
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
clear-output-folder: true
python: true
v3: true
no-async: false
add-credential: false
title: Azure Communication SIP Routing Service
disable-async-iterators: true
```