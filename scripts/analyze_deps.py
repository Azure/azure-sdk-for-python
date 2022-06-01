#!/usr/bin/env python
from __future__ import print_function, unicode_literals
import argparse
import ast
from datetime import datetime
import glob
import io
import json
import os
from pkg_resources import Requirement
import re
import sys
import textwrap

# Todo: This should use a common omit logic once ci scripts are refactored into ci_tools
skip_pkgs = [
    'azure-mgmt-documentdb',         # deprecated
    'azure-sdk-for-python',          # top-level package
    'azure-sdk-tools',               # internal tooling for automation
    'azure-servicemanagement-legacy', # legacy (not officially deprecated)
    'azure-common',
    'azure',
    'azure-keyvault',
    'azure-ai-ml'
]

def report_should_skip_lib(lib_name):
    return lib_name in skip_pkgs or lib_name.endswith('-nspkg')

def dump_should_skip_lib(lib_name):
    return report_should_skip_lib(lib_name) or '-mgmt' in lib_name or not lib_name.startswith('azure')

def locate_libs(base_dir):
    packages = [os.path.dirname(p) for p in (glob.glob(os.path.join(base_dir, 'azure*', 'setup.py')) + glob.glob(os.path.join(base_dir, 'sdk/*/azure*', 'setup.py')))]
    return sorted(packages)

def locate_wheels(base_dir):
    wheels = glob.glob(os.path.join(base_dir, '*.whl'))
    return sorted(wheels)

def parse_req(req):
    try:
        req_object = Requirement.parse(req.split(";")[0])
        req_name = req_object.key
        spec = str(req_object).replace(req_name, '')
        return (req_name, spec)
    except:
        print('Failed to parse requirement %s' % (req))

def record_dep(dependencies, req_name, spec, lib_name):
    if not req_name in dependencies:
        dependencies[req_name] = {}
    if not spec in dependencies[req_name]:
        dependencies[req_name][spec] = []
    dependencies[req_name][spec].append(lib_name)


def get_lib_deps(base_dir):
    packages = {}
    dependencies = {}
    for lib_dir in locate_libs(base_dir):
        try:
            setup_path = os.path.join(lib_dir, 'setup.py')
            lib_name, version, requires = parse_setup(setup_path)
            
            packages[lib_name] = {
                'version': version,
                'source': lib_dir,
                'deps': []
            }

            for req in requires:
                req_name, spec = parse_req(req)
                packages[lib_name]['deps'].append({
                    'name': req_name,
                    'version': spec
                })
                if not report_should_skip_lib(lib_name):
                    record_dep(dependencies, req_name, spec, lib_name)
        except:
            print('Failed to parse %s' % (setup_path))
    return packages, dependencies

def get_wheel_deps(wheel_dir):
    from wheel.pkginfo import read_pkg_info_bytes
    from wheel.wheelfile import WheelFile

    packages = {}
    dependencies = {}
    for whl_path in locate_wheels(wheel_dir):
        try:
            with WheelFile(whl_path) as whl:
                pkg_info = read_pkg_info_bytes(whl.read(whl.dist_info_path + '/METADATA'))
                lib_name = pkg_info.get('Name')

                packages[lib_name] = {
                    'version': pkg_info.get('Version'),
                    'source': whl_path,
                    'deps': []
                }

                requires = pkg_info.get_all('Requires-Dist')
                for req in requires:
                    req = req.split(';')[0] # Extras conditions appear after a semicolon
                    req = re.sub(r'[\s\(\)]', '', req) # Version specifiers appear in parentheses
                    req_name, spec = parse_req(req)
                    packages[lib_name]['deps'].append({
                        'name': req_name,
                        'version': spec
                    })
                    if not report_should_skip_lib(lib_name):
                        record_dep(dependencies, req_name, spec, lib_name)
        except:
            print('Failed to parse METADATA from %s' % (whl_path))
    return packages, dependencies

