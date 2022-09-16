# ServiceBus Stress Tests

TODO: README is currently a WIP and has minimal information for local testing. Need to update later.

The `stress_runner.py` file is AN EXAMPLE of how to run the tests, not the actual stress test file.
The actual test files are prefixed with `test_` and `stress_test_`.

## Setup for local stress test runs

```cmd
(env) ~/azure-servicebus> pip install .
(env) ~/azure-servicebus/stress/scripts> pip install -r dev_requirements.txt
```

## Test commands for local testing

Run the chosen test file with the following command:

```cmd
(env) ~/azure-servicebus/stress/scripts> python test_stress_queues.py
```
