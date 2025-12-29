# azure-sdk-tools `integration` tests

## Integration with the repo

These tests are within the `integration` folder because these tests are designed to run on _actual source from the repo_. Given that, these tests are guaranteed to be broken by actual code changes eventually. They are kept separate here for this exact reason.

See `test_package_discovery.py` or `proxy` folder for an examples.

## Manually created scenarios

The second category of `integration` tests are those whose scenario is created specifically for the test. Those will be present under `scenarios`.

Each folder within the `scenarios` folder will be used by one or multiple integration tests.



