# How to write ReplayableTest based VCR tests

The `scenario_tests` package uses the [VCR.py](https://pypi.python.org/pypi/vcrpy) library
to record the HTTP messages exchanged during a program run
and play them back at a later time,
making it useful for creating "scenario tests"
that interact with Azure (or other) services.
These tests can be replayed at a later time without any network activity,
allowing us to detect changes in the Python layers
between the code being tested and the underlying REST API.


## Overview

Tests all derive from the `ReplayableTest` class
found in `azure_devtools.scenario_tests.base`.
This class exposes the VCR tests using the standard Python `unittest` framework
and allows the tests to be discovered by and debugged in Visual Studio.

When you run a test,
the test driver will automatically detect the test is unrecorded
and record the HTTP requests and responses in a .yaml file
(referred to by VCR.py as a "cassette").
If the test succeeds, the cassette will be preserved
and future playthroughs of the test will come from the cassette
rather than using actual network communication.

If the tests are run on TravisCI,
any tests which cannot be replayed will automatically fail. 

`ReplayableTest` itself derives from `IntegrationTestBase`,
which provides some helpful methods for use in more general unit tests
but no functionality pertaining to network communication.


## Subclassing ReplayableTest and features

The two main users of `ReplayableTest` are
[azure-cli](https://github.com/Azure/azure-cli)
and [azure-sdk-for-python](https://github.com/Azure/azure-sdk-for-python).
Each uses a subclass of `ReplayableTest` to add context-specific functionality
and preserve backward compatibility with test code
prior to the existence of `azure-devtools`.
For example, azure-cli's [compatibility layer](https://github.com/Azure/azure-cli/tree/master/src/azure-cli-testsdk) 
adds methods for running CLI commands and evaluating their output.


<!--
Note: This document's source uses
[semantic linefeeds](http://rhodesmill.org/brandon/2012/one-sentence-per-line/)
to make diffs and updates clearer.
-->