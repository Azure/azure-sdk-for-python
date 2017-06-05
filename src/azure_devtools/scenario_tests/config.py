import configargparse

from .const import ENV_LIVE_TEST


class TestConfig(object):
    def __init__(self, parent_parsers=None, config_file=None):
        parent_parsers = parent_parsers or []
        self.parser = configargparse.ArgumentParser(parents=parent_parsers)
        self.parser.add_argument(
            '-c', '--config', is_config_file=True, default=config_file,
            help='Path to a configuration file in YAML format.'
        )
        self.parser.add_argument(
            '-l', '--live-mode', action='store_true', dest='live_mode',
            env_var=ENV_LIVE_TEST,
            help='Activate "live" recording mode for tests.'
        )
        self.args = self.parser.parse_args([])

    @property
    def record_mode(self):
        return self.args.live_mode