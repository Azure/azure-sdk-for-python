# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import argparse
import os
import time
import traceback

import git
from azure.ai.ml.entities._indexes.utils.git import clone_repo, get_keyvault_authentication
from azure.ai.ml.entities._indexes.utils.logging import (
    _logger_factory,
    enable_appinsights_logging,
    enable_stdout_logging,
    get_logger,
    track_activity,
)

logger = get_logger("git_clone")


def main(args, logger, activity_logger):
    try:
        if args.git_connection_id is not None and args.git_connection_id != "":
            from azure.ai.ml.entities._indexes.utils.connections import (
                connection_to_credential,
                get_connection_by_id_v2,
                get_metadata_from_connection,
                get_target_from_connection,
            )

            connection = get_connection_by_id_v2(args.git_connection_id)
            target = get_target_from_connection(connection)
            if args.git_repository != target and target != "":
                logger.warning(
                    f"Given git repository '{args.git_repository}' does not match the git repository '{target}' specified in the Workspace Connection '{args.git_connection_id}'. Using the arguments git repository."
                )
                args.git_repository = target

            # TODO: need to check to credentials is a AccessToken object?
            authentication = {"password": connection_to_credential(connection, data_plane=True).token}
            connection_meta = get_metadata_from_connection(connection)
            if "username" in connection_meta:
                authentication["username"] = connection_meta["username"]
            else:
                logger.warning(
                    f"Workspace Connection '{args.git_connection_id}' does not have a username specified. Assuming git_url has username."
                )
        elif args.authentication_key_prefix is not None:
            authentication = get_keyvault_authentication(args.authentication_key_prefix)
        else:
            authentication = None
    except Exception as e:
        logger.error(
            f"Failed to get authentication information from the Workspace Connection '{args.git_connection_id}'."
        )
        activity_logger.activity_info["error"] = (
            f"{e.__class__.__name__}: Failed to get authentication information from the Workspace Connection."
        )
        raise e

    activity_logger.activity_info["authentication_used"] = str(authentication is not None)

    try:
        clone_repo(args.git_repository, args.output_data, args.branch_name, authentication)
    except git.exc.GitError as e:
        activity_logger.activity_info["error"] = f"{e.__class__.__name__}: Failed with GitError."
        raise e
    except Exception as e:
        activity_logger.activity_info["error"] = f"{e.__class__.__name__}: Failed to clone git repository."
        raise e


def main_wrapper(args, logger):
    with track_activity(logger, "git_clone") as activity_logger:
        try:
            main(args, logger, activity_logger)
        except Exception:
            activity_logger.error(
                f"git_clone failed with exception: {traceback.format_exc()}"
            )  # activity_logger doesn't log traceback
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--git-repository", type=str, required=True, dest="git_repository")
    parser.add_argument("--branch-name", type=str, required=False, default=None)
    parser.add_argument(
        "--git-connection-id",
        type=str,
        required=False,
        default=None,
        help="The id of the Workspace Connection which contains authentication for the git repository to clone.",
    )
    parser.add_argument(
        "--authentication-key-prefix",
        type=str,
        required=False,
        default=None,
        help="<PREFIX>-USER and <PREFIX>-PASS are the expected names of two Secrets in the Workspace Key Vault which will be used for authenticated when pulling the given git repo.",
    )
    parser.add_argument("--output-data", type=str, required=True, dest="output_data")
    args = parser.parse_args()

    enable_stdout_logging()
    enable_appinsights_logging()

    if args.git_connection_id is None:
        logger.info("Reading connection id from environment variable")
        args.git_connection_id = os.environ.get("AZUREML_WORKSPACE_CONNECTION_ID_GIT")

    try:
        main_wrapper(args, logger)
    finally:
        if _logger_factory.appinsights:
            _logger_factory.appinsights.flush()
            time.sleep(5)

    logger.info("Finished cloning.")
