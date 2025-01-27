# Release History

## 0.20.8 (2024-10-31)

### Other Changes

- This package has been deprecated and will no longer be maintained after 10-31-2024. This package will only receive security fixes until 10-31-2024. To receive updates on new features and non-security bug fixes, upgrade to the specific service management package listed [here](https://azure.github.io/azure-sdk/releases/latest/all/python.html).

## 0.20.7 (2020-05-05)

- Python 3.7 compatibility

## 0.20.6 (2017-04-27)

This wheel package is now built with the azure wheel extension

## 0.20.5 (2016-09-22)

**Bugfix**

* #794 `show_in_gui` not correctly sent to the server
* #793 `recommended_vm_size` is not populated

Thank you to colemickens for his contribution

## 0.20.4 (2016-08-01)

**Bugfix**

* Incomplete parsing if XML contains namespace #257 #707

**New**

* Associate/Dissociate Reserved IP #695 #716

Thank you to brandondahler, schaefi for their contributions.

## 0.20.3 (2016-03-31)

**New**

* #519 Add support for the OSImage /details endpoint

Thank you to bear454 for his contribution.

## 0.20.2 (2016-01-20)

**New**

* #487 #488 Add StaticVirtualNetworkIPAddress to network configuration
* #497      Add replicate_vm_image, unreplicate_vm_image, share_vm_image
* #501 #511 Add update_os_image_from_image_reference

Thank you to bear454, ekesken, schaefi for their contributions.

## 0.20.1 (2015-09-14)

**News**

* Create a requests.Session() if the user doesn't pass one in.

## 0.20.0 (2015-08-31)

Initial release of this package, from the split of the `azure` package.
See the `azure` package release note for 1.0.0 for details and previous
history on service bus.