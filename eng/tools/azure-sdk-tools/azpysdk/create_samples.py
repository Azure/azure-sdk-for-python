import argparse
import os
from typing import List, Optional

from .Check import Check
from ci_tools.logging import logger

_README_TEMPLATE = """\
# {package_name} Samples

This directory contains samples for the `{package_name}` package.

## Getting started

Install the package and its dependencies:

```bash
pip install {package_name}
```

## Running the samples

```bash
python sample_hello_world.py
```

## Advanced code generation

To generate a fuller set of samples and SDK code from a TypeSpec or Swagger
spec, use the `azpysdk generate` command:

```bash
azpysdk generate <target>
```

See `azpysdk generate --help` for more information.
"""

_HELLO_WORLD_TEMPLATE = """\
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
\"\"\"
FILE: sample_hello_world.py

DESCRIPTION:
    A minimal sample for the {package_name} package.

    To learn how to generate a fuller set of samples from a TypeSpec or
    Swagger spec, run:

        azpysdk generate <target>
\"\"\"


def main():
    # TODO: replace with real usage of {package_name}
    print("Hello from {package_name}!")


if __name__ == "__main__":
    main()
"""


class create_samples(Check):
    """Generate a starter samples scaffold for a targeted package.

    For each targeted package this check:

    * Creates a ``samples/`` directory if one does not already exist.
    * Generates a starter ``README.md`` inside ``samples/`` (if absent).
    * Generates a starter ``sample_hello_world.py`` inside ``samples/`` (if absent).

    For full SDK code generation (including samples) from a TypeSpec or Swagger
    spec, use the existing ``azpysdk generate`` command::

        azpysdk generate <target>
    """

    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the ``create-samples`` subcommand.

        Creates a starter ``samples/`` scaffold (README + hello-world sample)
        for each targeted package.  For full SDK code generation from a
        TypeSpec/Swagger spec use ``azpysdk generate <target>``.
        """
        parents = parent_parsers or []
        p = subparsers.add_parser(
            "create-samples",
            parents=parents,
            help=(
                "Generate a starter samples scaffold (README.md, sample_hello_world.py) "
                "for each targeted package. For full code generation from a TypeSpec or "
                "Swagger spec, use: azpysdk generate <target>"
            ),
        )
        p.set_defaults(func=self.run)
        p.add_argument(
            "--output-dir",
            default=None,
            help=(
                "Directory to write the samples scaffold into. "
                "Defaults to <package_dir>/samples."
            ),
        )

    def run(self, args: argparse.Namespace) -> int:
        """Create a samples scaffold for each targeted package."""
        logger.info("Running create-samples check...")

        targeted = self.get_targeted_directories(args)
        if not targeted:
            logger.warning("No target packages discovered for create-samples check.")
            return 0

        results: List[int] = []

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name

            output_dir = getattr(args, "output_dir", None) or os.path.join(package_dir, "samples")

            try:
                self._create_scaffold(package_name, output_dir)
                logger.info(
                    f"create-samples SUCCEEDED for {package_name}. "
                    f"Samples scaffold written to: {output_dir}"
                )
                logger.info(
                    "Tip: for full SDK code generation from a TypeSpec or Swagger spec, run: "
                    f"azpysdk generate {package_dir}"
                )
            except Exception as exc:
                logger.error(f"create-samples FAILED for {package_name}: {exc}")
                results.append(1)

        return max(results) if results else 0

    def _create_scaffold(self, package_name: str, output_dir: str) -> None:
        """Create the samples directory and starter files."""
        os.makedirs(output_dir, exist_ok=True)

        readme_path = os.path.join(output_dir, "README.md")
        if not os.path.exists(readme_path):
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(_README_TEMPLATE.format(package_name=package_name))
            logger.info(f"Created {readme_path}")
        else:
            logger.info(f"Skipping {readme_path} (already exists)")

        hello_world_path = os.path.join(output_dir, "sample_hello_world.py")
        if not os.path.exists(hello_world_path):
            with open(hello_world_path, "w", encoding="utf-8") as f:
                f.write(_HELLO_WORLD_TEMPLATE.format(package_name=package_name))
            logger.info(f"Created {hello_world_path}")
        else:
            logger.info(f"Skipping {hello_world_path} (already exists)")
