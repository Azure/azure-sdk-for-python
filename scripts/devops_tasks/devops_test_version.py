import argparse
import sys

DEFAULT_TARGETED_PROJECTS = ['azure-keyvault']

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
        print(err, file = sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Build Azure Packages, Called from DevOps YAML Pipeline')
    parser.add_argument(
        '-g', 
        '--glob-string', 
        dest = 'glob_string', 
        default = 'azure-keyvault',
        help = 'A comma separated list of glob strings that will target the top level directories that contain packages. Examples: All = "azure-*", Single = "azure-keyvault", Targeted Multiple = "azure-keyvault,azure-mgmt-resource"')

    parser.add_argument(
        '-p',
        '--python-version',
        dest = 'python_version',
        default = 'python',
        help = 'The name of the python that should run the build. This is for usage in special cases like in /.azure-pipelines/specialcase.test.yml. Defaults to "python"')

    args = parser.parse_args()

    here = os.getcwd()

    targeted_packages = process_glob_string(args.glob_string, here)

    print('This is the sys.version: {}'.format(sys.version))
    run_check_call([args.python_version, '--version'], here)