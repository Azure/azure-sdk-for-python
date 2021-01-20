import argparse
import os

def combine_xml_files(dir):
    print("Parsing from {}".format(dir))

    cov_files = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]

    print("Found {} coverage files: {}".format(len(cov_files), cov_files))


print("Combining code coverage files")

parser = argparse.ArgumentParser(
    description="Install Dependencies, Install Packages, Test Azure Packages' Samples, Called from DevOps YAML Pipeline"
)

parser.add_argument(
    "-c",
    "--coverage-directory",
    dest="coverage_directory",
    help="The target directory holding coverage XML files.",
    required=True,
)

print(parser.coverage_directory)

combine_xml_files(parser.coverage_directory)