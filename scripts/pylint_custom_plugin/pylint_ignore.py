import re
from pylint.utils import utils


class PylintIgnorePaths:
    def __init__(self):
        self.paths = [r"sdk\\storage\\.*\\_shared\\models.py", r"sdk\\storage\\.*\\_models.py", r"sdk\\storage\\.*\\_lease.py", r"sdk\\storage\\.*\\.*client.*"]
        self.store_expand_modules = utils.expand_modules
        utils.expand_modules = self.filter_expand_modules
    
    def filter_expand_modules(self, *args, **kwargs):
        result, errors = self.store_expand_modules(*args, **kwargs)
        result = list(filter(self.keep_item,result))
        return result, errors
    
    def keep_item(self,item):
        for path in self.paths:
            if re.match(path, item["path"]):
                return False
    
        return True