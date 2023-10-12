

# Azure Identity Broker plugin for Python

## Getting started

### Install the package

Install the Azure Identity Broker plugin for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-identity-broker
```


## Examples

Now you can create `azure.identity.broker.InteractiveBrowserBrokerCredential` and `azure.identity.broker.UsernamePasswordBrokerCredential` with broker support.

```python

import win32gui
from azure.identity.broker import InteractiveBrowserBrokerCredential

# Get the handle of the current window
current_window_handle = win32gui.GetForegroundWindow()

credential = InteractiveBrowserBrokerCredential(allow_broker=True, parent_window_handle=current_window_handle)
```


## Troubleshooting

This client raises exceptions defined in [Azure Core](https://learn.microsoft.com/python/api/azure-core/azure.core.exceptions?view=azure-python).


## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
