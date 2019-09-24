from m2r import parse_from_file

# need to generate index.rst from readme.md OR copy readme.md
import zipfile
import glob
import logging
import shutil
import argparse
import os
import pdb

logging.getLogger().setLevel(logging.INFO)

RST_EXTENSION_FOR_INDEX = """

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
  :maxdepth: 5
  :glob:
  :caption: Developer Documentation

  {}
"""

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
sphinx_conf = os.path.join(root_dir, 'doc', 'sphinx', 'conf.py')

def create_index_file(readme_location, package_rst):
    readme_ext = os.path.splitext(readme_location)[1]

    if readme_ext == ".md":
        output = parse_from_file(readme_location)
    elif readme_ext == ".rst":
        with open(readme_location, 'r') as file:
            output = file.read()
    else:
        logging.error("{} is not a valid readme type. Expecting RST or MD.".format(readme_location))

    output += RST_EXTENSION_FOR_INDEX.format(package_rst)

    return output

def unzip_sdist_to_directory(containing_folder):
    # grab the first one
    path_to_zip_file = glob.glob(os.path.join(containing_folder, "*.zip"))[0]

    # dump into an `unzipped` folder
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(containing_folder)
        return os.path.splitext(path_to_zip_file)[0]

def move_and_rename(source_location):
    new_location = os.path.join(os.path.dirname(source_location), 'unzipped')
    os.rename(source_location, new_location)

    return new_location

def copy_conf(doc_folder):
    if not os.path.exists(doc_folder):
        os.mkdir(doc_folder)

    shutil.copy(sphinx_conf, doc_folder)

def create_index(doc_folder, source_location, package_name):
    index_content = ""

    package_rst = "{}.rst".format(package_name.replace("-", "."))
    content_destination = os.path.join(doc_folder, 'index.rst')

    if not os.path.exists(doc_folder):
        os.mkdir(doc_folder)

    # grep all content
    markdown_readmes = glob.glob(os.path.join(source_location, 'README.md'))
    rst_readmes = glob.glob(os.path.join(source_location, 'README.rst'))

    # if markdown, take that, otherwise rst
    if markdown_readmes:
        index_content = create_index_file(markdown_readmes[0], package_rst)
    elif rst_readmes:
        index_content = create_index_file(rst_readmes[0], package_rst)
    else:
        logging.warning("No readmes detected for this package {}".format(package_name))
        index_content = RST_EXTENSION_FOR_INDEX.format(package_rst)

    # write index
    with open(content_destination, "w+") as f:
        f.write(index_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Prep a doc folder for consumption by sphinx."
    )

    parser.add_argument(
        "-d",
        "--dist_dir",
        dest="dist_dir",
        help="The dist location on disk. Usually /tox/dist.",
        required=True,
    )

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk. The target module passed to pylint will be <target_package>/azure.",
        required=True,
    )


    args = parser.parse_args()

    package_path = os.path.abspath(args.target_package)
    package_name = os.path.basename(package_path)

    source_location = move_and_rename(unzip_sdist_to_directory(args.dist_dir))
    doc_folder = os.path.join(source_location, 'docgen')

    copy_conf(doc_folder)
    create_index(doc_folder, source_location, package_name)

    print(doc_folder)
    print(os.listdir(doc_folder))
