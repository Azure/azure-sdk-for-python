# Table of Contents
1. [The perfstress framework](#the-perfstress-framework)
    - [The framework baseclasses](#the-provided-baseclasses)
        - [PerfStressTest](#the-perfstresstest-baseclass)
        - [BatchPerfTest](#the-batchperftest-baseclass)
        - [EventPerfTest](#the-eventperftest-baseclass)
    - [Default command options](#default-command-options)
    - [Running with test proxy](#running-with-the-test-proxy)
2. [Adding performance tests to an SDK](#adding-performance-tests-to-an-sdk)
    - [Writing a test](#writing-a-test)
    - [Writing a batch test](#writing-a-batch-test)
    - [Adding legacy T1 tests](#adding-legacy-t1-tests)
3. [Running the tests](#running-the-tests)
    - [Running the system tests](#running-the-system-tests)
4. [Readme](#readme)

[comment]: # ( cspell:ignore perfstresstest batchperftest )

# The perfstress framework

The perfstress framework has been added to azure-devtools module. The code can be found [here](https://github.com/Azure/azure-sdk-for-python/tree/main/tools/azure-devtools/src/azure_devtools/perfstress_tests).
The framework provides a baseclass to inherit from when writing tests, as well as some tools and utilities to facilitate running
the tests. To start using the framework, make sure that `azure-devtools` is included in the `dev_requirements.txt` for the SDK:
```
-e ../../../tools/azure-devtools
```
The perfstress framework offers the following:
- The `perfstress` commandline tool.
- The `PerfStressTest` baseclass (each test run counted as a single data point).
- The `BatchPerfTest` baseclass (each test run counted as 1 or more data points).
- The `EventPerfTest` baseclass (supports a callback based event handler).
- Stream utilities for uploading/downloading without storing in memory: `RandomStream`, `AsyncRandomStream`, `WriteStream`.
- A `get_random_bytes` utility for returning randomly generated data.
- A series of "system tests" to test the perfstress framework along with the performance of the raw transport layers (requests, aiohttp, etc).

## The provided baseclasses:
The perf framework provides three baseclasses to accommodate testing different SDK scenarios. Depending on which baseclass you select, different
methods will need to be implemented. All of them have a common base API (`_PerfTestBase`), defined below:

```python
class _PerfTestBase:
    args = {}  # Command line arguments

    @property
    def completed_operations(self) -> int:
        # Total number of operations completed by run_all(). Reset after warmup.

    @property
    def last_completion_time(self) -> float:
        # Elapsed time between start of warmup/run and last completed operation. Reset after warmup.

    def __init__(self, arguments):
        # The command line args can be accessed on construction.

    async def global_setup(self) -> None:
        # Can be optionally defined. Only run once per process, regardless of multi-threading.
        # The baseclasses will also define logic here, so if you override this method, make sure you include a call to super().

    async def global_cleanup(self) -> None:
        # Can be optionally defined. Only run once per process, regardless of multi-threading.
        # The baseclasses will also define logic here, so if you override this method, make sure you include a call to super().

    async def post_setup(self) -> None:
        # Post-setup called once per parallel test instance.
        # Used by base classes to setup state (like test-proxy) after all derived class setup is complete.
        # There should be no need to overwrite this function.

    async def pre_cleanup(self) -> None:
        # Pre-cleanup called once per parallel test instance.
        # Used by base classes to cleanup state (like test-proxy) before all derived class cleanup runs.
        # There should be no need to overwrite this function.

    async def setup(self) -> None:
        # Can be optionally defined. Run once per test instance, after global_setup.
        # The baseclasses will also define logic here, so if you override this method, make sure you include a call to super().

    async def cleanup(self) -> None:
        # Can be optionally defined. Run once per test instance, before global_cleanup.
        # The baseclasses will also define logic here, so if you override this method, make sure you include a call to super().

    async def close(self) -> None:
        # Can be optionally defined. Run once per test instance, after cleanup and global_cleanup.
        # The baseclasses will also define logic here, so if you override this method, make sure you include a call to super().

    def run_all_sync(self, duration: int) -> None:
        # Run all sync tests, including both warmup and duration. This method is implemented by the provided base
        # classes, there should be no need to overwrite this function.

    async def run_all_async(self, duration: int) -> None:
        # Run all async tests, including both warmup and duration. This method is implemented by the provided base
        # classes, there should be no need to overwrite this function.

    @staticmethod
    def add_arguments(parser):
        # Override this method to add test-specific argparser args to the class.
        # These are accessible in __init__() and the self.args property.

    @staticmethod
    def get_from_env(variable):
        # Get the value of an env var. If empty or not found, a ValueError will be raised.
```
### The PerfStressTest baseclass
This is probably the most common test baseclass, and should be used where each test run represents 1 logical successful result.
For example, 1 successful service request, 1 file uploaded, 1 output downloaded, etc.
Along with the above base API, the following methods will need to be implemented:

```python
class PerfStressTest:
    def run_sync(self) -> None:
        # Must be implemented. This will be the perf test to be run synchronously.

    async def run_async(self) -> None:
        # Must be implemented. This will be the perf test to be run asynchronously.
        # If writing a test for an SDK without async support (e.g. a T1 legacy SDK), implement this method and raise an exception.

```
### The BatchPerfTest baseclass
The `BatchPerfTest` class is the parent class of the above `PerfStressTest` class that is further abstracted to allow for more flexible testing of SDKs that don't conform to a 1:1 ratio of operations to results.
This baseclass should be used where each test run represent a more than a single result. For example, results that are uploaded
or downloaded in batches.
Along with the above base API, the following methods will need to be implemented:

```python
class BatchPerfTest:
    def run_batch_sync(self) -> int:
        # Run cumulative operation(s) synchronously - i.e. an operation that results in more than a single logical result.
        # When inheriting from BatchPerfTest, this method will need to be implemented.
        # Must return the number of completed results represented by a single successful test run.

    async def run_batch_async(self) -> int:
        # Run cumulative operation(s) asynchronously - i.e. an operation that results in more than a single logical result.
        # When inheriting from BatchPerfTest, this method will need to be implemented.
        # Must return the number of completed results represented by a single successful test run.
        # If writing a test for an SDK without async support (e.g. a T1 legacy SDK), implement this method and raise an exception.

```
### The EventPerfTest baseclass
This baseclass should be used when SDK operation to be tested requires starting up a process that acts on events via callback.
Along with the above base API, the following methods will need to be implemented:
```python
class EventPerfTest:
    def event_raised_sync(self) -> None:
        # This method should not be overwritten, instead it should be called in your sync callback implementation
        # to register a single successful event.

    def error_raised_sync(self, error):
        # This method should not be overwritten, instead it should be called in your sync callback implementation
        # to register a failure in the event handler. This will result in the test being shutdown.

    async def event_raised_async(self):
        # This method should not be overwritten, instead it should be called in your async callback implementation
        # to register a single successful event.

    async def error_raised_async(self, error):
        # This method should not be overwritten, instead it should be called in your async callback implementation
        # to register a failure in the event handler. This will result in the test being shutdown.

    def start_events_sync(self) -> None:
        # Must be implemented - starts the synchronous process for receiving events.
        # This can be blocking for the duration of the test as it will be run during setup() in a thread.

    def stop_events_sync(self) -> None:
        # Stop the synchronous process for receiving events. Must be implemented. Will be called during cleanup.

    async def start_events_async(self) -> None:
        # Must be implemented - starts the asynchronous process for receiving events.
        # This can be blocking for the duration of the test as it will be scheduled in the eventloop during setup().

    async def stop_events_async(self) -> None:
        # Stop the asynchronous process for receiving events. Must be implemented. Will be called during cleanup.

```

## Default command options
The framework has a series of common command line options built in:
- `-d --duration=10` Number of seconds to run as many operations (the "run" function) as possible. Default is 10.
- `-p --parallel=1` Number of tests to run in parallel. Default is 1.
- `--processes=multiprocessing.cpu_count()` Number of concurrent processes that the parallel test runs should be distributed over. This is used
  together with `--parallel` to distribute the number of concurrent tests first between available processes, then between threads within each
  process. For example if `--parallel=16 --processes=4`, 4 processes will be started, each running 4 concurrent threaded test instances.
  Best effort will be made to distribute evenly, for example if `--parallel=10 --processes=4`, 4 processes will be start, two of which run 3 threads, and two that run 2 threads. It's therefore recommended that the value of `parallel` be less than, or a multiple of, the value of `processes`.
- `-w --warm-up=5` Number of seconds to spend warming up the connection before measuring begins. Default is 5.
- `--sync` Whether to run the tests in sync or async. Default is False (async).
- `--no-cleanup` Whether to keep newly created resources after test run. Default is False (resources will be deleted).
- `--insecure` Whether to run without SSL validation. Default is False.
- `-x --test-proxies` Whether to run the tests against the test proxy server. Specify the URL(s) for the proxy endpoint(s) (e.g. "https://localhost:5001"). Multiple values should be semi-colon-separated.
- `--profile` Whether to run the perftest with cProfile. If enabled (default is False), the output file of a single iteration will be written to the current working directory in the format `"cProfile-<TestClassName>-<TestID>-<sync|async>.pstats"`. **Note:** The profiler is not currently supported for the `EventPerfTest` baseclass.

## Running with the test proxy
Follow the instructions here to install and run the test proxy server:
https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy

Once running, in a separate process run the perf test in question, combined with the `-x` flag to specify the proxy endpoint.
```cmd
(env) ~/azure-storage-blob/tests> perfstress DownloadTest -x "https://localhost:5001"
```

# Adding performance tests to an SDK
The performance tests will be in a submodule called `perfstress_tests` within the `tests` directory in an SDK project.
For example:
```
sdk/storage/azure-storage-blob/tests/perfstress_tests
```
This `perfstress_tests` directory is a module, and so must contain an `__init__.py` file. This can be empty.

## Writing a test
To add a test, import and inherit from one of the provided baseclasses and populate the functions as needed.
The name of the class will be the name of the perf test, and is what will be passed into the command line to execute that test.
```python
from azure_devtools.perfstress_tests import PerfStressTest

from azure.storage.blob import BlobServiceClient as SyncBlobServiceClient
from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient


class ListContainersTest(PerfStressTest):

    def __init__(self, arguments):
        super().__init__(arguments)

        # Auth configuration
        connection_string = self.get_from_env("AZURE_STORAGE_CONNECTION_STRING")

        # Create clients
        self.service_client = SyncBlobServiceClient.from_connection_string(conn_str=connection_string)
        self.async_service_client = AsyncBlobServiceClient.from_connection_string(conn_str=connection_string)

    async def global_setup(self):
        """The global setup is run only once.

        Use this for any setup that can be reused multiple times by all test instances.
        """
        await super().global_setup()
        containers = [self.async_service_client.create_container(str(i)) for i in self.args.num_containers]
        await asyncio.wait(containers)

     async def global_cleanup(self):
        """The global cleanup is run only once.

        Use this to cleanup any resources created in setup.
        """
        async for container in self.async_service_client.list_containers():
            await self.async_service_client.delete_container(container)
        await super().global_cleanup()

    async def close(self):
        """This is run after cleanup.

        Use this to close any open handles or clients.
        """
        await self.async_service_client.close()
        await super().close()

    def run_sync(self):
        """The synchronous perf test.

        Try to keep this minimal and focused. Using only a single client API.
        Avoid putting any ancillary logic (e.g. generating UUIDs), and put this in the setup/init instead
        so that we're only measuring the client API call.
        """
        for _ in self.client.list_containers():
            pass

    async def run_async(self):
        """The asynchronous perf test.

        Try to keep this minimal and focused. Using only a single client API.
        Avoid putting any ancillary logic (e.g. generating UUIDs), and put this in the setup/init instead
        so that we're only measuring the client API call.
        """
        async for _ in self.async_client.list_containers():
            pass

    @staticmethod
    def add_arguments(parser):
        super(ListContainersTest, ListContainersTest).add_arguments(parser)
        parser.add_argument('--num-containers', nargs='?', type=int, help='Number of containers to list. Defaults to 100', default=100)
```
### Common test base
If you're writing a suite of tests for an SDK, that all make use of common arguments or logic, adding one or more of your own test base can be helpful. These can also be used to navigate different layers of a client hierarchy.
Here is an example Storage test base class, to be used for the Blob upload and download tests described below:
```python
from azure_devtools.perfstress_tests import PerfStressTest

from azure.storage.blob import BlobServiceClient as SyncBlobServiceClient
from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient

class _StorageStreamTestBase(PerfStressTest):

    def __init__(self, arguments):
        super().__init__(arguments)

        # Any common attributes
        self.container_name = 'stream-perf-tests'

        # Auth configuration
        connection_string = self.get_from_env("AZURE_STORAGE_CONNECTION_STRING")

        # Create clients
        self.service_client = SyncBlobServiceClient.from_connection_string(conn_str=connection_string)
        self.async_service_client = AsyncBlobServiceClient.from_connection_string(conn_str=connection_string)

    async def global_setup(self):
        await super().global_setup()

        # Any common setup used by all the streaming tests
        await self.async_service_client.create_container(self.container_name)

     async def global_cleanup(self):
        # Any common cleanup used by all the streaming tests
        await self.async_service_client.delete_container(self.container_name)
        await super().global_cleanup()

    async def close(self):
        await self.async_service_client.close()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        super(ListContainersTest, ListContainersTest).add_arguments(parser)

        # Add any common arguments for the streaming test cases
        parser.add_argument('--max-concurrency', nargs='?', type=int, help='Number of concurrent threads to upload/download the data. Defaults to 1.', default=1)
        parser.add_argument('--size', nargs='?', type=int, help='Size in bytes for the amount of data to be streamed. Defaults to 1024 bytes', default=1024)
```

### Testing with streams
If you need to test any kind of streaming behaviour (e.g. upload or download) then use the provided read and write file-like implementations. These will generate random data, while not storing more than the current chunk in memory. This prevents memory errors when running with large payloads at high parallelism.
#### Example upload stream test:
```python
from azure_devtools.perfstress_tests import RandomStream, get_random_bytes
from azure_devtools.perfstress_tests import AsyncRandomStream

from ._test_base import _StorageStreamTestBase


class UploadTest(_StorageStreamTestBase):
    def __init__(self, arguments):
        super().__init__(arguments)

        # Setup service clients
        blob_name = "uploadtest"
        self.blob_client = self.service_client.get_blob_client(self.container_name, blob_name)
        self.async_blob_client = self.async_serive_client.get_blob_client(self.container_name, blob_name)

        # Setup readable file-like upload data sources, using the configurable 'size' argument
        self.upload_stream = RandomStream(self.args.size)
        self.upload_stream_async = AsyncRandomStream(self.args.size)

    def run_sync(self):
        # The stream needs to be reset at the start of each run.
        # This sets the position index back to 0 with minimal overhead.
        self.upload_stream.reset()

        # Test the upload API
        self.blob_client.upload_blob(
            self.upload_stream,
            length=self.args.size,
            overwrite=True,
            max_concurrency=self.args.max_concurrency)

    async def run_async(self):
        # The stream needs to be reset at the start of each run.
        # This sets the position index back to 0 with minimal overhead.
        self.upload_stream_async.reset()

        # Test the upload API
        await self.async_blob_client.upload_blob(
            self.upload_stream_async,
            length=self.args.size,
            overwrite=True,
            max_concurrency=self.args.max_concurrency)
```
#### Example download stream test:
```python
from azure_devtools.perfstress_tests import get_random_bytes, WriteStream

from ._test_base import _StorageStreamTestBase


class DownloadTest(_StorageStreamTestBase):
    def __init__(self, arguments):
        super().__init__(arguments)

        # Setup service clients
        blob_name = "downloadtest"
        self.blob_client = self.service_client.get_blob_client(self.container_name, blob_name)
        self.async_blob_client = self.async_serive_client.get_blob_client(self.container_name, blob_name)

        self.download_stream = WriteStream()

    async def global_setup(self):
        await super().global_setup()

        # Setup the test by uploading data that can be reused by all test instances.
        data = get_random_bytes(self.args.size)
        await self.async_blob_client.upload_blob(data)

    def run_sync(self):
        # The stream needs to be reset at the start of each run.
        # This sets the position index back to 0 with minimal overhead.
        self.download_stream.reset()

        # Test the API
        stream = self.blob_client.download_blob(max_concurrency=self.args.max_concurrency)
        stream.readinto(self.download_stream)

    async def run_async(self):
        # The stream needs to be reset at the start of each run.
        # This sets the position index back to 0 with minimal overhead.
        self.download_stream.reset()

        # Test the API
        stream = await self.async_blob_client.download_blob(max_concurrency=self.args.max_concurrency)
        await stream.readinto(self.download_stream)
```
## Writing a batch test
#### Example messaging receive test
```python
from azure_devtools.perfstress_tests import BatchPerfTest

from azure.messaging.foo import MockReceiver
from azure.messaging.foo.aio import MockReceiver as AsyncMockReceiver

class MessageReceiveTest(BatchPerfTest):
    def __init__(self, arguments):
        super().__init__(arguments)

        # Setup service clients
        self.receiver_client = MockReceiver()
        self.async_receiver_client = AsyncMockReceiver()

    def run_batch_sync(self) -> int:
        messages = self.receiver_client.receive(
            max_messages=self.args.max_message_count,
            min_messages=self.args.min_message_count
        )
        return len(messages)

    async def run_batch_async(self) -> int:
        messages = await self.async_receiver_client.receive(
            max_messages=self.args.max_message_count,
            min_messages=self.args.min_message_count
        )
        return len(messages)
        
    @staticmethod
    def add_arguments(parser):
        super(MessageReceiveTest, MessageReceiveTest).add_arguments(parser)
        parser.add_argument('--max-message-count', nargs='?', type=int, default=10)
        parser.add_argument('--min-message-count', nargs='?', type=int, default=0)

```

## Adding legacy T1 tests
To compare performance against T1 libraries, you can add tests for a legacy SDK. To do this, add a submodule into the `perfstress_tests` module called `T1_legacy_tests` (and add an empty `__init__.py`).
To configure the exact T1 SDK you wish to compare perf against, add a `t1_test_requirements.txt` file to install any package requirements. Note that this will likely be incompatible with the T2 SDK testing environment, and running the legacy tests will probably need to be from a separate virtual environment (see the [Running the tests](#running-the-tests) section below).
Writing the tests themselves will be done exactly the same way - however it's recommended to prefix the test names with `Legacy` (or similar) to avoid confusion.
```
perfstress_tests
│   README.md
|   __init__.py
│   upload.py
|   download.py
│
└───T1_legacy_tests
|   |   __init__.py
│   │   legacy_upload.py
│   │   legacy_download.py
|   |   t1_test_requirements.txt
```

# Running the tests
In order to run the performance tests, the `azure-devtools` package must be installed. This is done as part of the `dev_requirements`.
Start be creating a new virtual environment for your perf tests. This will need to be a Python 3 environment, preferably >=3.7.
Note that tests for T1 and T2 SDKs usually cannot be run from the same environment, and will need to be setup separately.

### Setup for test resources
Depending on the tests, some resource configuration (e.g. environment variables) may need to be done first. This should documented in the perfstress_tests readme file.
Example from storage:
```
AZURE_STORAGE_CONNECTION_STRING=<live storage account connection string>
```
### Setup for perf test runs

```cmd
(env) ~/azure-storage-file-share> pip install -r dev_requirements.txt
(env) ~/azure-storage-file-share> pip install -e .
```
### Setup for T1 legacy perf test runs

```cmd
(legacy-env) ~/azure-storage-file-share> pip install -r dev_requirements.txt
(legacy-env) ~/azure-storage-file-share> pip install tests/perfstress_tests/T1_legacy_tests/t1_test_requirements.txt
```
### Test commands

When `azure-devtools` is installed, you will have access to the `perfstress` command line tool, which will scan the current module for runable perf tests. Only a specific test can be run at a time (i.e. there is no "run all" feature).

```cmd
(env) ~/azure-storage-file-share> perfstress
```
Using the `perfstress` command alone will list the available perf tests found. Note that the available tests discovered will vary depending on whether your environment is configured for the T1 or T2 SDK.
If your tests are not being discovered, run the `perfstressdebug` command instead for additional logging.

### Example test run command
```cmd
(env) ~/azure-storage-file-share> perfstress UploadTest --parallel=2 --size=10240
```
## Running the system tests
The system tests are used to test the performance of the Python HTTP layers exclusive of the Azure SDK in order to set a performance benchmark.
In order to run these, you will need a Python environment with `systemperf` flavour of `azure-devtools` installed. Installing to a fresh Python environment is recommended.
```cmd
(env) ~/> pip install -e azure-sdk-for-python/tools/azure-devtools[systemperf]
```
Once these dependencies are installed, the `systemperf` command can be run directly to list the available tests:
```cmd
(env)~/> systemperf
```
A specific test can be run in the same manner as an SDK perf test:
```cmd
(env)~/> systemperf AioHttpGetTest --url="http://test-endpoint.com"
```


# Readme

Please add a `README.md` to the perfstress_tests directory so that others know how to setup and run the perf tests, along with a description of the available tests and any support command line options. README files in a `tests/perfstress_tests` directory should already be filtered from CI validation for SDK readmes.
Some examples can be found here:
- [Azure Storage Blob](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/storage/azure-storage-blob/tests/perfstress_tests/README.md)
- [Azure Service Bus](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/servicebus/azure-servicebus/tests/perf_tests/README.md)
