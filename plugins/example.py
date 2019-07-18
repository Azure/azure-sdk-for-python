""" This is an example of a pylint-clean client
"""

class MyExampleClient:
    """ A simple, canonical client
    """

    def __init__(self, base_url):
        """ This constructor follows the canonical pattern.

        - It has a configuration parameter.
        """

    def create_configuration(self):
        """ All methods should allow for a configuration instance to be created.
        """

    def get_thing(self, name):
        # type: (str) -> Thing
        """ Getting a single instance should include a required parameter

        - The first positional parameter should be a name or some other identifying
        attribute of the `thing`.
        """

    def list_things(self):
        """ Getting a list of instances should not include any required parameters.
        """

    def download_things(self, zero, one, two, three, four, five=9, six=4, **kwargs):
        """
        stuff
        :return:
        """

    def check_if_exists(self):
        """
        checking if it exists
        :return:
        """

    def _ignore_me(self):
        """dfd"""
