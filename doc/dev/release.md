# Release process

### Disclaimer
This article assumes you have code on `master` that is ready to publish:
- Version is accurate
- ChangeLog is updated
- Readme is accurate, etc.

If you don't, and you are working with Management packages, start with this page:
https://github.com/Azure/azure-sdk-for-python/wiki/Preparing-a-management-package-for-release


## Python Package Index

Python packages are uploaded to [PyPI](https://pypi.org/). Once you've uploaded to PyPI, there's no way to overwrite the package. In case of problems, you'll need to increment the version number. Be sure that before going forward your package has passed all the necessary testing.

### Production - Deploy with Azure Dev Ops

Go to this Url: https://aka.ms/pysdkrelease

- Click on "Run pipeline"
- Change "BuildTargetingString" to the name of your package. Example: azure-mgmt-compute
- Change "CandidateForRelease" value to `True` (it should be defaulted to `False`)

Et voila :). Azure Dev Ops will tests one last time the package, dependencies, and the distributions (sdist/wheel) and push to PyPI using the user [azure-sdk](https://pypi.org/user/azure-sdk/).

### Production - Deploy manually

To build a package manually:
```
python .\build_package.py azure-mgmt-myservice
```

This will a sdist and a wheel file. This requires `wheel` package installed in your environment.

If you want to manually release on a regular basis, you should create a .pypirc:
```
[pypi]
repository = https://pypi.python.org/pypi
username = <yourusername>
password = <yourpassword>
```

To upload to production:
```
twine upload dist\*.zip
twine upload dist\*.whl
```

It's recommended that you create a Github tag using the format "packagename_version". Example: `azure-mgmt-compute_2.0.0`

# IMPORTANT NOTE

If this is a new package (i.e. first release), the "microsoft" account MUST be added as owner of your package. Please contact the engineering system team to do so.