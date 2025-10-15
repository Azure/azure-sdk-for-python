import functools
import os
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy, is_live

VoiceLivePreparer = functools.partial(
    EnvironmentVariableLoader,
    "voicelive",
    voicelive_openai_endpoint="fake_endpoint",
    voicelive_openai_api_key="fake_api_key",
)
