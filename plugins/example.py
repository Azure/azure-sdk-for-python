# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

""" This is an example to use for quick pylint tests
"""


class MyExampleClient(object):
    """ A simple, canonical client
    """

    def __init__(self, base_url, credential, **kwargs):
        """ This constructor follows the canonical pattern.
        """

    @staticmethod
    def create_configuration(param): # pylint: disable=client-method-missing-kwargs
        """ All methods should allow for a configuration instance to be created.
        """

    async def get_thing(self, name):
        # type: (str) -> Thing
        """ Getting a single instance should include a required parameter

        - The first positional parameter should be a name or some other identifying
        attribute of the `thing`.
        """

    def list_things(self): # pylint: disable=client-method-missing-tracing-decorator
        """ Getting a list of instances should not include any required parameters.
        """

    def check_if_exists(self):
        """Checking if something exists
        """

    def _ignore_me(self):
        """Ignore this internal method
        """

    def put_thing(self):
        """Not an approved name prefix.
        """


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
#     def put_thing(self):
#         """Not an approved name prefix.
#         """
