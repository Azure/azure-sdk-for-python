""" This is an example to use for quick pylint tests
"""


class MyExampleClient(object):
    """ A simple, canonical client
    """

    def __init__(self, base_url):
        """ This constructor follows the canonical pattern.
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

    def check_if_exists(self):
        """Checking if something exists
        """

    def _ignore_me(self):
        """Ignore this internal method
        """

    def put_thing(self):
        """Not an approved name prefix.
        """