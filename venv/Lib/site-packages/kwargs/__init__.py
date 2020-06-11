#pylint: disable=too-few-public-methods
""" Kwargs is the only True python micro-framework that doesn't limit your creativity™. """

def run(callback, *args, **kwargs):
    """ Alias for App.run """
    return callback(*args, **kwargs)


class App(object):
    """ App represents Kwargs application instance. """

    def __init__(self, callback):
        self.callback = callback

    def run(self, *args, **kwargs):
        """ Exexutes callback function provided in __init__ with given parameters """
        return run(self.callback, *args, **kwargs)
