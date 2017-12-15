The eventhubs Python client provides,
* a sender to publish events to the Event Hubs service.
* a receiver to read events from the Event Hubs service.
On Python 3.5 and above, it also includes,
* async sender and receiver that supports async/await methods.
* an event processor host module that manages the distribution of partition readers.

# Build and Install
* Proton-C and its Python binding: https://github.com/apache/qpid-proton/blob/master/INSTALL.md
For eventprocessorhost, you will also need (list for Fedora 26, adjust for other distributions),
* libs: libxml2-devel, libxslt-devel, libffi-devel, python3-cffi, redhat-rpm-config
* Python packages: requests, bs4, lxml, azure-storage, azure-storage-blob

*On Windows a private patch to proton-c code is required for the library to work.*

# Examples
* ./examples/send.py - use sender to publish events
* ./examples/recv.py - use receiver to read events
* ./examples/send_async.py - async/await support of a sender
* ./examples/recv_async.py - async/await support of a receiver
* ./examples/eph.py - event processor host
* ./tests/send.py - how to perform parallel send operations to achieve high throughput
* ./tests/recv.py - how to write an event pump to read events from multiple partitions

# Logging
* enable 'eventhubs' logger to collect traces from the library
* enable AMQP frame level trace by setting environment variable (`export PN_TRACE_FRM=1`)

# Contributing
This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
