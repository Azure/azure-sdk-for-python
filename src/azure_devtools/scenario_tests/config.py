import configargparse


class RecordMode(object):
    once = 'once'
    all = 'all'


class TestConfig(object):
    def __init__(self, parent_parsers=None, config_file=None):
        parent_parsers = parent_parsers or []
        self.parser = configargparse.ArgumentParser(parents=parent_parsers)
        self.parser.add_argument(
            '-c', '--config', is_config_file=True, default=config_file,
            help='Path to a configuration file in YAML format.'
        )
        self.parser.add_argument(
            '-m', '--record-mode', choices=[RecordMode.once, RecordMode.all],
            default=RecordMode.once,
            env_var='AZURE_TESTS_RECORD_MODE',
            help='Test recording mode.'
        )
        self.args = self.parser.parse_args([])

    @property
    def record_mode(self):
        return self.args.mode