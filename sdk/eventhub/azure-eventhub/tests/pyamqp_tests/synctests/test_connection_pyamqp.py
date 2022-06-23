# # Test close performative - detach
# # Test open performative - attach
# # Test Transfer performative - message sent/ received


# import pytest
# from azure.eventhub._pyamqp import SendClient
# from azure.eventhub._pyamqp.authentication import AccessToken, JWTTokenAuth
# from azure.eventhub._pyamqp.sasl import SASLAnonymousCredential
# import asyncio
# import functools
# import socket
# # TEST OPEN PERFORMATIVE BEING SENT TO ME

# # mock an incoming open frame/ performative 


# # if we want to mock an incoming frame, we just assert that it is an open frame by setting the performative, and then see how pyamqp handles that 
# # Create a mock link 

# class MockToken():
#     def get_token():
#         return AccessToken("my_token", 1000)

# def test_incoming_attach_frame():
#     my_send = SendClient("guest:guest@localhost:5672","amqps://guest:guest@localhost:5672", JWTTokenAuth("amqps://guest:guest@localhost:5672","amqps://guest:guest@localhost:5672/",functools.partial(MockToken.get_token, "amqps://guest:guest@rabbitmq3:5672/") ))
#     my_send.open()
#     print("client opened")
