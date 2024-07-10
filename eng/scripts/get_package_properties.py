import argparse
import glob
import os
import re

from ci_tools.parsing import ParsedSetup

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

def dump_setup(path: str) -> None:
    try:
        parsed = ParsedSetup.from_path(path)
        print(
            "{0} {1} {2} {3}".format(
                parsed.name, parsed.version, parsed.is_new_sdk, os.path.dirname(parsed.setup_filename)
            )
        )
    except:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get package version details from the repo")
    parser.add_argument("-s", "--search_path", required=False, help="The scope of the search. Usually a service directory path sdk/X.")
    parser.add_argument("-p", "--packages", required=False, help="The specific package names to search for. Comma separated list.")
    args = parser.parse_args()

    if args.search_path:
        # Use abspath for the os.walk because if setup parsing fails it often changes cwd which throws off the relative walk
        for root, dirs, files in os.walk(os.path.abspath(args.search_path)):
            if re.search(r"sdk[\\/][^\\/]+[\\/][^\\/]+$", root):
                if "setup.py" in files:
                    dump_setup(root)
    elif args.packages:
        for pkg in [pkg.strip() for pkg in args.packages.split(",")]:
            pkg_search = os.path.join(root_dir, "sdk", "*", pkg, "setup.py")
            globbed = glob.glob(pkg_search)

            if globbed:
                for match in globbed:
                    dump_setup(match)
    else:
        raise ValueError("Must provide either a search path or a package name list.")