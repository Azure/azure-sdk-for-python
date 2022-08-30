# pip install -r eng/ml_sample_tools.txt before invoking
import argparse
import glob
import os
import re

from azure.storage.blob import BlobServiceClient

UPLOAD_PATTERN = "{build_id}/{filename}"
DEFAULT_CONTAINER = os.getenv("BLOB_CONTAINER", "ml-sample-submissions")
CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING", None)

TEST_INSTALL_TEMPLATE = """# <az_ml_sdk_test_install>
{install_command}
# </az_ml_sdk_test_install>"""

DISABLE_PREVIEW_INSTALL_TEMPLATE = """# <az_ml_sdk_install>
# </az_ml_sdk_install>"""


# I am fully aware that regex isn't fully compatible with traditional tagging. That being said, it is not necessary here.
def replace_preview_install(content):
    regex = r"^# \<az_ml_sdk_install\>[\s\S]*\<\/az_ml_sdk_install\>"
    return re.sub(regex, DISABLE_PREVIEW_INSTALL_TEMPLATE, content, flags=re.MULTILINE)


def replace_test_install_command(content, targeted_urls):
    regex = r"^# \<az_ml_sdk_test_install\>[\s\S]*\<\/az_ml_sdk_test_install\>"

    install_commands = ["pip install {}".format(url) for url in targeted_urls]
    install_lines = "\n".join(install_commands)

    return re.sub(regex, TEST_INSTALL_TEMPLATE.format(install_command=install_lines), content, flags=re.MULTILINE)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This python script modifies build.sh files for the azure ml samples repository. Inputs are a "
        + "folder containing the azure-ml whl, the root of a cloned azureml-samples repo, and an optional build id. "
        + "Retrieves the necessary connection string from BLOB_CONNECTION_STRING."
    )

    parser.add_argument(
        "--ml-repo",
        dest="ml_root",
        help=("The root of a fresh clone of the ml samples repo."),
    )

    parser.add_argument(
        "--ml-wheel-folder",
        dest="wheel_folder",
        help=("The folder from where the the azure ml wheel will reside."),
    )

    parser.add_argument(
        "--build-id",
        dest="build_id",
        default="a-manual-run",
        help=("The folder from where the the azure ml wheel will reside."),
    )

    args = parser.parse_args()

    print("Input repo {}".format(args.ml_root))
    print("Folder for search {}".format(args.wheel_folder))

    target_glob = os.path.join(os.path.abspath(args.wheel_folder), "*.whl")
    sdk_setup_sh = os.path.join(os.path.abspath(args.ml_root), "sdk", "setup.sh")
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(DEFAULT_CONTAINER)
    to_be_installed = []

    whls = glob.glob(target_glob)

    for whl in whls:
        if os.path.isfile(whl):
            upload_path = UPLOAD_PATTERN.format(build_id=args.build_id, filename=os.path.basename(whl))

            blob_client = container_client.get_blob_client(blob=upload_path)

            with open(whl, "rb") as data:
                result = blob_client.upload_blob(data=data, overwrite=True)
                to_be_installed.append(blob_client.primary_endpoint)
        else:
            print("Operated on non-whl file or folder {}".format(whl))
            exit(1)

    with open(sdk_setup_sh, "r", encoding="utf-8") as f:
        original_content = f.read()

    content = replace_preview_install(original_content)
    content = replace_test_install_command(content, to_be_installed)

    if content != original_content:
        with open(sdk_setup_sh, "w", encoding="utf-8") as f:
            f.write(content)
