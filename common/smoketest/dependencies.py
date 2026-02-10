import argparse

import importlib.metadata as importlib_metadata

from packaging.requirements import Requirement

try:
    # pip < 20
    from pip._internal.req import parse_requirements
    from pip._internal.download import PipSession
except:
    # pip >= 20
    from pip._internal.req import parse_requirements
    from pip._internal.network.session import PipSession


def combine_requirements(requirements):
    name = requirements[0].name  # packaging.requirements.Requirement uses 'name' instead of 'project_name'
    specs = []
    for req in requirements:
        if len(req.specifier) == 0:  # packaging.requirements.Requirement uses 'specifier' instead of 'specs'
            continue

        # Convert specifier to the expected format
        specs.extend([str(spec) for spec in req.specifier])

    return name + ",".join(specs)


def get_dependencies(packages):
    requirements = []
    for package in packages:
        try:
            # Get the distribution for this package
            package_info = importlib_metadata.distribution(package)

            # Get requirements and process them like pkg_resources did
            if package_info.requires:
                for req_str in package_info.requires:
                    # Parse the requirement string
                    req = Requirement(req_str)

                    # Apply the same filtering as the original code:
                    # include requirements where marker is None or evaluates to True
                    if req.marker is None or req.marker.evaluate():
                        requirements.append(req)
        except importlib_metadata.PackageNotFoundError:
            # Package not found, skip it (similar to how pkg_resources would handle missing packages)
            continue
        except Exception:
            # Skip packages that can't be processed
            continue

    return requirements


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List dependencies for a given requirements.txt file")

    parser.add_argument(
        "-r",
        "--requirements",
        dest="requirements_file",
        help="File containing list of packages for which to find dependencies",
        required=True,
    )

    args = parser.parse_args()
    # Get package names from requirements.txt
    requirements = parse_requirements(args.requirements_file, session=PipSession())

    # Handle different pip versions - extract package names
    package_names = []
    for item in requirements:
        if hasattr(item, "requirement"):
            # Parse the requirement string to get the name
            req_str = item.requirement
            if isinstance(req_str, str):
                # Parse the requirement string using packaging.requirements
                try:
                    req = Requirement(req_str)
                    package_names.append(req.name)
                except Exception:
                    # If parsing fails, try to extract name directly
                    name = req_str.split("==")[0].split(">=")[0].split("<=")[0].split(">")[0].split("<")[0].strip()
                    package_names.append(name)
            else:
                package_names.append(req_str.name)
        elif hasattr(item, "req"):
            # Older pip versions
            package_names.append(item.req.name)
        else:
            # Try to get name from the object directly
            try:
                package_names.append(item.name)
            except AttributeError:
                # Skip items we can't parse
                continue

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
        # Use 'name' instead of 'key' for packaging.requirements.Requirement
        dep_name = dep.name
        if dep_name in grouped_dependencies:
            grouped_dependencies[dep_name].append(dep)
        else:
            grouped_dependencies[dep_name] = [dep]

    final_dependencies = [combine_requirements(r) for r in grouped_dependencies.values()]

    print("\n".join(final_dependencies))
