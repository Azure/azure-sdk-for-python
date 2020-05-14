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

def combine_requirements(requirements):
    name = requirements[0].project_name
    specs = []
    for req in requirements:
        if len(req.specs) == 0:
            continue

        specs.extend([s[0] + s[1] for s in req.specs])

    return name + ",".join(specs)

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

    dependencies = get_dependencies(package_names)

    # It may be the case that packages have multiple sets of dependency
    # requirements, for example:
    # Package A requires Foo>=1.0.0,<2.0.0
    # Package B requires Foo>=1.0.0,<1.2.3
    # This combines all required versions into one string for pip to resolve
    # Output: Foo>=1.0.0,<2.0.0,>=1.0.0,<1.2.3
    # Pip parses this value using the Requirement object (https://setuptools.readthedocs.io/en/latest/pkg_resources.html#requirement-objects)
    # According to https://packaging.python.org/glossary/#term-requirement-specifier
    grouped_dependencies = {}
    for dep in dependencies:
        if dep.key in grouped_dependencies:
            grouped_dependencies[dep.key].append(dep)
        else:
            grouped_dependencies[dep.key] = [dep]

    final_dependencies = [combine_requirements(r) for r in grouped_dependencies.values()]

    print("\n".join(final_dependencies))