def parse_setup(setup_filename):
    mock_setup = textwrap.dedent('''\
    def setup(*args, **kwargs):
        __setup_calls__.append((args, kwargs))
    ''')
    parsed_mock_setup = ast.parse(mock_setup, filename=setup_filename)
    with io.open(setup_filename, 'r', encoding='utf-8-sig') as setup_file:
        parsed = ast.parse(setup_file.read())
        for index, node in enumerate(parsed.body[:]):
            if (
                not isinstance(node, ast.Expr) or
                not isinstance(node.value, ast.Call) or
                not hasattr(node.value.func, 'id') or
                node.value.func.id != 'setup'
            ):
                continue
            parsed.body[index:index] = parsed_mock_setup.body
            break

    fixed = ast.fix_missing_locations(parsed)
    codeobj = compile(fixed, setup_filename, 'exec')
    local_vars = {}
    global_vars = {'__setup_calls__': []}
    current_dir = os.getcwd()
    working_dir = os.path.dirname(setup_filename)
    os.chdir(working_dir)
    exec(codeobj, global_vars, local_vars)
    os.chdir(current_dir)
    _, kwargs = global_vars['__setup_calls__'][0]

    version = kwargs['version']
    name = kwargs['name']
    requires = []
    if 'install_requires' in kwargs:
        requires += kwargs['install_requires']
    if 'extras_require' in kwargs:
        for extra in kwargs['extras_require'].values():
            requires += extra
    return name, version, requires

