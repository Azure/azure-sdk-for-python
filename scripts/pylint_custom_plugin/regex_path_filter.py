import re
from pylint.utils import utils

class RegexPathFilter:
    def __init__(self):
        self.old_expand_modules = utils.expand_modules
        utils.expand_modules = self.new_expand_modules
    
    def new_expand_modules(self, files_or_modules, black_list, black_list_re, **kwargs):
        modules, errors = self.old_expand_modules(files_or_modules, black_list, black_list_re, **kwargs)
        new_modules = self.filtered(modules)
        return new_modules, errors

    def filtered(self, modules):
        paths = [r"sdk/storage/.*/_shared/models.py", r"sdk/storage/.*/_models.py", r"sdk/storage/.*/.*_lease.*", r"sdk/storage/.*/.*client.*", r"sdk\\storage\\.*\\_shared\\models.py", r"sdk\\storage\\.*\\_models.py", r"sdk\\storage\\.*\\.*_lease.*", r"sdk\\storage\\.*\\.*client.*"]
        reg = re.compile("(%s|%s|%s|%s|%s|%s|%s|%s)" % (paths[0], paths[1], paths[2], paths[3], paths[4], paths[5], paths[6], paths[7]))
        new_modules = []
        for m in modules:
            if not reg.match(m['path']):
                new_modules.append(m)
        return new_modules

