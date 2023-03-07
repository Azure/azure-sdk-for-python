#!/usr/bin/env python
from __future__ import print_function, unicode_literals
import argparse
import ast
from datetime import datetime
import glob
import io
import json
import os
import re
import sys
import textwrap
from typing import List

from pkg_resources import Requirement
from packaging.specifiers import SpecifierSet
from ci_tools.variables import discover_repo_root
from ci_tools.functions import discover_targeted_packages
from ci_tools.parsing import ParsedSetup, parse_require

from pypi_tools.pypi import PyPIClient

try:
    from jinja2 import Environment, FileSystemLoader
except:
    pass  # we only technically require this when outputting the rendered report

# Todo: This should use a common omit logic once ci scripts are refactored into ci_tools


def get_known_versions(package_name: str, include_local_version: bool = False) -> List[str]:
    client = PyPIClient()
    return client.get_ordered_versions(package_name)


def report_should_skip_lib(lib_name: str) -> bool:
    return "-nspkg" in lib_name


def dump_should_skip_lib(lib_name: str) -> bool:
    return "-mgmt" in lib_name or not lib_name.startswith("azure")


def locate_wheels(base_dir: str) -> str:
    wheels = glob.glob(os.path.join(base_dir, "*.whl"))
    return sorted(wheels)


def record_dep(dependencies, req_name, spec, lib_name):
    if not req_name in dependencies:
        dependencies[req_name] = {}
    if not spec in dependencies[req_name]:
        dependencies[req_name][spec] = []
    dependencies[req_name][spec].append(lib_name)


def get_lib_deps(base_dir):
    packages = {}
    dependencies = {}
    for lib_dir in discover_targeted_packages("azure*", base_dir):
        try:
            setup_path = os.path.join(lib_dir, "setup.py")
            parsed = ParsedSetup.from_path(setup_path)
            lib_name, version, requires = parsed.name, parsed.version, parsed.requires

            packages[lib_name] = {"version": version, "source": lib_dir, "deps": []}

            for req in requires:
                req_name, spec = parse_require(req)
                if spec is None:
                    spec = ""

                packages[lib_name]["deps"].append({"name": req_name, "version": str(spec)})
                record_dep(dependencies, req_name, str(spec), lib_name)
        except:
            print("Failed to parse %s" % (setup_path))
    return packages, dependencies


def get_wheel_deps(wheel_dir):
    from wheel.pkginfo import read_pkg_info_bytes
    from wheel.wheelfile import WheelFile

    packages = {}
    dependencies = {}
    for whl_path in locate_wheels(wheel_dir):
        try:
            with WheelFile(whl_path) as whl:
                pkg_info = read_pkg_info_bytes(whl.read(whl.dist_info_path + "/METADATA"))
                lib_name = pkg_info.get("Name")

                packages[lib_name] = {"version": pkg_info.get("Version"), "source": whl_path, "deps": []}

                requires = pkg_info.get_all("Requires-Dist")
                for req in requires:
                    req = req.split(";")[0]  # Extras conditions appear after a semicolon
                    req = re.sub(r"[\s\(\)]", "", req)  # Version specifiers appear in parentheses
                    req_name, spec = parse_require(req)
                    if spec is None:
                        spec = ""

                    # spec = spec if spec is not None else ''
                    # req_name2, spec2 = parse_req(req)

                    # if(req_name != req_name2):
                    #     breakpoint()

                    # if(str(spec) != spec2):
                    #     breakpoint()

                    packages[lib_name]["deps"].append({"name": req_name, "version": str(spec)})
                    record_dep(dependencies, req_name, str(spec), lib_name)
        except:
            print("Failed to parse METADATA from %s" % (whl_path))
    return packages, dependencies


def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o: (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    return added, removed, modified


def render_report(output_path, report_context):
    env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.realpath(__file__))))
    template = env.get_template("deps.html.j2")
    with io.open(output_path, "w", encoding="utf-8") as output:
        output.write(template.render(report_context))


def get_dependent_packages(data_pkgs):
    # Get unique set of Azure SDK packages that are added as required package
    deps = []
    for v in data_pkgs.values():
        deps.extend([dep["name"] for dep in v["deps"] if not dump_should_skip_lib(dep["name"])])
    return set(deps)


def dump_packages(data_pkgs):
    dump_data = {}
    unique_dependent_packages = get_dependent_packages(data_pkgs)
    for p_name, p_data in data_pkgs.items():
        p_id = p_name + ":" + p_data["version"]
        dep = [p for p in p_data["deps"] if not dump_should_skip_lib(p["name"])]
        # Add package if it requires other azure sdk package or if it is added as required by other sdk package
        if len(dep) > 0 or p_name in unique_dependent_packages:
            dump_data[p_id] = {"name": p_name, "version": p_data["version"], "type": "internal", "deps": dep}

    return dump_data


