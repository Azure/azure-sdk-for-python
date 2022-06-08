import argparse
import os
import logging
import pdb
from subprocess import CalledProcessError, check_call

from common_tasks import process_glob_string, filter_packages_by_compatibility_override

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description="Invoke apistubgenerator against a set of packages. Assumes that dependencies present in eng/apiview_reqs.txt have been installed."
  )

  parser.add_argument(
      "glob_string",
      nargs="?",
      help=(
          "A comma separated list of glob strings that will target the top level directories that contain packages."
          'Examples: All = "azure-*", Single = "azure-keyvault", Targeted Multiple = "azure-keyvault,azure-mgmt-resource"'
      ),
  )

  parser.add_argument(
      "--service",
      help=(
          "Name of service directory (under sdk/) to test."
          "Example: --service applicationinsights"
      ),
  )

  args = parser.parse_args()

  # We need to support both CI builds of everything and individual service
  # folders. This logic allows us to do both.
  if args.service:
      service_dir = os.path.join("sdk", args.service)
      target_dir = os.path.join(root_dir, service_dir)
  else:
      target_dir = root_dir

  return_code = 0

  targeted_packages = process_glob_string(args.glob_string, target_dir, "", "Omit_management")
  compatible_targeted_packages = filter_packages_by_compatibility_override(targeted_packages)

  if targeted_packages != compatible_targeted_packages:
      logging.info("At least one package incompatible with current platform was detected. Skipping: {}".format(set(targeted_packages) - set(compatible_targeted_packages)))

  for targeted_package in targeted_packages:
    cmds = ["apistubgen", "--pkg-path", targeted_package]
    logging.info("Running apistubgen {}.".format(cmds))
    try:
      check_call(cmds, cwd=args.work_dir)
    except CalledProcessError as e:
      logging.error(e)
      return_code = 1
      
  exit(return_code)
      