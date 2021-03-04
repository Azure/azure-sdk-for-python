# Azure SDK for Python - Engineering System

There are various tests currently enabled in Azure pipeline for Python SDK and some of them are enabled only for nightly CI checks. We also run some static analysis tool to verify code completeness, security and lint check.  

Check the [contributing guide](https://github.com/Azure/azure-sdk-for-python/blob/master/CONTRIBUTING.md#building-and-testing) for an intro to `tox`.

As a contributor, you will see the build jobs run in two modes: `Nightly Scheduled` and `Pull Request`.

These utilize the _same build definition_, except that the `nightly` builds run additional, deeper checks that run for a bit longer.

Example PR build:

![res/job_snippet.png](res/job_snippet.png)

 - `Analyze` tox envs run during the `Analyze job.
 - `Test <platform>_<pyversion>` runs PR/Nightly tox envs, depending on context.

## Analyze Checks
Analyze job in both nightly CI and pull request validation pipeline runs a set of static analysis using external and internal tools. Following are the list of these static analysis.

#### MyPy
`Mypy` is a static analysis tool that runs type checking of python package. Following are the steps to run `MyPy` locally for a specific package
1. Go to root of the package
2. Execute following command
   ```tox -e mypy -c ../../../eng/tox/tox.ini ``` 

#### Pylint
`Pylint` is a static analysis tool to run lint checking. Following are the steps to run `pylint` locally for a specific package.
 
1. Go to root of the package.
2. Execute following command
   ```tox -e pylint -c ../../../eng/tox/tox.ini```
 

#### Bandit
`Bandit` is static security analysis tool. This check is triggered for all Azure SDK package as part of analyze job. Following are the steps to `Bandit` tool locally for a specific package.

1. Got to package root directory.
2. Execute following command
   ```tox -e bandit -c ../../../eng/tox/tox.ini```


#### ApiStubGen
`ApiStubGen` is an internal tool used to create API stub to help reviewing public APIs in our SDK package using [`APIViewTool`.](https://apiview.dev/) This tool also has some built in lint checks available and purpose of having this step in analyze job is to ensure any  change in code is not impacting stubbing process and also to have more and more custom lint checks added in future.

#### Change log verification

Change log verification is added to ensure package has valid change log for current version. Guidelines to properly maintain the change log is documented [here](https://github.com/Azure/azure-sdk-for-python/blob/master/doc/)

## PR Validation Checks
Each pull request runs various tests using `pytest` in addition to all the tests mentioned above in analyze check. Pull request validation performs 3 different types of test: `whl, sdist and depends`. The following section explains the purpose of each of these tests and how to execute them locally. All pull requests are validated on multiple python versions across different platforms. Find the test matrix below.


|`Python  Version`|`Platform`  |
|--|--|
|2.7|Linux|
|3.5|Windows|
|3.8|Linux|

### PR validation tox test environments
Tests are executed using tox environment and following are the tox test names that are part of pull request validation
#### whl
This test installs wheel of the package being tested and runs all tests cases in the package using `pytest`. Following is the command to run this test environment locally.

1. Go to package root folder on a command line
2. Run following command
   ``tox -e whl -c ../../../eng/tox/tox.ini``

#### sdist
This test installs sdist of the package being tested and runs all tests cases in the package using `pytest`. Following is the command to run this test environment locally.

1. Go to package root folder on a command line
2. Run following command
   ``tox -e sdist -c ../../../eng/tox/tox.ini``

#### depends
The `depends` check ensures all modules in a target package can be successfully imported. Actually installing and importing will verify that all package requirements are properly set in setup.py and that the `__all__` set for the package is properly defined. This test installs the package and its required packages, then executes `from <package-root-namespace> import *`. For example from `azure-core`, the following would be invoked:  `from azure.core import *`.

Following is the command to run this test environment locally.

1. Go to package root folder on a command line
2. Run following command
   ``tox -e sdist -c ../../../eng/tox/tox.ini``


## Nightly CI Checks

Nightly continuous integration checks run all tests mentioned above in Analyze and Pull request checks in addition to multiple other tests. Nightly CI checks run on all python versions that are supported by Azure SDK packages across multiple platforms.

![res/full_matrix.png](res/full_matrix.png)

Regression also executes:
![res/regression.png](res/regression.png)

Nightly CI check runs following additional tests to ensure the dependency between a package being developed against released packages to ensure backward compatibility. Following is the explanation of why we need dependency tests to ensure backward compatibility.

Imagine a situation where package `XYZ` requires another package `ABC` and as per the package requirement of `XYZ`, It should work with any version between 1.0 and 2.0 of package `ABC`. 
 
Package `XYZ` requires package `ABC` 
 
As a developer of package `XYZ`, we need to ensure that our package works fine with all versions of ABC as long as it is within package requirement specification. 
 
Another scenario where regression test( reverse dependency) is required. Let's take same example above and assume we are developers of package `ABC` which is taken as required package by another  package `XYZ` 
 
Package `ABC is required by package `XYZ`


As a developer of `ABC`, we need to ensure that any new change in `ABC` is not breaking the use of `XYZ` and hence ensures backward compatibility. 
 
Let's take few Azure SDK packages instead of dummy names to explain this in a context we are more familiar of. 
 
Most of the Azure SDK packages require `azure-core` and this requirement is within a range for e.g. `azure-storage-blob` that requires `azure-core >1.0.0, <2.0.0`. So any new change in azure-storage-blob needs to make sure it works fine with all versions of azure-core between 1.0.0 and 2.0.0(Both included).  
Similarly any new version of azure-core needs to ensure that it is still compatible with all released package versions which takes azure-core as required package. 
 
It is lot of combinations if we need to run tests for all released versions within the range of requirement specification. In order to reduce the test matrix and at the same time ensures the quality, we currently run the test using oldest released and latest released packages and skips any version in between. 

Following are the additional tests we run during nightly CI checks.

#### Latest Dependency Test 
 
This test makes sure that a package being developed works absolutely fine using latest released version of required Azure SDK package as long as there is a released version which satisfies the requirement specification. Workflow of this test is as follows: 
 
1.  Identify if any azure SDK package is marked as required package in setup.py of current package being tested. 
Note: Any dependency mentioned only in dev_requirements are not considered to identify dependency. 
2.  Identify latest released version of required azure sdk package on PyPI 
3.  Install latest released version of required package instead of dev dependency to package in code repo 
4.  Install current package that is being tested 
5.  Run pytest of all test cases in current package 
 
Tox name of this test is `latestdependency` and steps to manually run this test locally is as follows. 
1.  Go to package root. For e.g azure-storage-blob or azure-identity 
2.  Run following command 
        `Tox –e latestdependency –c ../../../tox/tox.ini`
 
 
#### Minimum Dependency Test 
 
This test makes sure that a package being developed works absolutely fine using oldest released version of required Azure SDK package as long as there is a released version which satisfies the requirement specification. Workflow of this test is as follows: 
 
1.  Identify if any azure SDK package is marked as required package in setup.py of current package being tested. 
Note: Any dependency mentioned only in dev_requirements are not considered to identify dependency. 
2.  Identify oldest released version of required azure sdk package on PyPI 
3.  Install oldest released version of required package instead of dev dependency to package in code repo 
4.  Install current package that is being tested 
5.  Run pytest of all test cases in current package 
 
Tox name of this test is `mindependency` and steps to manually run this test locally is as follows. 
1.  Go to package root. For e.g azure-storage-blob or azure-identity 
2.  Run following command 
`Tox –e mindependency –c ../../../tox/tox.ini`
 
 
#### Regression Test 
 
As mentioned earlier, regression test or reverse dependency test is added to avoid a regression scenario for customers when any new change is made in a package that is required by other packages. Currently we have only very few Azure SDK packages that are added as required package by other Azure SDK package. As of now, list of these required packages are: 
`azure-core`
`azure-eventhub`
`azure-storage-blob`
 
Our regression framework automatically finds any such package that is added as required package so this list is not hardcoded. 
 
We have two different set of regression tests to verify regression scenarios against oldest and latest released dependent packages. 
•   Regression using latest released dependent package 
•   Regression using oldest released dependent package 
 
One main difference between regression tests and forward dependency test( latest and mindependency) is in terms of what test cases are executed as part of the tests. While forward dependency tests executes the test cases in current code repo, regression tests execute the tests that were part of repo at the time of dependent package release. To make it more clear, let's look at an example here. 
 
Let's assume that we are testing regression for azure-core and this test is for regression against latest released dependent packages. Test will identify all packages that takes azure-core as required package and finds latest released version of those packages. Test framework install currently being developed azure-core and latest released dependent package and runs the test cases in dependent package, for e.g. azure-identity, that were part of repo at the time of releasing depending package. 
 
Workflow of this test is as follows when running regression for an SDK package. 
1.  Identify any packages that takes currently being tested package as required package 
2.  Find latest and oldest released versions of dependent package from PyPI 
3.  Install currently being developed version of package  we are testing regression for. E.g. azure-core 
4.  Checkout the release tag of dependent package from github 
5.  Install latest/oldest version of dependent package. For e.g. azure-identity 
6.  Run test cases within dependent package from checked out branch.  
 
 
Steps to manually run regression test locally: 
1.  Run below command from your git code repo to generate the wheel of package being developed. Currently we have restricted to have prebuilt wheel. 
`./scripts/devops_tasks/build_packages.py --service= <service-name> -d <out-folder>`
2.  Run below command to start regression test locally 
`./scripts/devops_tasks/test_regression.py azure-* --service=<service-name> --whl-dir=<out-folder given above in step 2>`
 
 
How to run these additional tests on azure pipelines manually 
 
Following variables can be set at queueing time in order to run these additional tests which are by default run only for scheduled runs. 
 
•   Latest and oldest dependency test in addition to basic testing 
Variable name: `Run.DependencyTest`
Value: true 
 
•   Regression test 
Variable name: `Run.Regression`
Value: true 
