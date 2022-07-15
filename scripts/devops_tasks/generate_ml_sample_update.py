# pip install -r eng/ml_sample_tools.txt before invoking
import argparse
import glob
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This python script modifies build.sh files for the azure ml samples repository. Inputs are a folder containing the azure-ml whl, and  "
    )

    parser.add_argument(
        "--ml-repo",
        dest="ml_root",
        help=(
            "The root of a fresh clone of the ml samples repo."
        ),
    )

    parser.add_argument(
        "--ml-wheel-folder",
        dest="wheel_folder",
        help=(
            "The folder from where the the azure ml wheel will reside."
        ),
    )

    args = parser.parse_args()

    target_glob = os.path.join(os.path.abspath(args.wheel_folder), "*.whl")

    print("Input repo {}".format(args.ml_root))
    print("Folder for search {}".format(args.wheel_folder))

    # find all *.whl in the search folder
    whls = glob.glob(target_glob)

    print(whls)

    
    # with open(os.path.join(os.path.abspath(args.wheel_folder), 'sdk/setup.sh'), "r", encoding="utf-8") as f:
    #     lines = f.readlines()    
    
    # between <az_ml_sdk_install>
    # comment each line
    # and </az_ml_sdk_install>

    # between <az_ml_sdk_test_install>
    # insert line of form pip install <blob-location>
    # </az_ml_sdk_test_install>
