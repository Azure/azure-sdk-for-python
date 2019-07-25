# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

""" This is an example to use for quick pylint tests
"""
from azure.core import HttpResponseError
from azure.core.tracing.decorator import distributed_trace

class MyExampleClient(object):
    """ A simple, canonical client

    .. code-block:: python
        thing = 5
    """

    def __init__(self, base_url, credential, **kwargs):
        """ This constructor follows the canonical pattern.
        """
        self._client = None

    @distributed_trace
    @classmethod
    def create_configuration(
            self, param: str, **kwargs
    ) -> None:  # pylint: disable=client-method-missing-kwargs
        """ All methods should allow for a configuration instance to be created.

        param str param: stuff
        param int **thing: an int

        .. code-block:: python
            thing = 5
        """
        # return self._client.blob.delete(one, two, self.three, four=4)


    @distributed_trace
    def get_thing(self, one, two, three, four):
        """ Getting a single instance should include a required parameter

        - The first positional parameter should be a name or some other identifying
        attribute of the `thing`.
        """

    @distributed_trace_async
    async def __get_key(self, name: str, version: str = None):
        """hel
        .. code-block:: python
            thing = 5
        """
#
# class StorageErrorException(object):
#     pass
    # def list_things(self): # pylint: disable=client-method-missing-tracing-decorator
    #     """ Getting a list of instances should not include any required parameters.
    #     """
    #
    # def check_if_exists(self):
    #     """Checking if something exists
    #     """
    #
    # def _ignore_me(self):
    #     """Ignore this internal method
    #     """
    #
    # def put_thing(self):
    #     """Not an approved name prefix.
    #     """


# class MyExamplefClient(object):
#     """ A simple, canonical client
#     """
#
#     def __init__(self, base_url, credential, **kwargs):
#         """ This constructor follows the canonical pattern.
#         """
#
#     @staticmethod
#     def create_configuration(cls, param):
#         """ All methods should allow for a configuration instance to be created.
#         """
#
#     async def get_thing(self, name):
#         # type: (str) -> Thing
#         """ Getting a single instance should include a required parameter
#
#         - The first positional parameter should be a name or some other identifying
#         attribute of the `thing`.
#         """
#
#     def list_things(self): # pylint: disable=client-method-missing-tracing-decorator
#         """ Getting a list of instances should not include any required parameters.
#         """
#
#     def check_if_exists(self):
#         """Checking if something exists
#         """
#
#     def _ignore_me(self):
#         """Ignore this internal method
#         """
#
# def put_thing():
#     """Not an approved name prefix.
#     """
#     client(one, two, three, four)