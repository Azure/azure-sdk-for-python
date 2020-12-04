import logging
import os
import xml.etree.ElementTree as ET


root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
coverage_file = os.path.join(root_dir, "coverage.xml")
output_file = os.path.join(root_dir, "coverage-new.xml")


def create_coverage_report():
    if not os.path.exists(coverage_file):
        logging.info("No coverage file detected at {}".format(coverage_file))
    logging.info("Modifying coverage file at {}".format(coverage_file))
    tree = ET.parse(coverage_file)
    root = tree.getroot()

    packages = root[1]

    # First let's go through and edit the name to include the full path
    recursive_set_name(packages)

    packages_to_report = []
    for child in packages:
        # Order should be: ['azure', '<package-name>', 'azure-<package-name>', ...]
        name = child.attrib['name'].split('.')
        folder = name[1]
        package = name[2]
        if (folder, package) not in packages_to_report:
            packages_to_report.append((folder, package))

    new_packages = []
    for p in packages_to_report:
        n = create_new_node(p, root)
        new_packages.append(n)

    # Now remove all the old packages
    packages_nodes = root.findall('packages') # THere should only be one, but returns a list
    for packages_node in packages_nodes:
        for p in packages_node.findall('package'):
            packages_node.remove(p)


    for np in new_packages:
        packages_nodes[0].append(np)

    ET.ElementTree(root).write(output_file)


def recursive_set_name(root):
    # Stopping condition
    if 'line' in root.attrib:
        return

    # Add file path to the filename
    if root.tag == 'class':
        root.set('name', root.attrib['filename'])

    for child in root:
        recursive_set_name(child)


def create_new_node(package_tuple, xml_root):
    directory, package = package_tuple
    packages_root = xml_root[1]
    new_node = ET.Element('package')
    name = 'sdk' + '.' + directory + '.' + package
    create_default_attribs(new_node, name)

    classes_elem = ET.Element('classes')
    new_node.append(classes_elem)

    for sub_package in packages_root:
        if name in sub_package.attrib['name']:
            for class_elem in sub_package[0]:
                classes_elem.append(class_elem)
    return new_node


def create_default_attribs(node, name):
    node.set('branch-rate', '0')
    node.set('complexity', '0')
    node.set('line-rate', '0.0000')
    node.set('name', name)
