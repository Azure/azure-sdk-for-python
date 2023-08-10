# Release History

## 1.0.0b1 (2023-05-31)

New Feature Management Library

Provides support for using Feature Flags in your application. Enables:

* Loading Feature Flags from Azure App Configuration, Json Files, or a Dictionary
* Checking if a Feature Flag is enabled/disabled
* Feature Filters, including built in; Microsoft.Targeting, and Microsoft.TimeWindow
* Custom Feature Filters

```python
from feature.management import FeatureManager
from azure.appconfiguration.provider import load, SettingSelector
from azure.identity import DefaultAzureCredential
import os

config = load(endpoint=endpoint, credential=DefaultAzureCredential())

feature_manager = FeatureManager(config)

# Is always true
print("Alpha is ", feature_manager.is_enabled("Alpha"))
```
