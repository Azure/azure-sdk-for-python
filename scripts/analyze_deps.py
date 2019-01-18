#!/usr/bin/env python
from __future__ import print_function
import argparse
import ast
import glob
import os
import re
import sys
import textwrap

# packages which are skipped in all cases
skip_pkgs = [
    'azure-sdk-for-python',
    'azure-sdk-tools'
]

# packages which are not considered when displaying / generating the list of requirements,
# but which are still considered when looking for requirement version inconsistencies
meta_pkgs = [
    'azure-mgmt',
    'azure'
]

def locate_libs(base_dir):
    packages = [os.path.dirname(p) for p in glob.glob(os.path.join(base_dir, 'azure*', 'setup.py'))]
    return sorted([p for p in packages if os.path.basename(p) not in skip_pkgs])

def locate_wheels(base_dir):
    wheels = glob.glob(os.path.join(base_dir, '*.whl'))
    return sorted(wheels)

def get_lib_deps(base_dir):
    dependencies = {}
    for lib_dir in locate_libs(base_dir):
        try:
            lib_name = os.path.basename(lib_dir)
            setup_path = os.path.join(lib_dir, 'setup.py')
            requires = parse_setup(setup_path)
            for req in requires:
                req_parts = re.split('([<>~=]+)', req, 1)
                req_name = req_parts[0]
                spec = ''.join(req_parts[1:])
                spec = ','.join(sorted(spec.split(',')))
                if not req_name in dependencies:
                    dependencies[req_name] = {}
                if not spec in dependencies[req_name]:
                    dependencies[req_name][spec] = []
                dependencies[req_name][spec].append(lib_name)
        except:
            print('Failed to parse %s' % (setup_path))
    return dependencies

def get_wheel_deps(wheel_dir):
    from wheel.pkginfo import read_pkg_info_bytes
    from wheel.wheelfile import WheelFile

    requires_dist_re = re.compile(r"""^(?P<name>\S+)(\s\((?P<spec>.+)\))?$""")
    dependencies = {}
    for whl_path in locate_wheels(wheel_dir):
        try:
            with WheelFile(whl_path) as whl:
                pkg_info = read_pkg_info_bytes(whl.read(whl.dist_info_path + '/METADATA'))
                lib_name = pkg_info.get('Name')
                requires = pkg_info.get_all('Requires-Dist')
                for req in requires:
                    parsed = requires_dist_re.match(req.split(';')[0].strip())
                    req_name, spec = parsed.group('name', 'spec')
                    spec = ','.join(sorted(spec.split(','))) if spec else ''
                    if not req_name in dependencies:
                        dependencies[req_name] = {}
                    if not spec in dependencies[req_name]:
                        dependencies[req_name][spec] = []
                    dependencies[req_name][spec].append(lib_name)
        except:
            print('Failed to parse METADATA from %s' % (whl_path))
    return dependencies

def parse_setup(setup_filename):
    mock_setup = textwrap.dedent('''\
    def setup(*args, **kwargs):
        __setup_calls__.append((args, kwargs))
    ''')
    parsed_mock_setup = ast.parse(mock_setup, filename=setup_filename)
    with open(setup_filename, 'rt') as setup_file:
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

    requires = []
    if 'install_requires' in kwargs:
        requires += kwargs['install_requires']
    if 'extras_require' in kwargs:
        for extra in kwargs['extras_require'].values():
            requires += extra
    return requires