def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o : (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    return added, removed, modified

def render_report(output_path, report_context):
    env = Environment(
        loader=FileSystemLoader(os.path.dirname(os.path.realpath(__file__)))
    )
    template = env.get_template('deps.html.j2')
    with io.open(output_path, 'w', encoding='utf-8') as output:
        output.write(template.render(report_context))

def get_dependent_packages(data_pkgs):
    # Get unique set of Azure SDK packages that are added as required package
    deps = []
    for v in data_pkgs.values():
        deps.extend([dep['name'] for dep in v['deps'] if not dump_should_skip_lib(dep['name'])])
    return set(deps)

def dump_packages(data_pkgs):
    dump_data = {}
    unique_dependent_packages = get_dependent_packages(data_pkgs)
    for p_name, p_data in data_pkgs.items():
        p_id = p_name + ':' + p_data['version']
        dep = [p for p in p_data['deps'] if not dump_should_skip_lib(p['name'])]
        # Add package if it requires other azure sdk package or if it is added as required by other sdk package
        if len(dep) > 0 or p_name in unique_dependent_packages:
            dump_data[p_id] = {
                'name': p_name,
                'version': p_data['version'],
                'type': 'internal',
                'deps': dep
            }

    return dump_data

def resolve_lib_deps(dump_data, data_pkgs, pkg_id):
    for dep in dump_data[pkg_id]['deps']:
        dep_req = Requirement.parse(dep['name'] + dep['version'])
        if dep['name'] in data_pkgs and data_pkgs[dep['name']]['version'] in dep_req:
            # If the internal package version matches the dependency spec,
            # rewrite the dep version to match the internal package version
            dep['version'] = data_pkgs[dep['name']]['version']
        else:
            dep_id = dep['name'] + ':' + dep['version']
            if not dep_id in dump_data:
                dump_data[dep_id] = {
                    'name': dep['name'],
                    'version': dep['version'],
                    'type': 'internalbinary' if dep['name'] in data_pkgs else 'external',
                    'deps': []
                }

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    parser = argparse.ArgumentParser(description='''\
    Analyze dependencies in Python packages. First, all declared dependencies
    and the libraries that declare them will be discovered (visible with
    --verbose). Next, all declared dependency version specs will be analyzed to
    ensure they are consistent across all libraries. Finally, all declared
    dependency version specs will be compared to the frozen version specs in
    shared_requirements.txt, or if --freeze is provided, all declared dependency
    version specs will be frozen to shared_requirements.txt.
    ''')
    parser.add_argument('--verbose', help='verbose output', action='store_true')
    parser.add_argument('--freeze', help='freeze dependencies after analyzing (otherwise, validate dependencies against frozen list)', action='store_true')
    parser.add_argument('--out', metavar='FILE', help='write HTML-formatted report to FILE')
    parser.add_argument('--dump', metavar='FILE', help='write JSONP-formatted dependency data to FILE')
    parser.add_argument('--wheeldir', metavar='DIR', help='analyze wheels in DIR rather than source packages in this repository')
    args = parser.parse_args()

    if args.out:
        try:
            from jinja2 import Environment, FileSystemLoader
        except:
            print("Jinja2 is required to render the dependency report. Please install with 'pip install Jinja2' to use this option.")
            sys.exit(1)

    if args.wheeldir:
        all_packages, dependencies = get_wheel_deps(args.wheeldir)
    else:
        all_packages, dependencies = get_lib_deps(base_dir)

    packages = {k: v for k,v in all_packages.items() if not report_should_skip_lib(k)}

    if args.verbose:
        print('Packages analyzed')
        print('=================')
        for package in sorted(packages.keys()):
            info = packages[package]
            print("%s %s" % (package, info['version']))
            print("  from %s" % (info['source']))

        print('\n\nRequirements discovered')
        print('=======================')
        for requirement in sorted(dependencies.keys()):
            specs = dependencies[requirement]
            libs = []
            print('%s' % (requirement))
            for spec in specs.keys():
                print('%s' % (spec if spec else '(empty)'))
                for lib in specs[spec]:
                    print('  * %s' % (lib))
            print('')

    inconsistent = []
    for requirement in sorted(dependencies.keys()):
        specs = dependencies[requirement]
        num_specs = len(specs)
        if num_specs == 1:
            continue

        if not inconsistent and args.verbose:
            print('\nInconsistencies detected')
            print('========================')

        inconsistent.append(requirement)
        if args.verbose:
            print("Requirement '%s' has %s unique specifiers:" % (requirement, num_specs))
            for spec in sorted(specs.keys()):
                libs = specs[spec]
                friendly_spec = '(none)' if spec == '' else spec
                print("  '%s'" % (friendly_spec))
                print('  ' + ('-' * (len(friendly_spec) + 2)))
                for lib in sorted(libs):
                    print('    * %s' % (lib))
                print('')

    frozen_filename = os.path.join(base_dir, 'shared_requirements.txt')
    if args.freeze:
        if inconsistent:
            print('Unable to freeze requirements due to incompatible dependency versions')
            sys.exit(1)
        else:
            with io.open(frozen_filename, 'w', encoding='utf-8') as frozen_file:
                for requirement in sorted(dependencies.keys()):
                    spec = list(dependencies[requirement].keys())[0]
                    if spec == '':
                        print("Requirement '%s' being frozen with no version spec" % requirement)
                    frozen_file.write(requirement + spec + '\n')
            print('Current requirements frozen to %s' % (frozen_filename))
            sys.exit(0)

    frozen = {}
    overrides = {}
    override_count = 0
    try:
        with io.open(frozen_filename, 'r', encoding='utf-8-sig') as frozen_file:
            for line in frozen_file:
                if line.startswith('#override'):
                    _, lib_name, req_override = line.split(' ', 2)
                    req_override_name, override_spec = parse_req(req_override)
                    record_dep(overrides, req_override_name, override_spec, lib_name)
                    override_count += 1
                elif not line.startswith('#'):
                    req_name, spec = parse_req(line)
                    frozen[req_name] = [spec]
    except:
        print('Unable to open shared_requirements.txt, shared requirements have not been validated')

    missing_reqs, new_reqs, changed_reqs = {}, {}, {}
    non_overridden_reqs_count = 0
    exitcode = 0
    if frozen:
        flat_deps = {req: sorted(dependencies[req].keys()) for req in dependencies}
        missing_reqs, new_reqs, changed_reqs = dict_compare(frozen, flat_deps)
        if args.verbose and len(overrides) > 0:
            print('\nThe following requirement overrides are in place:')
            for overridden_req in overrides:
                for spec in overrides[overridden_req]:
                    libs = ', '.join(sorted(overrides[overridden_req][spec]))
                    print('  * %s is allowed for %s' % (overridden_req + spec, libs))
        if args.verbose and len(missing_reqs) > 0:
            print('\nThe following requirements are frozen but do not exist in any current library:')
            for missing_req in missing_reqs:
                [spec] = frozen[missing_req]
                print('  * %s' % (missing_req + spec))
        if len(new_reqs) > 0:
            exitcode = 1
            if args.verbose:
                for new_req in new_reqs:
                    for spec in dependencies[new_req]:
                        libs = dependencies[new_req][spec]
                        print("\nRequirement '%s' is declared in the following libraries but has not been frozen:" % (new_req + spec))
                        for lib in libs:
                            print("  * %s" % (lib))
        if len(changed_reqs) > 0:
            for changed_req in changed_reqs:
                frozen_specs, current_specs = changed_reqs[changed_req]
                unmatched_specs = set(current_specs) - set(frozen_specs)
                override_specs = overrides.get(changed_req, [])

                for spec in unmatched_specs:
                    if spec in override_specs:
                        non_overridden_libs = set(dependencies[changed_req][spec]) - set(override_specs[spec])
                    else:
                        non_overridden_libs = dependencies[changed_req][spec]

                    if len(non_overridden_libs) > 0:
                        exitcode = 1
                        non_overridden_reqs_count += 1
                        if args.verbose:
                            print("\nThe following libraries declare requirement '%s' which does not match the frozen requirement '%s':" % (changed_req + spec, changed_req + frozen_specs[0]))
                            for lib in non_overridden_libs:
                                print("  * %s" % (lib))
        if exitcode == 0:
            if args.verbose:
                print('')
            print('All library dependencies validated against frozen requirements')
        elif not args.verbose:
            print('Library dependencies do not match frozen requirements, run this script with --verbose for details')
    elif inconsistent:
        exitcode = 1
    
    if exitcode == 1:
        if not args.verbose:
            print('\nIncompatible dependency versions detected in libraries, run this script with --verbose for details')
    else:
        print('\nAll library dependencies verified, no incompatible versions detected')

    if args.out:
        external = [k for k in dependencies if k not in packages and not report_should_skip_lib(k)]
        def display_order(k):
            if k in inconsistent:
                return 'a' + k if k in external else 'b' + k
            else:
                return 'c' + k if k in external else 'd' + k

        render_report(args.out, {
            'changed_reqs': changed_reqs,
            'curtime': datetime.utcnow(),
            'dependencies': dependencies,
            'env': os.environ,
            'external': external,
            'frozen': frozen,
            'inconsistent': inconsistent,
            'missing_reqs': missing_reqs,
            'new_reqs': new_reqs,
            'non_overridden_reqs_count': non_overridden_reqs_count,
            'ordered_deps': sorted(dependencies.keys(), key=display_order),
            'override_count': override_count,
            'overrides': overrides,
            'packages': packages,
            'repo_name': 'azure-sdk-for-python'
        })

    if args.dump:
        data_pkgs = {k: v for k, v in all_packages.items() if not dump_should_skip_lib(k)}
        dump_data = dump_packages(data_pkgs)
        pkg_ids = [k for k in dump_data.keys()]
        for pkg_id in pkg_ids:
            resolve_lib_deps(dump_data, data_pkgs, pkg_id)
        with io.open(f"{args.dump}/data.js", 'w', encoding='utf-8') as dump_file:
            dump_file.write('const data = ' + json.dumps(dump_data) + ';')
        with io.open(f"{args.dump}/arcdata.json", 'w', encoding='utf-8') as dump_file:
            dump_file.write(json.dumps(dump_data))

    sys.exit(exitcode)
