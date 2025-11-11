import sys
import argparse
import logging
from pathlib import Path
from typing import Optional
import yaml
import json
from .generate_utils import update_metadata_json, generate_packaging_and_ci_files
from .package_utils import check_file


logging.basicConfig(
    stream=sys.stdout,
    format="[%(levelname)s] %(message)s",
)

_LOGGER = logging.getLogger(__name__)


def main(
    package_path: Path,
    *,
    pipeline_input: Optional[dict] = None,
    codegen_config: Optional[dict] = None,
    spec_folder: Optional[Path] = None,
    readme_or_tsp: Optional[str] = None,
):
    # update _metadata.json
    try:
        tsp_location_file = package_path / "tsp-location.yaml"
        if pipeline_input is None and tsp_location_file.exists():
            pipeline_input = {}
            with open(tsp_location_file, "r") as f:
                tsp_data = yaml.safe_load(f)
                if tsp_data.get("commit"):
                    pipeline_input["headSha"] = tsp_data["commit"]
                else:
                    _LOGGER.warning("TSP location file does not contain 'commit' field.")
                if tsp_data.get("repo"):
                    pipeline_input["repoHttpsUrl"] = tsp_data["repo"]
                else:
                    _LOGGER.warning("TSP location file does not contain 'repo' field.")
                if tsp_data.get("directory"):
                    readme_or_tsp = tsp_data["directory"]
                else:
                    _LOGGER.warning("TSP location file does not contain 'directory' field.")

            if Path("eng/emitter-package.json").exists():
                codegen_config = {}
                with open("eng/emitter-package.json", "r") as f:
                    emitter_data = json.load(f)
                    if emitter_data.get("dependencies", {}).get("@azure-tools/typespec-python"):
                        codegen_config["emitterVersion"] = emitter_data["dependencies"]["@azure-tools/typespec-python"]
                    else:
                        _LOGGER.warning(
                            "'@azure-tools/typespec-python' not found in emitter-package.json dependencies."
                        )

        if pipeline_input and codegen_config and readme_or_tsp:
            update_metadata_json(
                package_path,
                pipeline_input=pipeline_input,
                codegen_config=codegen_config,
                spec_folder=spec_folder,
                input_readme=readme_or_tsp,
            )
        else:
            _LOGGER.error(
                f" Skip metadata update for missing information: pipeline input {pipeline_input}, codegen_config {codegen_config}, readme_or_tsp {readme_or_tsp}."
            )
    except Exception as e:
        _LOGGER.error(f"Fail to update meta: {str(e)}")

    # generate packaging files and ci.yml if needed
    try:
        generate_packaging_and_ci_files(package_path)
    except Exception as e:
        _LOGGER.warning(
            f"Fail to generate packaging files and ci.yml under {package_path} for {readme_or_tsp}: {str(e)}"
        )

    # edit other metadata files if needed
    if "azure-mgmt-" in package_path.name:
        check_file(package_path)


def generate_main():
    """Main method for command line execution"""

    parser = argparse.ArgumentParser(
        description="Update metadata files for Azure SDK package.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--package-path",
        dest="package_path",
        required=True,
        help="Absolute path to the package directory",
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        help="Verbosity in DEBUG mode",
    )

    args = parser.parse_args()
    main_logger = logging.getLogger()
    logging.basicConfig()
    main_logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    package_path = Path(args.package_path)

    if not package_path.exists():
        _LOGGER.error(f"Package path does not exist: {package_path}")
        sys.exit(1)

    if not package_path.is_absolute():
        _LOGGER.error(f"Package path must be absolute: {package_path}")
        sys.exit(1)

    main(package_path)


if __name__ == "__main__":
    generate_main()
