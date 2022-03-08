import logging


class RunConfiguration:
    def __init__(self, *args, **kwargs):
        self.log_level = kwargs.get("log_level", logging.INFO)
        configure_logging(args)
        pass

    def initialize_run(self, customizations={}):
        pass

    def configure_logging(self, args):
        pass

    def resolve_repo_root(self, root_arg):
        pass

    def __str__(self):
        return "Implement me!"
