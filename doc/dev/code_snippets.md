# Code Snippets

All code snippets in README should be up to date and runnable. And we want to have single source of truth hence we only need to maintain one copy. To achieve it, we want to have:

- [Define snippet definitions in the samples folder](#create-samples)
- [In README, refer to the code snippets from the samples](#refer-samples)
- [Run `python_snippet_updater.py` to keep them in sync](#python_snippet_updater-tool)

## Create samples

Samples need to store in the samples folder under each service. In each sample file, we use `# [START snippet_name]` & `# [END snippet_name]` to note a code snippet.

**Note:** valid characters for a snippet name are [A-Z a-z0-9_]

A sample code snippet could be like:

```python
# [START asyncio]
from azure.core.pipeline.transport import AsyncioRequestsTransport

async with AsyncPipeline(AsyncioRequestsTransport(), policies=policies) as pipeline:
    response = await pipeline.run(request)
# [END asyncio]
```

https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/samples/test_example_async.py#L63-L68

## Refer samples

Instead of copying the code snippet into README which is hard to maintain and validate, we add reference to the sample snippet in README. We use the annotation `\<!-- SNIPPET:file_name.snippet_name-->` to refer the code snippet in README file.

If you have a file in `samples\text_example_async.py` with a snippet named `asyncio`, you can reference it in your README like:

````markdown
<!-- SNIPPET:test_example_async.asyncio -->
```python
```
<!-- END SNIPPET -->
````

> Make sure you include a Python code fence within the snippet reference!

## Run python_snippet_updater tool

```powershell
python <azure-sdk-for-python>/tools/azure-sdk-tools/ci_tools/snippet_update/python_snippet_updater.py <path_to_the_service>
```

The script scans the snippets in samples folder and populates snippet references in README with the snippet definitions from samples folder.

The example reference above could become:

````markdown
<!-- SNIPPET:test_example_async.asyncio -->

```python
from azure.core.pipeline.transport import AsyncioRequestsTransport

async with AsyncPipeline(AsyncioRequestsTransport(), policies=policies) as pipeline:
    response = await pipeline.run(request)
```

<!-- END SNIPPET -->
````

Once you've run the script, you can commit your changes. Now you are all set!
