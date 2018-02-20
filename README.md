The eventhubs Python client provides,
* a sender to publish events to the Event Hubs service.
* a receiver to read events from the Event Hubs service.
On Python 3.5 and above, it also includes,
* async sender and receiver that supports async/await methods.
* an event processor host module that manages the distribution of partition readers.

# Build and Install

### Local
The core library requires Apache Proton-C and its Python binding.
* build Proton-C: https://github.com/apache/qpid-proton/blob/master/INSTALL.md  

For eventprocessorhost, you will also need (list for Fedora 26, adjust for other distributions),
* libs: libxml2-devel, libxslt-devel, libffi-devel, python3-cffi, redhat-rpm-config
* Python packages: requests, bs4, lxml, azure-storage, azure-storage-blob

*On Windows a private patch to proton-c code is required for the library to work.*

### Docker

The following Dockerfile at  `./examples/Dockerfile` creates a Docker image with Apache Proton and the Azure Event Hubs SDK.

The base image is Python `3.6-slim-stretch` and Proton `0.18.1` but you can set the `PYTHON_IMAGE_VERSION` `PROTON_VERSION` `PYTHON_DIR_VERSION` when building the image.

```
docker build -t azure-eventhubs-sdk --build-arg PYTHON_IMAGE_VERSION=3.6-slim-stretch --build-arg PROTON_VERSION=0.18.1 --build-arg PYTHON_DIR_VERSION=3.6 .
```

After the image is built you can run the samples with
```
docker run -it azure-eventhubs-sdk python examples/send.py
```

##### Note that you have fill the Event Hub connection parameters in the example py files.

# Examples
* ./examples/send.py - use sender to publish events
* ./examples/recv.py - use receiver to read events
* ./examples/send_async.py - async/await support of a sender
* ./examples/recv_async.py - async/await support of a receiver
* ./examples/eph.py - event processor host
* ./examples/Dockerfile - create a Docker image with Apache Proton and Azure Event Hubs SDK

* ./tests/send.py - how to perform parallel send operations to achieve high throughput
* ./tests/recv.py - how to write an event pump to read events from multiple partitions

# Logging
* enable 'eventhubs' logger to collect traces from the library
* enable AMQP frame level trace by setting environment variable (`export PN_TRACE_FRM=1`)

# Contributing
This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
