# Change Log azure-storage-file

## Version 12.0.0b1:

For release notes and more information please visit
https://aka.ms/azure-sdk-preview1-python

## Version 2.0.1:
- Updated dependency on azure-storage-common.

## Version 2.0.0:
- Support for 2018-11-09 REST version. Please see our REST API documentation and blogs for information about the related added features.
- Added an option to get share stats in bytes.
- Added support for listing and closing file handles.

## Version 1.4.0:

- azure-storage-nspkg is not installed anymore on Python 3 (PEP420-based namespace package)

## Version 1.3.1:

- Fixed design flaw where get_file_to_* methods buffer entire file when max_connections is set to 1.

## Version 1.3.0:

- Support for 2018-03-28 REST version. Please see our REST API documentation and blog for information about the related added features.

## Version 1.2.0rc1:

- Support for 2017-11-09 REST version. Please see our REST API documentation and blog for information about the related added features.

## Version 1.1.0:

- Support for 2017-07-29 REST version. Please see our REST API documentation and blogs for information about the related added features.
- Error message now contains the ErrorCode from the x-ms-error-code header value.

## Version 1.0.0:

- The package has switched from Apache 2.0 to the MIT license.
- Fixed bug where get_file_to_* cannot get a single byte when start_range and end_range are both equal to 0.
- Metadata keys are now case-preserving when fetched from the service. Previously they were made lower-case by the library.