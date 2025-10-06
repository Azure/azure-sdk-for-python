# Python SDK Health Status Report

This script generates a health status report for the Python SDK. The report can be found at [aka.ms/azsdk/python/health](https://www.aka.ms/azsdk/python/health).

# How to run the script

1. pip install -r dev_requirements.txt
2. az login
3. Set the `GH_TOKEN` environment variable to your [GitHub PAT](https://github.com/settings/tokens) (with repo permissions).
4. Run the script: `python output_health_report.py`

## Command line options

By default, the script will generate a csv report. To generate a report in markdown or html, pass `-f markdown` or `-f html`, respectively. To omit SDK team owned libraries from the report, pass `-s`.
