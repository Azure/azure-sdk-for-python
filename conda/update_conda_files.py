"""Update package versions, yml files, release-logs, and changelogs for conda packages."""

import os
import argparse
import csv
import yaml
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from ci_tools.logging import logger, configure_logging 

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONDA_DIR = os.path.join(ROOT_DIR, "conda")

# paths
CONDA_RECIPES_DIR = os.path.join(CONDA_DIR, "conda-recipes")
CONDA_RELEASE_LOGS_DIR = os.path.join(CONDA_DIR, "conda-releaselogs")
CONDA_ENV_PATH = os.path.join(CONDA_RECIPES_DIR, "conda_env.yml")

# constants
RELEASE_PERIOD_MONTHS = 3

def update_conda_version() -> str:
    """Update the AZURESDK_CONDA_VERSION in conda_env.yml and return the new version."""
    
    with open(CONDA_ENV_PATH, 'r') as file:
        conda_env_data = yaml.safe_load(file)
    
    current_version = conda_env_data['variables']['AZURESDK_CONDA_VERSION']
    current_date = datetime.strptime(current_version, '%Y.%m.%d')
    
    new_date = current_date + relativedelta(months=RELEASE_PERIOD_MONTHS)

    # bump version    
    new_version = new_date.strftime('%Y.%m.%d')
    conda_env_data['variables']['AZURESDK_CONDA_VERSION'] = new_version
    
    with open(CONDA_ENV_PATH, 'w') as file:
        yaml.dump(conda_env_data, file, default_flow_style=False, sort_keys=False)
    
    logger.info(f"Updated AZURESDK_CONDA_VERSION from {current_version} to {new_version}")

    return new_version


# read from csv
def parse_csv():
    pass

# get new data plane libraries

# get outdated versions

# handle data yml

# mgmt yml

# import tests for data

# import tests for mgmt

# update conda-sdk-client

# release logs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update conda package files and versions."
    )

    args = parser.parse_args()
    
    configure_logging(args)

    # Call the update function
    update_conda_version()


