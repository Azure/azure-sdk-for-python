# Output old packages script

This script can be run to output old packages in the repo and their download stats to csv.

It defaults to reporting packages that have not seen a release in the last 2 years.

To omit an older package from the script output that we don't want to deprecate, add the `verify_status_by` key to the package's `pyproject.toml`. The value should be a date in the format `YYYY-MM-DD` and indicate the future date by which the package should be re-evaluated for deprecation. If a package should be kept and not re-evaluated, then set the date to 3000-01-01.

```toml
[tool.azure-sdk-build]
verify_status_by = 2025-07-09
```

## Requirements

- requests
- PePy API key ([PePy API](https://www.pepy.tech/pepy-api))

Set the `PEPY_API_KEY` environment variable to your PePy API key.

## Usage

1. Defaults to packages that have not released in the past 2 years. Omits already Inactive released packages.

```bash
python output_old_packages.py
```

2. Specify the number of years since last release (e.g. 1 year).

```bash
python output_old_packages.py -y 1
```

3. Run unfiltered (don't omit already Inactive packages or packages which have a `verify_status_by` in the future.)

```bash
python output_old_packages.py -f
```
