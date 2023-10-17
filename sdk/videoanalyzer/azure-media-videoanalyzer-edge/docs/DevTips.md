## How to update the lva sdk

1. Clone the latest swagger onto your local machine
2. Replace the `require` field inside of `autorest.md` to point to your local swagger file
3. Generate the sdk using the autorest command which can be found inside the `autorest.md` file
4. Add any customization functions inside of `sdk\media\azure-media-lva-edge\azure\media\lva\edge\__init__.py`. Make sure the customization functions are outside of the `_generated` folder.
5. Update the README file and Changelog with the latest version number
6. Submit a PR

## Running tox locally

Tox is the testing and virtual environment management tool that is used to verify our sdk will be installed correctly with different Python versions and interpreters. To run tox follow these instructions

Please see the repo's [contributing guide](https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md#building-and-testing) for instructions
on how to install and run `tox`.

### Troubleshooting tox errors

- Tox will complain if there are no tests. Add an empty test in case you need to bypass this
- Make sure there is an `__init__.py` file inside of every directory inside of `azure` (Example: `azure/media` should have an __init__.py file)
- Follow the ReadMe guidelines outlined here: https://review.docs.microsoft.com/help/contribute-ref/contribute-ref-how-to-document-sdk?branch=master#readme. ReadMe titles are case SENSITIVE and use sentence casing.
- Make sure MANIFEST.in includes all required folders. (Most likely the required folders will be tests, samples, and the generated folder) 
