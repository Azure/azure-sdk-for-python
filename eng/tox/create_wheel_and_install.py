from subprocess import check_call
import argparse
import os
import logging
import sys

logging.getLogger().setLevel(logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build a package directory into a wheel. Then install it."
    )
    parser.add_argument(
        "-d",
        "--distribution-directory",
        dest="distribution_directory",
        help="The path to the distribution directory. Should be passed $(Build.ArtifactStagingDirectory) from the devops yaml definition.",
        required=True,
    )

    parser.add_argument(
        "-p",
        "--path-to-setup",
        dest="target_setup",
        help="The path to the setup.py (not including the file) for the package we want to package into a wheel and install.",
        required=True,
    )

    args = parser.parse_args()

    check_call(
        [
            "python",
            os.path.join(args.target_setup, "setup.py"),
            "bdist_wheel",
            "--universal",
            "-d",
            args.distribution_directory,
        ]
    )

    discovered_wheels = [
        f
        for f in os.listdir(args.distribution_directory)
        if f.endswith(".whl")
    ]

    for wheel in discovered_wheels:
        # if the environment variable is set, that means that this is running where we
        # want to use the pre-built wheels
        if os.getenv("PREBUILT_WHEEL_DIR") is not None:
            # find the wheel in the set of prebuilt wheels
            if os.path.isfile(os.path.join(os.environ["PREBUILT_WHEEL_DIR"], wheel)):
                check_call(
                    [sys.executable, "-m", "pip", "install", "--upgrade", os.path.join(os.path.join(os.environ["PREBUILT_WHEEL_DIR"], wheel))]
                )
                logging.info("Installed {w} from wheel directory".format(w=wheel))
            # it does't exist, so we need to error out
            else:
                logging.error("{w} not present in the prebuilt wheels directory. Exiting.")
                exit(1)
        else:
            check_call(
                [sys.executable, "-m", "pip", "install",  "--upgrade", os.path.join(args.distribution_directory, wheel)]
            )
            logging.info("Installed {w} from fresh wheel.".format(w=wheel))
