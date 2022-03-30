import re
from pylint.utils import utils


class PylintIgnorePaths:
    def __init__(self):
        
        self.paths = [r"sdk\\storage\\.*\\_shared\\models.py", r"sdk\\storage\\.*\\_models.py", r"sdk\\storage\\.*\\_lease.py", r"sdk\\storage\\.*\\.*client.*"]
        self.original_expand_modules = utils.expand_modules
        utils.expand_modules = self.patched_expand

    def patched_expand(self, *args, **kwargs):
        result, errors = self.original_expand_modules(*args, **kwargs)

        def keep_item(item):
            for path in self.paths:
                if re.match(path, item['path']):
                    return False

            return True

        result = list(filter(keep_item, result))

        return result, errors