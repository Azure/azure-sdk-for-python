import configargparse


class TestConfig(object):
    def __init__(self, parent_parsers=None, config_file=None):
        parent_parsers = parent_parsers or []
        self.parser = configargparse.ArgumentParser(parents=parent_parsers)
        self.parser.add_argument(
            '-c', '--config', is_config_file=True, default=config_file,
            help='Path to a configuration file in YAML format.'
        )
        self.parser.add_argument(
            '-m', '--mode', choices=['playback', 'live', 'record'], default='playback',
            env_var='AZURE_TESTS_RECORDING_MODE',
            help='Test recording mode.'
        )
        self.args = configargparse.Namespace()

    def parse_args(self):
        self.args = self.parser.parse_args()