def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o : (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    return added, removed, modified

class Logger(object):
    def __init__(self, path):
        self.terminal = sys.stdout
        self.log = open(path, 'a')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

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
    parser.add_argument('--out', metavar='FILE', help='write log output to FILE in addition to stdout')
    parser.add_argument('--wheeldir', metavar='DIR', help='analyze wheels in DIR rather than source packages in this repository')
    args = parser.parse_args()

    if args.out:
        sys.stdout = Logger(args.out)

    if args.wheeldir:
        dependencies = get_wheel_deps(args.wheeldir)
    else:
        dependencies = get_lib_deps(base_dir)

    if args.verbose:
        print('Requirements discovered:')
        for requirement in sorted(dependencies.keys()):
            specs = dependencies[requirement]
            libs = []
            for spec in specs.keys():
                friendly_spec = ' (%s)' % (spec) if spec != '' else ''
                for lib in specs[spec]:
                    libs.append('  * %s%s' % (lib, friendly_spec))

            if len(libs) > 0:
                print('\n%s' % (requirement))
                for lib in libs:
                    print(lib)

    consistent = True
    for requirement in sorted(dependencies.keys()):
        specs = dependencies[requirement]
        num_specs = len(specs)
        if num_specs == 1:
            continue
        consistent = False
        if not args.verbose:
            break

        print("\n\nRequirement '%s' has %s unique specifiers:" % (requirement, num_specs))
        for spec in sorted(specs.keys()):
            libs = specs[spec]
            friendly_spec = '(none)' if spec == '' else spec
            print("\n  '%s'" % (friendly_spec))
            print('  ' + ('-' * (len(friendly_spec) + 2)))
            for lib in sorted(libs):
                print('    * %s' % (lib))

    exitcode = 0
    if not consistent:
        if not args.verbose:
            print('\n\nIncompatible dependency versions detected in libraries, run this script with --verbose for details')
        else:
            print('\n')
        exitcode = 1
    else:
        print('\n\nAll library dependencies verified, no incompatible versions detected')

    frozen_filename = os.path.join(base_dir, 'shared_requirements.txt')
    if args.freeze:
        if exitcode != 0:
            print('Unable to freeze requirements due to incompatible dependency versions')
            sys.exit(exitcode)
        else:
            with open(frozen_filename, 'w') as frozen_file:
                for requirement in sorted(dependencies.keys()):
                    spec = list(dependencies[requirement].keys())[0]
                    frozen_file.write(requirement + spec + '\n')
            print('Current requirements frozen to %s' % (frozen_filename))
            sys.exit(0)

    frozen = {}
    try:
        with open(frozen_filename, 'r') as frozen_file:
            for line in frozen_file:
                req_parts = re.split('([<>~=]+)', line.strip(), 1)
                req_name = req_parts[0]
                spec = ''.join(req_parts[1:])
                frozen[req_name] = [spec]
    except:
        print('Unable to open shared_requirements.txt, shared requirements will not be validated')
        sys.exit(exitcode)
    
    flat_deps = {req: sorted(dependencies[req].keys()) for req in dependencies}
    missing_reqs, new_reqs, changed_reqs = dict_compare(frozen, flat_deps)
    if args.verbose and len(missing_reqs) > 0:
        print('\nThe following requirements are frozen but do not exist in any current library:')
        for missing_req in missing_reqs:
            [spec] = frozen[missing_req]
            print('  * %s' % (missing_req + spec))
    if len(new_reqs) > 0:
        exitcode = 1
        for new_req in new_reqs:
            for spec in dependencies[new_req]:
                libs = dependencies[new_req][spec]
                print("\nRequirement '%s' is declared in the following libraries but has not been frozen:" % (new_req + spec))
                for lib in libs:
                    print("  * %s" % (lib))
    if len(changed_reqs) > 0:
        exitcode = 1
        for changed_req in changed_reqs:
            [frozen_spec] = frozen[changed_req]
            for current_spec in dependencies[changed_req]:
                if frozen_spec == current_spec:
                    continue
                libs = dependencies[changed_req][current_spec]
                print("\nThe following libraries declare requirement '%s' which does not match the frozen requirement '%s':" % (changed_req + current_spec, changed_req + frozen_spec))
                for lib in libs:
                    print("  * %s" % (lib))

    if exitcode == 0:
        print('All library dependencies validated against frozen requirements')

    sys.exit(exitcode)