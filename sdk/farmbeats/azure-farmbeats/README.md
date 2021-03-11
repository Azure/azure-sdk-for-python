# Farmbeats SDK

## Usage

```python
from azure.farmbeats import FarmbeatsClient
from datetime import datetime, timedelta

contosofarmbeats = FarmbeatsClient(
    instance_url="https://contoso.farmbeats.azure.net",
    tenant_id="01234567-89ab-cdef-0123-456789abcdef",
    client_id="01234567-89ab-cdef-0123-456789abcdef",
    client_secret="abcdefghijklmnopqrstuvwxyz",
)

contosofarmbeats.farmers.get_all(
    min_last_modified_date_time=datetime.now() - timedelta(minutes=5)
)
```