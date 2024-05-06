# WebPubSub Client Stress Tests

This doc shows how to run stress test.

## Setup for local stress test runs

```cmd
(env) ~/azure-messaging-webpubsubclient> pip install .
(env) ~/azure-messaging-webpubsubclient> pip install -r dev_requirements.txt
```

## Test commands for local testing

Run the chosen test file with the following command:

```cmd
(env) ~/azure-messaging-webpubsubclient/stress> python stress_base_async.py
```

You can also add `--help` in command to see the arguments for stress test:

```cmd
(env) ~/azure-messaging-webpubsubclient/stress> python stress_base_async.py --help
```
