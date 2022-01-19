import importlib
import pkg_resources

if __name__ == '__main__':
    packages = [str(d).split(" ")[0] for d in pkg_resources.working_set if str(d).startswith('azure')]
    for pkg in packages:
        importlib.import_module(pkg.replace('-', '.'))
