from devops_common_tasks import *


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
    targeted_packages = process_glob_string(args.glob_string, root_dir)

    print('This is the sys.version: {}'.format(sys.version))
    run_check_call([args.python_version, '--version', '.')