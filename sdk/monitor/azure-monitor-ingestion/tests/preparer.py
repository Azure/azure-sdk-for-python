import functools
from devtools_testutils import EnvironmentVariableLoader

IngestionPreparer = functools.partial(
    EnvironmentVariableLoader, "monitor",
    azure_monitor_dce="https://fake-logsingestion-dcr-lrz3.westus2-1.ingest.monitor.azure.com",
    azure_monitor_dcr_id="dcr-fake66661d12345f9876f32a07af6f34",
    monitor_client_id="11x11111-1x1x-1x1x-9999-11x1x1x11x11",
    monitor_tenant_id="11x11111-1x1x-1x1x-9999-11x1x1x11x11",
    monitor_client_secret="1x11111x-1x1x-111x-x1dx-111xx1x1xx11"
)
