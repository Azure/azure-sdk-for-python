import argparse
import sys
import glob
import os
import re

from ci_tools.parsing import ParsedSetup

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get package version details from the repo')
    parser.add_argument('-s', '--search_path', required=True, help='The scope of the search')
    args = parser.parse_args()

    # Use abspath for the os.walk because if setup parsing fails it often changes cwd which throws off the relative walk
    for root, dirs, files in os.walk(os.path.abspath(args.search_path)):
        if re.search(r"sdk[\\/][^\\/]+[\\/][^\\/]+$", root):
            if "setup.py" in files:
                try:
                    parsed = ParsedSetup.from_path(root)
                    print("{0} {1} {2} {3}".format(parsed.name, parsed.version, parsed.is_new_sdk, parsed.setup_filename))
                except:
                    # Skip setup.py if the package cannot be parsed
                    pass