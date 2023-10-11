import os
import tempfile
from ci_tools.snippet_update.python_snippet_updater import (
    get_snippet,
    update_snippet,
    check_snippets,
    check_not_up_to_date,
)


def test_update_snippet():
    temp_sample = tempfile.NamedTemporaryFile(delete=False)
    snippets = """
                 # [START trio]
                 from azure.core.pipeline.transport import TrioRequestsTransport

                 async with AsyncPipeline(TrioRequestsTransport(), policies=policies) as pipeline:
                     return await pipeline.run(request)
                 # [END trio]
    """
    temp_sample.write(snippets.encode("utf-8"))
    temp_sample.close()
    full_path_sample = temp_sample.name
    get_snippet(full_path_sample)
    parsed_snippets = check_snippets()
    print(parsed_snippets)
    assert len(parsed_snippets) == 1
    keys = parsed_snippets.keys()
    snippet_name = list(keys)[0]

    temp_readme = tempfile.NamedTemporaryFile(delete=False)
    readme = (
        """
<!-- SNIPPET:"""
        + snippet_name
        + """ -->

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
key = os.environ["AZURE_LANGUAGE_KEY"]

text_analytics_client = TextAnalyticsClient(endpoint, AzureKeyCredential(key))
```

<!-- END SNIPPET -->
        """
    )
    temp_readme.write(readme.encode("utf-8"))
    temp_readme.close()
    update_snippet(temp_readme.name)
    with open(temp_readme.name, "rb") as file:
        content = file.read()
        print(content)

    assert check_not_up_to_date()
    os.unlink(temp_readme.name)
    os.unlink(full_path_sample)


if __name__ == "__main__":
    test_update_snippet()
