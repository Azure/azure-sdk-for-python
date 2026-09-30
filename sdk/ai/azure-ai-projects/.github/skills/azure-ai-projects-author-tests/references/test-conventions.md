# azure-ai-projects test conventions

Use the nearest feature tests as the final authority. Simple recorded anchors are [`test_deployments.py`](../../../../tests/deployments/test_deployments.py) and its [async mirror](../../../../tests/deployments/test_deployments_async.py); shared clients and preparers live in [`test_base.py`](../../../../tests/test_base.py).

## Test kind

- Keep deterministic model/customization tests as ordinary enabled unit tests when no service call or recording is needed.
- Service tests derive from `TestBase`, use `@servicePreparer()` (or a narrower existing preparer), and use `@recorded_by_proxy` or `@recorded_by_proxy_async`.
- Create clients with `self.create_client(**kwargs)` or `self.create_async_client(**kwargs)` so playback uses fake credentials and sanitized endpoints. Pass `allow_preview=True` only when the neighboring feature/API requires it.
- Mirror sync files/methods with `_async` naming and equivalent assertions/cleanup.

## New coverage stays enabled

Do not add `skip`, `skipif`, `xfail`, or any other disabling marker to newly created recorded files, classes, or methods. Write the complete operation flow and leave it enabled even when no Test Proxy recording exists yet, so PR validation surfaces the missing-recording error. Updates to pre-existing recorded tests retain their current enabled or skipped state.

## Recording-safe design

Use stable inputs where possible. For generated names/IDs/timestamps, add the narrowest function-scoped sanitizer or reuse a sanitizer in `tests\conftest.py`. Add sanitized defaults to the narrowest `EnvironmentVariableLoader` preparer. Never commit credentials, tokens, account names, or raw endpoints.

Place reusable payloads under `tests\test_data`; preserve LF handling and `.gitattributes` patterns for uploaded text files. Use `try/finally` cleanup and assert returned IDs, names, states, paging behavior, and error contracts rather than only checking non-`None`.

Include `RecordedTransport.HTTPX2` when the test also uses an OpenAI/httpx client. When combining `pytest.mark.parametrize` with recorder decorators, copy the package's passthrough-wrapper pattern described in [`test_finetuning.py`](../../../../tests/finetuning/test_finetuning.py).

Do not edit `assets.json` or add recordings in this workflow. Collection must succeed, but do not run new service tests live. Keep them enabled and direct authors to the SDK maintainer for help when PR validation reports missing recordings.
