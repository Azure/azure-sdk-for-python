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


## Configuring ReplayableTest

The only configuration of `ReplayableTest` that is "exposed"
(in the sense of being accessible other than through subclassing)
is whether tests should be run in "live" or "playback" mode.
This can be set in the following two ways,
of which the first takes precedence:
* Set the environment variable `AZURE_TEST_RUN_LIVE`.
  Any value will cause the tests to run in live mode;
  if the variable is unset the default of playback mode will be used.
* Specify a boolean value for `live-mode` in a configuration file,
  the path to which must be specified by a `ReplayableTest` subclass as described below
  (i.e. by default no config file will be read).
  True values mean "live" mode; false ones mean "playback."

"Live" and "playback" mode are actually just shorthand for recording modes
in the underlying VCR.py package;
they correspond to "all" and "once"
as described in the [VCR.py documentation](https://vcrpy.readthedocs.io/en/latest/usage.html#record-modes).

### Subclassing ReplayableTest and features

Most customization of `ReplayableTest` is accessible only through subclassing.

The two main users of `ReplayableTest` are
[azure-cli](https://github.com/Azure/azure-cli)
and [azure-sdk-for-python](https://github.com/Azure/azure-sdk-for-python).
Each uses a subclass of `ReplayableTest` to add context-specific functionality
and preserve backward compatibility with test code
prior to the existence of `azure-devtools`.
For example, azure-cli's [compatibility layer](https://github.com/Azure/azure-cli/tree/master/src/azure-cli-testsdk)
adds methods for running CLI commands and evaluating their output.

Subclasses of `ReplayableTest` can configure its behavior
by passing the following keyword arguments when they call
its `__init__` method (probably using `super`):

* `config_file`: Path to a configuration file.
  It should be in the format described in Python's
  [ConfigParser](https://docs.python.org/3/library/configparser.html) docs
  and currently allows only the boolean option `live-mode`.
* `recording_dir` and `recording_name`:
  Directory path and file name, respectively,
  for the recording that should be used for a given test case.
  By default, the directory will be a `recordings` directory
  in the same location as the file containing the test case,
  and the file name will be the same as the test method name.
  A `.yaml` extension will be appended to whatever is used for `recording_name`.
* `recording_processors` and `replay_processors`:
  Lists of `RecordingProcessor` instances for making changes to requests and responses
  during test recording and test playback, respectively.
  See [recording_processors.py](https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-devtools/src/azure_devtools/scenario_tests/recording_processors.py)
  for some examples and how to implement them.
* `recording_patches` and `replay_patches`:
  Lists of patches to apply to functions, methods, etc.
  during test recording and playback, respectively.
  See [patches.py](https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-devtools/src/azure_devtools/scenario_tests/patches.py)
  for some examples. Note the `mock_in_unit_test` function
  which abstracts out some boilerplate for applying a patch.


<!--
Note: This document's source uses
[semantic linefeeds](http://rhodesmill.org/brandon/2012/one-sentence-per-line/)
to make diffs and updates clearer.
-->
