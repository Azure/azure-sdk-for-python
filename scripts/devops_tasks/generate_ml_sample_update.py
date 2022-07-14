import argparse

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

    print("Input repo {}".format(args.ml_root))
    print("Folder for search {}".format(args.wheel_folder))