def resolve_lib_deps(dump_data, data_pkgs, pkg_id):
    for dep in dump_data[pkg_id]["deps"]:
        dep_req = Requirement.parse(dep["name"] + dep["version"])
        if dep["name"] in data_pkgs and data_pkgs[dep["name"]]["version"] in dep_req:
            # If the internal package version matches the dependency spec,
            # rewrite the dep version to match the internal package version
            dep["version"] = data_pkgs[dep["name"]]["version"]
        else:
            dep_id = dep["name"] + ":" + dep["version"]
            if not dep_id in dump_data:
                dump_data[dep_id] = {
                    "name": dep["name"],
                    "version": dep["version"],
                    "type": "internalbinary" if dep["name"] in data_pkgs else "external",
                    "deps": [],
                }


def analyze_dependencies():
    base_dir = discover_repo_root()

    parser = argparse.ArgumentParser(
        description="""\
    Analyze dependencies in Python packages. First, all declared dependencies
    and the libraries that declare them will be discovered (visible with
    --verbose). Next, all declared dependency version specs will be analyzed to
    ensure that none of requirements are unknown. Finally, all declared dependency
    version specs will be frozen to shared_requirements.txt.
    """
    )
    parser.add_argument("--verbose", help="verbose output", action="store_true")
    parser.add_argument(
        "--freeze",
        help="freeze dependencies after analyzing (otherwise, validate dependencies against frozen list)",
        action="store_true",
    )
    parser.add_argument("--out", metavar="FILE", help="write HTML-formatted report to FILE")
    parser.add_argument("--dump", metavar="FILE", help="write JSONP-formatted dependency data to FILE")
    parser.add_argument(
        "--wheeldir", metavar="DIR", help="analyze wheels in DIR rather than source packages in this repository"
    )
    args = parser.parse_args()

    if args.out:
        try:
            from jinja2 import Environment, FileSystemLoader
        except:
            print(
                "Jinja2 is required to render the dependency report. Please install with 'pip install Jinja2' to use this option."
            )
            sys.exit(1)

    if args.wheeldir:
        all_packages, dependencies = get_wheel_deps(args.wheeldir)
    else:
        all_packages, dependencies = get_lib_deps(base_dir)

    packages = {k: v for k, v in all_packages.items() if not report_should_skip_lib(k)}

    if args.verbose:
        print("Packages analyzed")
        print("=================")
        for package in sorted(packages.keys()):
            info = packages[package]
            print("%s %s" % (package, info["version"]))
            print("  from %s" % (info["source"]))

        print("\n\nRequirements discovered")
        print("=======================")
        for requirement in sorted(dependencies.keys()):
            specs = dependencies[requirement]
            libs = []
            print("%s" % (requirement))
            for spec in specs.keys():
                print("%s" % (spec if spec else "(empty)"))
                for lib in specs[spec]:
                    print("  * %s" % (lib))
            print("")

    frozen_filename = os.path.join(base_dir, "shared_requirements.txt")

    if os.path.exists(frozen_filename):
        with open(frozen_filename, "r") as f:
            frozen_reqs = set([line.strip() for line in f.readlines()])

        discovered_reqs = set(dependencies.keys())
        difference = discovered_reqs.difference(frozen_reqs)
    else:
        frozen_reqs = None
        difference = None

    # todo: do we need to set difference?

    incompatible = []
    missing_reqs, new_reqs, changed_reqs = {}, {}, {}
    non_overridden_reqs_count = 0
    exitcode = 0

    for package in dependencies:
        speclist = dependencies[package].keys()
        dep_versions = get_known_versions(package)  # todo: include latest from repo as well
        remaining_dep_versions = list(dep_versions)

        for spec in speclist:
            if not spec:
                # package with no specifier means that any specifier will match.
                continue
            try:
                spec = SpecifierSet(spec)
            except Exception as ex:
                print(ex)
                breakpoint()

            previous_remaining_dep_versions = list(remaining_dep_versions)
            remaining_dep_versions = [version for version in remaining_dep_versions if str(version) in spec]

            if not remaining_dep_versions:
                exitcode = 1
                incompatible.append(package)

                if args.verbose:
                    print(
                        f"{package} is required in an irreconcilable combination. No available versions can be found to match the following combination of specifiers:"
                    )
                    for specifier in sorted(dependencies[package].keys(), key=lambda x: len(x)):
                        pluralizer = "s" if len(dependencies[package][specifier]) == 1 else ""
                        print(
                            f"{dependencies[package][specifier]} take{pluralizer} a dependency on specifier {specifier}"
                        )
                    print(f'Resolve conflicts in reqs for "{package}" and re-run.')

    # if frozen:
    #     flat_deps = {req: sorted(dependencies[req].keys()) for req in dependencies}
    #     missing_reqs, new_reqs, changed_reqs = dict_compare(frozen, flat_deps)
    #     if args.verbose and len(overrides) > 0:
    #         print('\nThe following requirement overrides are in place:')
    #         for overridden_req in overrides:
    #             for spec in overrides[overridden_req]:
    #                 libs = ', '.join(sorted(overrides[overridden_req][spec]))
    #                 print('  * %s is allowed for %s' % (overridden_req + spec, libs))
    #     if args.verbose and len(missing_reqs) > 0:
    #         print('\nThe following requirements are frozen but do not exist in any current library:')
    #         for missing_req in missing_reqs:
    #             [spec] = frozen[missing_req]
    #             print('  * %s' % (missing_req + spec))
    #     if len(new_reqs) > 0:
    #         exitcode = 1
    #         if args.verbose:
    #             for new_req in new_reqs:
    #                 for spec in dependencies[new_req]:
    #                     libs = dependencies[new_req][spec]
    #                     print("\nRequirement '%s' is declared in the following libraries but has not been frozen:" % (new_req + spec))
    #                     for lib in libs:
    #                         print("  * %s" % (lib))
    #     if len(changed_reqs) > 0:
    #         for changed_req in changed_reqs:
    #             frozen_specs, current_specs = changed_reqs[changed_req]
    #             unmatched_specs = set(current_specs) - set(frozen_specs)
    #             override_specs = overrides.get(changed_req, [])

    #             for spec in unmatched_specs:
    #                 if spec in override_specs:
    #                     non_overridden_libs = set(dependencies[changed_req][spec]) - set(override_specs[spec])
    #                 else:
    #                     non_overridden_libs = dependencies[changed_req][spec]

    #                 if len(non_overridden_libs) > 0:
    #                     exitcode = 1
    #                     non_overridden_reqs_count += 1
    #                     if args.verbose:
    #                         print("\nThe following libraries declare requirement '%s' which does not match the frozen requirement '%s':" % (changed_req + spec, changed_req + frozen_specs[0]))
    #                         for lib in non_overridden_libs:
    #                             print("  * %s" % (lib))
    #     if exitcode == 0:
    #         if args.verbose:
    #             print('')
    #         print('All library dependencies validated against frozen requirements')
    #     elif not args.verbose:
    #         print('Library dependencies do not match frozen requirements, run this script with --verbose for details')
    # elif difference:
    #     exitcode = 1

    if exitcode == 1:
        if not args.verbose:
            print(
                "\nIncompatible dependency versions detected in libraries, run this script with --verbose for details"
            )
    else:
        print("\nAll library dependencies verified, no incompatible versions detected.")

    if args.freeze:
        if incompatible:
            print("Unable to freeze requirements due to incompatible new specifier.")
        else:
            with io.open(frozen_filename, "w", encoding="utf-8") as frozen_file:
                for requirement in sorted(dependencies.keys()):
                    frozen_file.write(requirement + "\n")
            print("Current known external deps set to %s" % (frozen_filename))
            sys.exit(0)

    frozen = {}

    # if there are
    # try:
    #     with io.open(frozen_filename, 'r', encoding='utf-8-sig') as frozen_file:
    #         for line in frozen_file:
    #             if line.startswith('#override'):
    #                 _, lib_name, req_override = line.split(' ', 2)
    #                 req_override_name, override_spec = parse_req(req_override)
    #                 record_dep(overrides, req_override_name, override_spec, lib_name)
    #                 override_count += 1
    #             elif not line.startswith('#'):
    #                 req_name, spec = parse_req(line)
    #                 frozen[req_name] = [spec]
    # except:
    #     print('Unable to open shared_requirements.txt, shared requirements have not been validated')

    if args.out:
        external = [k for k in dependencies if k not in packages]

        def display_order(k):
            if k in {}:
                return "a" + k if k in external else "b" + k
            else:
                return "c" + k if k in external else "d" + k

        render_report(
            args.out,
            {
                "changed_reqs": changed_reqs,
                "curtime": datetime.utcnow(),
                "dependencies": dependencies,
                "env": os.environ,
                "external": external,
                "frozen": frozen,
                "inconsistent": incompatible,  # the list of packages that caused compatibility errors
                "missing_reqs": missing_reqs,
                "new_reqs": new_reqs,
                "non_overridden_reqs_count": non_overridden_reqs_count,
                "ordered_deps": sorted(dependencies.keys(), key=display_order),
                "override_count": 0,
                "overrides": [],
                "packages": packages,
                "repo_name": "azure-sdk-for-python",
            },
        )

    if args.dump:
        data_pkgs = {k: v for k, v in all_packages.items() if not dump_should_skip_lib(k)}
        dump_data = dump_packages(data_pkgs)
        pkg_ids = [k for k in dump_data.keys()]
        for pkg_id in pkg_ids:
            resolve_lib_deps(dump_data, data_pkgs, pkg_id)
        with io.open(f"{args.dump}/data.js", "w", encoding="utf-8") as dump_file:
            dump_file.write("const data = " + json.dumps(dump_data) + ";")
        with io.open(f"{args.dump}/arcdata.json", "w", encoding="utf-8") as dump_file:
            dump_file.write(json.dumps(dump_data))

    sys.exit(exitcode)
