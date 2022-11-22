# Background

For the coming new package, here is the typical scenario that customer may use:

```python

def my_call_back1(...):
    ...

def my_call_back2(...):
    ...

...

client.add_call_back("group-message", my_call_back1)

client.start()
client.send_to_group(...)

client.add_call_back("group-message", my_call_back2)

...
client.stop()

```

In this scenario, there are the following characteristics:

(1) When customers start the client, client shall be able to receive message from server and call back the related function which customers register.

(2) Customer can still register callback function after client start

(3) After client stop, client can't receive message from server

With the scenario, we need to solve the 2 questions:

1. How can we make full-duplex communication based on websocket
2. Which open-source package shall we use? [websocket-client](https://github.com/websocket-client/websocket-client) vs [websockets](https://github.com/aaugustin/websockets)

# 1. How can we make full-duplex communication based on websocket
I think we need to **make new thread or process** when client start so new thread or process can listen to message from server and trigger callback function registered. Even if thread in Python is "fake" because of GIL, I think thread is better for the following reasons:
- process cost more resource
- because of (2), we need to think about communication between two process about new registered callback function after client start while thread not.

Maybe there is other solution that we don't need to maintain thread or process by ourselves?

# 2. Which open-source package shall we use? [websocket-client](https://github.com/websocket-client/websocket-client) vs [websockets](https://github.com/aaugustin/websockets)
websockets is more popular compared with websocket-client. However websockets only support async API, and asyncio in python is not thread safe. If we want to support sync API and adopt thread solution, maybe websocket-client is better choice