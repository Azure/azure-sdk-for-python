#!/usr/bin/env python
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
from typing import List, Set, Dict, Tuple, Any

try:
    from collections import Sized
except:
    from collections.abc import Sized

from pkg_resources import Requirement
from packaging.specifiers import SpecifierSet, Version
from ci_tools.variables import discover_repo_root
from ci_tools.functions import discover_targeted_packages
from ci_tools.parsing import ParsedSetup, parse_require

from pypi_tools.pypi import PyPIClient

try:
    from jinja2 import Environment, FileSystemLoader
except:
    pass  # we only technically require this when outputting the rendered report


def get_known_versions(package_name: str) -> List[str]:
    client = PyPIClient()
    return client.get_ordered_versions(package_name)


def report_should_skip_lib(lib_name: str) -> bool:
    return "-nspkg" in lib_name


def dump_should_skip_lib(lib_name: str) -> bool:
    return "-mgmt" in lib_name or not lib_name.startswith("azure")


def locate_wheels(base_dir: str) -> List[str]:
    wheels = glob.glob(os.path.join(base_dir, "*.whl"))
    return sorted(wheels)


def record_dep(dependencies: Dict[str, Dict[str, Any]], req_name: str, spec: str, lib_name: str) -> None:
    if req_name not in dependencies:
        dependencies[req_name] = {}
    if spec not in dependencies[req_name]:
        dependencies[req_name][spec] = []
    dependencies[req_name][spec].append(lib_name)


def get_lib_deps(base_dir: str) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    packages = {}
    dependencies = {}
    for lib_dir in discover_targeted_packages("azure*", base_dir):
        try:
            setup_path = os.path.join(lib_dir, "setup.py")
            parsed = ParsedSetup.from_path(setup_path)
            lib_name, version, requires = parsed.name, parsed.version, parsed.requires

            packages[lib_name] = {"version": version, "source": lib_dir, "deps": []}

            for req in requires:
                req_obj = parse_require(req)
                req_name = req_obj.key
                spec = req_obj.specifier if len(req_obj.specifier) else None
                if spec is None:
                    spec = ""

                packages[lib_name]["deps"].append({"name": req_name, "version": str(spec)})
                record_dep(dependencies, req_name, str(spec), lib_name)
        except:
            print("Failed to parse %s" % (setup_path))
    return packages, dependencies


def get_wheel_deps(wheel_dir: str) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
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
                    req_obj = parse_require(req)

                    req_name = req_obj.key
                    spec = req_obj.specifier if len(req_obj.specifier) else None
                    if spec is None:
                        spec = ""

                    packages[lib_name]["deps"].append({"name": req_name, "version": str(spec)})
                    record_dep(dependencies, req_name, str(spec), lib_name)
        except:
            print("Failed to parse METADATA from %s" % (whl_path))
    return packages, dependencies


def dict_compare(d1: Dict[Any, Any], d2: Dict[Any, Any]) -> Tuple[Set[Any], Set[Any], Dict[Any, Tuple]]:
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o: (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    return added, removed, modified


def render_report(output_path: str, report_context: Dict[str, any]) -> None:
    env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.realpath(__file__))))
    template = env.get_template("deps.html.j2")
    with io.open(output_path, "w", encoding="utf-8") as output:
        output.write(template.render(report_context))


def get_dependent_packages(data_pkgs) -> Set[str]:
    # Get unique set of Azure SDK packages that are added as required package
    deps = []
    for v in data_pkgs.values():
        deps.extend([dep["name"] for dep in v["deps"] if not dump_should_skip_lib(dep["name"])])
    return set(deps)


