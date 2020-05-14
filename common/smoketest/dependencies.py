import argparse
import pkg_resources

try:
    # pip < 20
    from pip._internal.req import parse_requirements
    from pip._internal.download import PipSession
except:
    # pip >= 20
    from pip._internal.req import parse_requirements
    from pip._internal.network.session import PipSession

def get_freeze_string(requirement):
    output = []
    output.append(requirement.project_name)
    spec_list = [s[0] + s[1] for s in requirement.specs]

    output.extend(','.join(spec_list))

    return ''.join(output)


def get_dependencies(packages):
    requirements = []
    for package in packages:
        package_info = pkg_resources.working_set.by_key[package]

        applicable_requirements = [r for r in package_info.requires() if r.marker is None or r.marker.evaluate()]
        requirements.extend(applicable_requirements)

    return requirements

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="List dependencies for a given requirements.txt file"
    )

    parser.add_argument(
        "-r",
        "--requirements",
        dest="requirements_file",
        help="File containing list of packages for which to find dependencies",
        required=True
    )

    args = parser.parse_args()
    # Get package names from requirements.txt
    requirements = parse_requirements(args.requirements_file, session=PipSession())
    package_names = [item.req.name for item in requirements]

    # Remove existing packages (that came from the public feed) and install
    # from dev feed
    dependencies = get_dependencies(package_names)

    # TODO: Do a better job of merging these that doesn't squash earlier entries
    final_dependencies = {d.key: get_freeze_string(d) for d in dependencies}

    print("\n".join(final_dependencies.values()))
