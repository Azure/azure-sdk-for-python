import logging
import os
import xml.etree.ElementTree as ET

from code_cov_report import create_coverage_report

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

    # First let's go through and edit the name to include the full path
    recursive_set_name(packages)

    packages_to_report = []
    for child in packages:
        # Order should be: ['azure', '<package-name>', 'azure-<package-name>', ...]
        name = child.attrib['name'].split('.')
        logging.info("Name: {}".format(name))
        folder = name[1]
        package = name[2]
        print("Folder: {}\tPackage: {}\tName: {}".format(folder, package, name))
        if (folder, package) not in packages_to_report:
            packages_to_report.append((folder, package))
            logging.info("Found a package: {}".format(package))

    print(packages_to_report)
    package_names = [p[1] for p in packages_to_report]
    print("package names: {}".format(package_names))

    packages_root = root.find('packages')
    packages_root = packages
    print(packages_root.tag, packages_root.attrib)
    print('\n\n')

    # New plan
    # 1. Get all the unique package nodes (done above)
    # 2. Iterate through all packages again, if the package should be within another combine them
    # 2b. Find the first node for each of those packages.
    # 2c. Find the following nodes for each of those packages
    # 3. Combine the following matching nodes by only moving the class sections to the end of the master package
    # 3b. Remove the nodes after combining
    # 4. Write out
    # 5. pray

    packages_nodes = []
    for folder, package_name in packages_to_report:
        condense_nodes = []
        for child in packages:
            # print(child.tag, child.attrib)

            test_str = "sdk.{}.{}.{}".format(
                folder,
                package_name,
                package_name.replace('-', '.')
            )
            # print("Test string: ", test_str)

            if package_name in child.attrib['name']:
                print("condense_package \t {}".format(child.attrib['name']))
                condense_nodes.append(child)

        print("Condensing into one:")
        for n in condense_nodes:
            print(n.tag, n.attrib)
        # print(condense_nodes)
        packages_nodes.append(condense_nodes)
        # print()


    nodes_to_remove = []
    for nodes in packages_nodes:
        if len(nodes) > 1:
            first_package = nodes[0]

            first_package_classes = first_package.find('classes')

            for node in nodes[1:]:
                # print(node.tag, node.attrib)
                temp_classes = node.find('classes')

                for _class in temp_classes:
                    first_package_classes.append(_class)
                nodes_to_remove.append(node)


    print("\nRemoving nodes:")
    for n in nodes_to_remove:
        if n not in packages_root:
            continue
        print(n.tag, n.attrib)

        packages_root.remove(n)

    # Compress into the one package
    # Change name to just the one package

    # Last thing with root, change the 'name' attrib to be just the package name

    for package in root.find('packages'):
        name = package.attrib['name'].split('.')
        print(name)
        package.attrib['name'] = name[2]

    # ET.ElementTree(root).write("coverage-new.xml")
    with open(coverage_file, "wb") as f:
        data = ET.tostring(root)#, encoding="utf8") # Build System does not support utf-8 encoding
        f.write(data)


    print("\n\n\nFinal packages")
    for package in packages_root:
        print(package.tag, package.attrib)

    return

def recursive_set_name(root):
    # Stopping condition
    if 'line' in root.attrib:
        return

    # Add file path to the filename
    if root.tag == 'class':
        root.set('name', root.attrib['filename'])

    for child in root:
        recursive_set_name(child)


def create_new_node(package_tuple, packages_root):
    # print(f"ROOT: {packages_root.tag}")
    directory, package_name = package_tuple
    new_node = ET.Element('package')
    name = 'sdk' + '.' + directory + '.' + package_name
    create_default_attribs(new_node, name)


    for package in packages_root.findall('package'):

        if package_name in package.attrib['name']:
            print(package.tag, package.attrib)

            for classes in package:
                print(classes.tag, classes.attrib)

                if classes[0].tag == "class" and package_name in classes[0].attrib["filename"]:
                    new_node.append(classes)
                    break


    ET.ElementTree(new_node).write("temp.xml")

    # quit()
    return new_node


    package_root = packages_root.find('package')
    print(package_root.tag, package_root.attrib)

    print("CHILD")
    for child in package_root:
        print(child.tag)

    return


    classes_node = package_root.find('classes')
    class_nodes = classes_node.find_all('class')
    print(class_nodes)

    # classes_elem = ET.Element('classes')
    new_node.append(classes_elem)

    # for classes
    for sub_package in packages_root:
        if name in sub_package.attrib['name']:
            print(sub_package.tag)
            for class_elem in sub_package[0]:
                classes_elem.append(class_elem)
    return new_node


def create_default_attribs(node, name):
    node.set('branch-rate', '0')
    node.set('complexity', '0')
    node.set('line-rate', '0.0000')
    node.set('name', name)


if __name__ == "__main__":
    create_coverage_report()