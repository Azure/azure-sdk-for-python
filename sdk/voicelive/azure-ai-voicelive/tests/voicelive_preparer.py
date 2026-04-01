import functools
import os
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy

VoiceLivePreparer = functools.partial(
    EnvironmentVariableLoader,
    "voicelive",
    voicelive_openai_endpoint=os.getenv("AI_SERVICES_ENDPOINT", "fake_endpoint"),
    voicelive_openai_api_key=os.getenv("AI_SERVICES_KEY", "fake_api_key"),
)
