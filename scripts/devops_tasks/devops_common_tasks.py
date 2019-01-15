import glob
from pathlib import Path
from subprocess import check_call, CalledProcessError
import os

def process_glob_string(glob_string, target_root_dir):
    individual_globs = glob_string.split(',')
    collected_top_level_directories = []

    for glob_string in individual_globs:
        globbed = glob.glob(os.path.join(target_root_dir, glob_string, 'setup.py'))
        collected_top_level_directories.extend([os.path.dirname(p) for p in globbed])

    # dedup, in case we have double coverage from the glob strings. Example: "azure-mgmt-keyvault,azure-mgmt-*"
    return list(set(collected_top_level_directories))

def run_check_call(command_array, working_directory):
    print('Command Array: {0}, Target Working Directory: {1}'.format(command_array, working_directory))
    try:
        check_call(command_array, cwd = working_directory)
    except CalledProcessError as err:
        print(err) #, file = sys.stderr
        sys.exit(1)