""" This is an example to use for quick pylint tests
"""

#
# class MyExampleClient(object):
#     """ A simple, canonical client
#     """
#
#     MAX_SIZE = 10
#
#     def __init__(self, base_url, credential, **kwargs):
#         """ This constructor follows the canonical pattern.
#         """
#
#     @classmethod
#     def create_configuration(cls, param):
#         """ All methods should allow for a configuration instance to be created.
#         """
#
#     def get_thing(self, name):
#         # type: (str) -> Thing
#         """ Getting a single instance should include a required parameter
#
#         - The first positional parameter should be a name or some other identifying
#         attribute of the `thing`.
#         """
#
#     def list_things(self):
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

# from azure.core import Configuration
# from azure.core.pipeline.policies import (
#     RedirectPolicy,
#     ProxyPolicy)
#
# @staticmethod
# def create_configuration(**kwargs):
#     # type: (**Any) -> Configuration
#
#     config = Configuration(**kwargs)
#     config.redirect_policy = RedirectPolicy(**kwargs)
#     config.proxy_policy = ProxyPolicy()
#     return config
#
#
# def create_config(credential, api_version=None, **kwargs):
#     # type: (TokenCredential, Optional[str], Mapping[str, Any]) -> Configuration
#     if api_version is None:
#         api_version = KeyVaultClient.DEFAULT_API_VERSION
#     config = KeyVaultClient.get_configuration_class(api_version, aio=False)(credential, **kwargs)
#     config.authentication_policy = ChallengeAuthPolicy(credential)
#     return config