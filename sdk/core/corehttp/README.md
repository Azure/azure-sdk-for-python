
# Core HTTP shared client library for Python

`corehttp` provides shared exceptions and modules for Python SDK client libraries.

## Getting started

Typically, you will not need to install `corehttp`, as it will be installed when you install one of the client libraries using it.

### Transports

To use `corehttp`, you will need to choose a transport implementation. `corehttp` provides the following transports:

Synchronous transports:
- `RequestsTransport` - A synchronous transport based on the [Requests](https://requests.readthedocs.io/en/master/) library.
- `HttpXTransport` - An synchronous transport based on the [HTTPX](https://www.python-httpx.org/) library.

Asynchronous transports:
- `AioHttpTransport` - An asynchronous transport based on the [aiohttp](https://docs.aiohttp.org/en/stable/) library.
- `AsyncHttpXTransport` -  An asynchronous transport based on the [HTTPX](https://www.python-httpx.org/) library.

Each transport has its own dependencies, which you can install using the `corehttp` extras:

```bash
# Install individually.
pip install corehttp[requests]
pip install corehttp[aiohttp]
pip install corehttp[httpx]

# Install multiple.
pip install corehttp[requests,httpx]
```

If no transports are specified, `corehttp` will default to using `RequestsTransport` for synchronous pipeline requests and `AioHttpTransport` for asynchronous pipeline requests.

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit [https://cla.microsoft.com](https://cla.microsoft.com).

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information, see the
[Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/)
or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any
additional questions or comments.