def dump_packages(data_pkgs: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    dump_data = {}
    unique_dependent_packages = get_dependent_packages(data_pkgs)
    for p_name, p_data in data_pkgs.items():
        p_id = p_name + ":" + p_data["version"]
        dep = [p for p in p_data["deps"] if not dump_should_skip_lib(p["name"])]
        # Add package if it requires other azure sdk package or if it is added as required by other sdk package
        if len(dep) > 0 or p_name in unique_dependent_packages:
            dump_data[p_id] = {"name": p_name, "version": p_data["version"], "type": "internal", "deps": dep}
    return dump_data


def resolve_lib_deps(dump_data: Dict[str, Dict[str, Any]], data_pkgs: Dict[str, Dict[str, Any]], pkg_id: str) -> None:
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


def pluralize(data: Sized, singular: str, plural: str) -> str:
    if len(data) == 1 or data is None:
        return singular
    else:
        return plural


def analyze_dependencies() -> None:
    base_dir = discover_repo_root()

    parser = argparse.ArgumentParser(
        description="""\
    Analyze dependencies in Python packages. First, all declared dependencies
    and the libraries that declare them will be discovered (visible with
    --verbose). Next, all declared dependency version specs will be analyzed to
    ensure that none of requirements conflict with any other package in the repo. Finally, all declared dependency
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

    incompatible, known_reqs, new_reqs, missing_reqs = [], [], [], []
    exitcode = 0
    frozen_filename = os.path.join(base_dir, "shared_requirements.txt")

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

    ## verify dependencies
    for package in dependencies:
        known_reqs.append(package)
        speclist = dependencies[package].keys()
        dep_versions = get_known_versions(package)

        if package.startswith("azure"):
            # include local version if present
            if package in packages:
                dep_versions.append(Version(packages[package]["version"]))

        remaining_dep_versions = list(dep_versions)

        for spec in speclist:
            if not spec:
                # package with no specifier means that any specifier will match.
                continue
            spec = SpecifierSet(spec)

            remaining_dep_versions = [
                version for version in remaining_dep_versions if spec.contains(str(version), prereleases=True)
            ]

            if not remaining_dep_versions:
                exitcode = 1
                incompatible.append(package)

                if args.verbose:
                    print(
                        f"{package} is required in an irreconcilable combination. No available versions can be found to match the following combination of specifiers:"
                    )
                    for specifier in sorted(dependencies[package].keys(), key=lambda x: len(x)):
                        if specifier:
                            print(
                                f"{dependencies[package][specifier]} {pluralize(dependencies[package][specifier], 'takes', 'take')} a dependency on specifier {specifier}"
                            )
                    print(f'Resolve conflicts in reqs for "{package}" and re-run.')

    # verify requirements in shared_requirements.txt
    if os.path.exists(frozen_filename):
        with open(frozen_filename, "r") as f:
            frozen_reqs = set([line.strip() for line in f.readlines()])

        discovered_reqs = set(dependencies.keys())
        # packages that are part of the dependencies and not yet in the shared_requirement.txt
        new_reqs = discovered_reqs.difference(frozen_reqs)
        # packages that are in the frozen list and no longer part of the discovered dependencies
        missing_reqs = frozen_reqs.difference(discovered_reqs)

        if new_reqs:
            print(
                f"Unknown {pluralize(new_reqs, 'dependency', 'dependencies')} found that are not present in shared_requirements.txt. Use --verbose for details."
            )
            if args.verbose:
                print(f"Unknown {pluralize(new_reqs, 'dependency', 'dependencies')}: {list(new_reqs)}")
            exitcode = 1
    else:
        new_reqs = set(dependencies.keys())
        print("No shared_requirements.txt file can be located to compare against existing.")

    if exitcode == 1:
        if not args.verbose:
            print(
                "\nIncompatible dependency versions detected in libraries, run this script with --verbose for details."
            )
    else:
        print("\nAll library dependencies verified, no incompatible versions detected.")

    if args.freeze:
        if incompatible:
            print(
                "Unable to freeze requirements due to incompatible specifier combination. Re-run with --verbose or see details above."
            )
        else:
            frozen_reqs = list(dependencies.keys())
            with open(frozen_filename, "w") as f:
                f.writelines("\n".join(frozen_reqs))

    if args.out:
        external = [k for k in dependencies if k not in packages and not k.startswith("azure")]

        complete_dir = os.path.abspath(args.out)
        report_dir = os.path.dirname(complete_dir)
        os.makedirs(report_dir, exist_ok=True)

        def display_order(k):
            if k in incompatible:
                return "a" + k if k in external else "b" + k
            else:
                return "c" + k if k in external else "d" + k

        render_report(
            args.out,
            {
                "curtime": datetime.utcnow(),
                "dependencies": dependencies,  # dictionary that contains dependency packages and the specifiers each packages takes on them
                "env": os.environ,
                "external": external,  # list of requirements that are external
                "known_reqs": known_reqs,  # flat list of requirements that we know of
                "incompatible": incompatible,  # list of packages that caused compatibility errors
                "missing_reqs": missing_reqs,  # list of packages that are in the shared_requirements file and no longer taken as dependency
                "new_reqs": new_reqs,  # list of requirements that are new and not yet in the shared_requirements file
                "ordered_deps": sorted(
                    dependencies.keys(), key=display_order
                ),  # dependencies sorted so that external / error are on top
                "packages": packages,  # dictionary of packages that are in the repo
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
