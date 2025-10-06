import functools
import os
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy

VoiceLivePreparer = functools.partial(
    EnvironmentVariableLoader,
    "voicelive",
    voicelive_openai_endpoint=os.getenv("VOICELIVE_OPENAI_ENDPOINT", "fake_endpoint"),
    voicelive_openai_api_key=os.getenv("VOICELIVE_OPENAI_API_KEY", "fake_api_key"),
)
