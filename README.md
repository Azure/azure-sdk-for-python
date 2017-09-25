The eventhubs package provides a simple client to read events from an Event Hub.

**This project is under active development. Major API changes may be excepted.**

It is built on top of the [Apache Qpid Proton](https://qpid.apache.org/proton/) Python binding and provides the following extra functionalities.
* Specifies address with Event Hubs specific concepts, e.g. entity name, consumer group, and partition. The client constructs the AMQP address from those.
* Provides an offset to read events. The client constructs the AMQP filter supported by the Event Hubs service.
* Provides fault tolerance with transient errors. When the AMQP link, session or connection is closed due to transient errors, the client automatically recover.
* Provides an EventData helper to read data from the AMQP message.


# Example

Follow the steps below to run the `recv.py` example.
* Install Proton if not done yet. Please follow the [instructions here](https://git-wip-us.apache.org/repos/asf?p=qpid-proton.git;a=blob;f=INSTALL.md;hb=0.17.0) to install Proton. Ensure that SSL prerequisites are available so Proton is built and installed with SSL support.
* Install eventhubs (by running `setup.py`) if not done yet.
* In `./examples/recv.py`, update `ADDRESS` with your Event Hub configuration.
* Run `recv.py`.

If anything goes wrong, set the frame trace environment variable to enable Proton frame tracing (`export PN_TRACE_FRM=1`).

# Contributing

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
