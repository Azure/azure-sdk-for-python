# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import argparse
import git
import os
import time
import traceback

from azure.ai.generative.index._utils.git import clone_repo, get_keyvault_authentication
from azure.ai.generative.index._utils.logging import get_logger, enable_stdout_logging, enable_appinsights_logging, track_activity, _logger_factory

logger = get_logger('git_clone')

def main(args, logger, activity_logger):
    try:
        connection_id = os.environ.get('AZUREML_WORKSPACE_CONNECTION_ID_GIT')
        if connection_id is not None and connection_id != '':
            from azure.ai.generative.index._utils.connections import get_connection_by_id_v2

            connection = get_connection_by_id_v2(connection_id)
            if args.git_repository != connection['properties']['target']:
                logger.warning(f"Given git repository '{args.git_repository}' does not match the git repository '{connection['properties']['target']}' specified in the Workspace Connection '{connection_id}'. Using the Workspace Connection git repository.")
            args.git_repository = connection['properties']['target']
            authentication = {'username': connection['properties']['metadata']['username'], 'password': connection['properties']['credentials']['pat']}
        elif args.authentication_key_prefix is not None:
            authentication = get_keyvault_authentication(args.authentication_key_prefix)
        else:
            authentication = None
    except Exception as e:
        logger.error(f"Failed to get authentication information from the Workspace Connection '{connection_id}'.")
        activity_logger.activity_info['error'] = f"{e.__class__.__name__}: Failed to get authentication information from the Workspace Connection."
        raise e

    activity_logger.activity_info['authentication_used'] = str(authentication is not None)

    try:
        clone_repo(args.git_repository, args.output_data, args.branch_name, authentication)
    except git.exc.GitError as e:
        activity_logger.activity_info['error'] = f"{e.__class__.__name__}: Failed with GitError."
        raise e
    except Exception as e:
        activity_logger.activity_info['error'] = f"{e.__class__.__name__}: Failed to clone git repository."
        raise e

def main_wrapper(args, logger):
    with track_activity(logger, "git_clone") as activity_logger:
        try:
            main(args, logger, activity_logger)
        except Exception:
            activity_logger.error(f"git_clone failed with exception: {traceback.format_exc()}")  # activity_logger doesn't log traceback
            raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--git-repository", type=str, required=True, dest='git_repository')
    parser.add_argument("--branch-name", type=str, required=False, default=None)
    parser.add_argument("--authentication-key-prefix", type=str, required=False, default=None, help="<PREFIX>-USER and <PREFIX>-PASS are the expected names of two Secrets in the Workspace Key Vault which will be used for authenticated when pulling the given git repo.")
    parser.add_argument("--output-data", type=str, required=True, dest='output_data')
    args = parser.parse_args()

    enable_stdout_logging()
    enable_appinsights_logging()

    try:
        main_wrapper(args, logger)
    finally:
        if _logger_factory.appinsights:
            _logger_factory.appinsights.flush()
            time.sleep(5)

    logger.info('Finished cloning.')
