import copy
import logging
import os
import xml.etree.ElementTree as ET

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
coverage_file = os.path.join(root_dir, "coverage.xml")


def create_coverage_report():
    if not os.path.exists(coverage_file):
        logging.info("No coverage file detected at {}".format(coverage_file))
        return
    logging.info("Modifying coverage file at {}".format(coverage_file))
    tree = ET.parse(coverage_file)
    root = tree.getroot()

    packages = root[1]

    recursive_set_name(packages)

    packages_to_report = []
    for child in packages:
        # Order should be: ['azure', '<package-name>', 'azure-<package-name>', ...]
        name = child.attrib['name'].split('.')
        logging.info("Name: {}".format(name))
        folder, package = name[1], name[2]
        if (folder, package) not in packages_to_report:
            packages_to_report.append((folder, package))
            logging.info("Found a package: {}".format(package))

    package_names = [p[1] for p in packages_to_report]

    packages_root = root.find('packages')
    packages_root = packages

    packages_nodes = []
    for folder, package_name in packages_to_report:
        condense_nodes = []
        for child in packages:

            test_str = "sdk.{}.{}.{}".format(
                folder,
                package_name,
                package_name.replace('-', '.')
            )

            if package_name in child.attrib['name']:
                condense_nodes.append(child)

        packages_nodes.append(condense_nodes)

    nodes_to_remove = []
    for nodes in packages_nodes:
        if len(nodes) > 1:
            first_package = nodes[0]

            first_package_classes = first_package.find('classes')

            for node in nodes[1:]:
                temp_classes = node.find('classes')

                for _class in temp_classes:
                    first_package_classes.append(_class)
                nodes_to_remove.append(node)

    for n in nodes_to_remove:
        if n not in packages_root:
            continue

        packages_root.remove(n)

    # Last thing with root, change the 'name' attrib to be just the package name
    packages_to_add = []
    for package in root.find('packages'):
        name = package.attrib['name'].split('.')
        package.attrib['name'] = name[2]

        packages_to_add.append(copy.deepcopy(package))

    write_final_xml(packages_to_add)


def write_final_xml(packages_to_add):
    if not os.path.exists(coverage_file):
        logging.info("No coverage file detected at {}".format(coverage_file))
        return

    logging.info("Modifying coverage file at {}".format(coverage_file))
    tree = ET.parse(coverage_file)
    root = tree.getroot()

    packages = root[1]

    for p in packages_to_add:
        packages.insert(0, p)

    with open(coverage_file, "wb") as f:
        data = ET.tostring(root)
        f.write(data)


def recursive_set_name(root):
    # Stopping condition
    if 'line' in root.attrib:
        return

    # Add file path to the filename
    if root.tag == 'class':
        root.set('name', root.attrib['filename'])

    for child in root:
        recursive_set_name(child)
