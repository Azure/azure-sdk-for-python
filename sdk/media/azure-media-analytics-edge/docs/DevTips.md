## How to update the lva sdk

1. Clone the latest swagger onto your local machine
2. Replace the `require` field inside of `autorest.md` to point to your local swagger file
3. Generate the sdk using the autorest command which can be found inside the `autorest.md` file
4. Add any customization functions inside of `sdk\media\azure-media-lva-edge\azure\media\lva\edge\__init__.py`. Make sure the customization functions are outside of the `_generated` folder.
5. Update the README file and Changelog with the latest version number
6. Submit a PR

## Running tox locally

Tox is the testing and virtual environment management tool that is used to verify our sdk will be installed correctly with different Python versions and interpreters. To run tox follow these instructions

```
pip install tox tox-monorepo
cd path/to/target/folder
tox -c eng/tox/tox.ini
```
To run a specific tox command from your directory use the following commands:
```bash
> tox -c ../../../eng/tox/tox.ini -e sphinx
> tox -c ../../../eng/tox/tox.ini -e lint
> tox -c ../../../eng/tox/tox.ini -e mypy
> tox -c ../../../eng/tox/tox.ini -e whl
> tox -c ../../../eng/tox/tox.ini -e sdist
```
A quick description of the five commands above:
* sphinx: documentation generation using the inline comments written in our code
* lint: runs pylint to make sure our code adheres to the style guidance
* mypy: runs the mypy static type checker for Python to make sure that our types are valid
* whl: creates a whl package for installing our package
* sdist: creates a zipped distribution of our files that the end user could install with pip


### Troubleshooting tox errors

- Tox will complain if there are no tests. Add a dummy test in case you need to bypass this
- Make sure there is an `__init__.py` file inside of every directory inside of `azure` (Example: `azure/media` should have an __init__.py file)
- Follow the ReadMe guidelines outlined here: https://review.docs.microsoft.com/help/contribute-ref/contribute-ref-how-to-document-sdk?branch=master#readme. ReadMe titles are case SENSITIVE and use sentence casing.
- Make sure MANIFEST.in includes all required folders. (Most likely the required folders will be tests, samples, and the generated folder) 
