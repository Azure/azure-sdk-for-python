import functools
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy

VoiceLivePreparer = functools.partial(
    EnvironmentVariableLoader,
    "voicelive",
    voicelive_openai_endpoint="fake-endpoint",
    voicelive_openai_key="fake-key",
)