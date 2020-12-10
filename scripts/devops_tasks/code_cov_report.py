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

    # First let's go through and edit the name to include the full path
    recursive_set_name(packages)

    packages_to_report = []
    for child in packages:
        # Order should be: ['azure', '<package-name>', 'azure-<package-name>', ...]
        name = child.attrib['name'].split('.')
        logging.info("Name: {}".format(name))
        folder = name[1]
        package = name[2]
        if (folder, package) not in packages_to_report:
            packages_to_report.append((folder, package))
            logging.info("Found a package: {}".format(package))

    print(packages_to_report)

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
    for package_tuple in packages_to_report:
        folder, package_name = package_tuple

        condense_nodes = []
        master_package = False
        for child in packages:
            # print(child.tag, child.attrib)

            test_str = "sdk.{}.{}.{}".format(
                folder,
                package_name,
                package_name.replace('-', '.')
            )
            print(test_str)

            if test_str in child.attrib['name']:
                # print("condense_package")
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
        print(n.tag, n.attrib)

        packages_root.remove(n)

    ET.ElementTree(root).write(coverage_file)

    print("\n\n\nFinal packages")
    for package in packages_root:
        print(package.tag, package.attrib)

    return
    # ET.ElementTree(root).write("coverage-new.xml")

    # master_package = False
    # for child in packages:
    #     print()
    #     print(child.tag, child.attrib)

    #     # Should this be combined into another node
    #     for p in packages_to_report:
    #         if p[1] in child.attrib['name']:
    #             print("FOUND: ", p)

    #             # Need to make sure it's not the master one
    #             test_str = "sdk.{}.{}.azure.{}".format(p[0], p[1], p[0])
    #             print(test_str)
    #             print(child.attrib['name'])

    #             if test_str != child.attrib['name']:
    #                 print("Condense package")


    # quit()







    # new_packages = []
    # for p in packages_to_report:
    #     n = create_new_node(p, packages_root)
    #     new_packages.append(n)

    # # Now remove all the old packages
    # packages_nodes = root.findall('packages') # THere should only be one, but returns a list
    # for packages_node in packages_nodes:
    #     for p in packages_node.findall('package'):
    #         packages_node.remove(p)

    # for np in new_packages:
    #     packages_nodes[0].append(np)

    # ET.ElementTree(root).write("coverage-new.xml")


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

    quit()
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


# create_coverage_report()