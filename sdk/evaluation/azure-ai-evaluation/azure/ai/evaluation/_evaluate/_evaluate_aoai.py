# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from openai import AzureOpenAI, OpenAI
import pandas as pd
from typing import Any, Callable, Dict, Tuple, TypeVar, Union, Type, Optional, TypedDict, List
from time import sleep

from ._batch_run import CodeClient, ProxyClient

#import aoai_mapping
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._constants import EVALUATION_PASS_FAIL_MAPPING
from azure.ai.evaluation._aoai.aoai_grader import AzureOpenAIGrader
from azure.ai.evaluation._common._experimental import experimental


TClient = TypeVar("TClient", ProxyClient, CodeClient)
LOGGER = logging.getLogger(__name__)


class OAIEvalRunCreationInfo(TypedDict, total=True):
    """Configuration for an evaluator"""

    client: Union[AzureOpenAI, OpenAI]
    eval_group_id: str
    eval_run_id: str
    grader_name_map: Dict[str, str]

def _split_evaluators_and_grader_configs(
        evaluators: Dict[str, Union[Callable, AzureOpenAIGrader]]
    ) -> Tuple[Dict[str, Callable], Dict[str, AzureOpenAIGrader]]:
    """
    Given a dictionary of strings to Evaluators and AOAI graders. Identity which is which, and return two
    dictionaries that each contain one subset, the first containing the evaluators and the second containing
    the AOAI graders. AOAI graders are defined as anything that is an instance of the AoaiGrader class,
    including child class instances. 

    :param evaluators: Evaluators to be used for evaluation. It should be a dictionary with key as alias for evaluator
        and value as the evaluator function or AOAI grader. 
    :type evaluators: Dict[str, Union[Callable, ]]
    :return: Tuple of two dictionaries, the first containing evaluators and the second containing AOAI graders.
    :rtype: Tuple[Dict[str, Callable], Dict[str, AoaiGrader]]
    """
    true_evaluators = {}
    aoai_graders = {}
    for key, value in evaluators.items():
        if isinstance(value, AzureOpenAIGrader):
            aoai_graders[key] = value
        else:
            true_evaluators[key] = value
    return true_evaluators, aoai_graders

@experimental
def _begin_aoai_evaluation(
        graders: Dict[str, AzureOpenAIGrader],
        column_mappings: Optional[Dict[str, Dict[str, str]]],
        data: pd.DataFrame,
        run_name: str
    ) -> List[OAIEvalRunCreationInfo]:
    """
    Use the AOAI SDK to start an evaluation of the inputted dataset against the supplied graders.
    AOAI evaluation runs must be queried for completion, so this returns the IDs needed to poll for the
    results, and map those results to the user-supplied names of the graders.

    If any of the graders require unique column mappings, this function will
    create a separate evaluation run for each grader. Otherwise, all graders
    will be evaluated in a single run.

    :param client: The AOAI client to use for the evaluation.
    :type client: Union[OpenAI, AzureOpenAI]
    :param graders: The graders to use for the evaluation. Should be a dictionary of string to AOAIGrader.
    :type graders: Dict[str, AoaiGrader]
    :param column_mappings: The column mappings to use for the evaluation.
    :type column_mappings: Optional[Dict[str, Dict[str, str]]]
    :param data: The data to evaluate, preprocessed by the `_validate_and_load_data` method.
    :type data: pd.DataFrame
    :param run_name: The name of the evaluation run.
    :type run_name: str
    :return: A list of evaluation run info that can be used to retrieve the results of the evaluation later
    :rtype: List[OAIEvalRunCreationInfo]
    """


    LOGGER.info("AOAI: Aoai graders detected among evaluator inputs. Preparing to create OAI eval group...")
    all_eval_run_info: List[OAIEvalRunCreationInfo] = []

    for selected_graders, selected_column_mapping in _get_graders_and_column_mappings(graders, column_mappings):
        all_eval_run_info.append(_begin_single_aoai_evaluation(
            selected_graders,
            data,
            selected_column_mapping,
            run_name
        ))

    return all_eval_run_info

def _begin_single_aoai_evaluation(
        graders: Dict[str, AzureOpenAIGrader],
        data: pd.DataFrame,
        column_mapping: Dict[str, str],
        run_name: str
    ) -> OAIEvalRunCreationInfo:
    """
    Use the AOAI SDK to start an evaluation of the inputted dataset against the supplied graders.
    AOAI evaluation runs must be queried for completion, so this returns a poller to accomplish that task
    at a later time.

    :param graders: The graders to use for the evaluation. Should be a dictionary of string to AOAIGrader.
    :type graders: Dict[str, AoaiGrader]
    :param data_source_config: The data source configuration to apply to the
    :type data_source_config: pd.DataFrame
    :param run_name: The name of the evaluation run.
    :type run_name: str
    :return: A tuple containing the eval group ID and eval run ID of the resultant eval run, as well as a dictionary
        that maps the user-supplied evaluators to the names of the graders as generated by the OAI service.
    :rtype: Tuple[str, str, Dict[str, str]]
    """

    # Format data for eval group creation
    grader_name_list  = []
    grader_list = []
    # It's expected that all graders supplied for a single eval run use the same credentials
    # so grab a client from the first grader.
    client = list(graders.values())[0].get_client()

    for name, grader in graders.items():
        grader_name_list.append(name)
        grader_list.append(grader._grader_config)
    data_source_config = _generate_data_source_config(data, column_mapping)

    # Create eval group
    # import pdb; pdb.set_trace()
    eval_group_info = client.evals.create(
        data_source_config=data_source_config,
        testing_criteria=grader_list,
        metadata={"is_foundry_eval": "true"}
    )
    
    LOGGER.info(f"AOAI: Eval group created with id {eval_group_info.id}. Creating eval run next...")
    # Use eval group info to map grader IDs back to user-assigned names.
    grader_name_map = {}
    num_criteria = len(eval_group_info.testing_criteria)
    if num_criteria != len(grader_name_list):
        raise EvaluationException(
            message=f"Number of testing criteria ({num_criteria})" +
                f" returned by OAI eval group does not match oai graders({len(grader_name_list)}).",
            blame=ErrorBlame.USER_ERROR,
            category=ErrorCategory.INVALID_VALUE,
            target=ErrorTarget.AOAI_GRADER,
        )
    for name, criteria in zip(grader_name_list, eval_group_info.testing_criteria):
        grader_name_map[criteria.id] = name

    # Create eval run 
    eval_run_id = _begin_eval_run(client, eval_group_info.id, run_name, data, column_mapping)
    LOGGER.info(f"AOAI: Eval run created with id {eval_run_id}." +
          " Results will be retrieved after normal evaluation is complete...")

    return OAIEvalRunCreationInfo(client=client, eval_group_id=eval_group_info.id, eval_run_id=eval_run_id, grader_name_map=grader_name_map)

def _get_evaluation_run_results(
        all_run_info: List[OAIEvalRunCreationInfo]
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Get the results of an OAI evaluation run, formatted in a way that is easy for the rest of the evaluation
    pipeline to consume. This method accepts a list of eval run information, and will combine the
    results into a single dataframe and metrics dictionary.
    
    :param all_run_info: A list of evaluation run information that contains the needed values
        to retrieve the results of the evaluation run.
    :type all_run_info: List[OAIEvalRunCreationInfo]
    :return: A tuple containing the results of the evaluation run as a dataframe, and a dictionary of metrics
        calculated from the evaluation run.
    :rtype: Tuple[pd.DataFrame, Dict[str, Any]]
    :raises EvaluationException: If the evaluation run fails or is not completed before timing out.
    """

    run_metrics = {}
    output_df = pd.DataFrame()
    for run_info in all_run_info:
        cur_output_df, cur_run_metrics = _get_single_run_results(run_info)
        output_df = pd.concat([output_df, cur_output_df], axis=1)
        run_metrics.update(cur_run_metrics)

    return output_df, run_metrics

def _get_single_run_results(
        run_info: OAIEvalRunCreationInfo,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Get the results of an OAI evaluation run, formatted in a way that is easy for the rest of the evaluation
    pipeline to consume.
    
    :param run_info: The evaluation run information that contains the needed values
        to retrieve the results of the evaluation run.
    :type run_info: OAIEvalRunCreationInfo
    :return: A tuple containing the results of the evaluation run as a dataframe, and a dictionary of metrics
        calculated from the evaluation run.
    :rtype: Tuple[pd.DataFrame, Dict[str, Any]]
    :raises EvaluationException: If the evaluation run fails or is not completed before timing out.
    """
    # Wait for evaluation run to complete
    run_results = _wait_for_run_conclusion(run_info["client"], run_info["eval_group_id"], run_info["eval_run_id"])
    if run_results.status != "completed":
        raise EvaluationException(
            message=f"AOAI evaluation run {run_info['eval_group_id']}/{run_info['eval_run_id']}"
             + f" failed with status {run_results.status}.",
            blame=ErrorBlame.UNKNOWN,
            category=ErrorCategory.FAILED_EXECUTION,
            target=ErrorTarget.AOAI_GRADER,
        )
    LOGGER.info(f"AOAI: Evaluation run {run_info['eval_group_id']}/{run_info['eval_run_id']}"
                + " completed successfully. Gathering results...")
    # Convert run results into a dictionary of metrics
    run_metrics = {}
    if run_results.per_testing_criteria_results is None:
        msg = ("AOAI evaluation run returned no results, despite 'completed' status. This might" +
               " occur when invalid or conflicting models are selected in the model and grader configs."
            f" Navigate to the evaluation run's report URL for more details: {run_results.report_url}")
        raise EvaluationException(
            message=msg,
            blame=ErrorBlame.UNKNOWN,
            category=ErrorCategory.FAILED_EXECUTION,
            target=ErrorTarget.AOAI_GRADER,
        ) 
    for criteria_result in run_results.per_testing_criteria_results:
        grader_name = run_info["grader_name_map"][criteria_result.testing_criteria]
        passed = criteria_result.passed
        failed = criteria_result.failed
        ratio = passed / (passed + failed)
        formatted_column_name = f"{grader_name}.pass_rate"
        run_metrics[formatted_column_name] = ratio

    
    # Get full results and convert them into a dataframe.
    # Notes on raw full data output from OAI eval runs:
    # Each row in the full results list in itself a list.
    # Each entry corresponds to one grader's results from the criteria list
    # that was inputted to the eval group.
    # Each entry is a dictionary, with a name, sample, passed boolean, and score number.
    # The name is used to figure out which grader the entry refers to, the sample is ignored.
    # The passed and score values are then added to the results dictionary, prepended with the grader's name
    # as entered by the user in the inputted dictionary.
    # Other values, if they exist, are also added to the results dictionary.
    raw_list_results = run_info["client"].evals.runs.output_items.list(
        eval_id=run_info["eval_group_id"],
        run_id=run_info["eval_run_id"]
    )
    listed_results = {"index": []}
    # raw data has no order guarantees, we need to sort them by their
    # datasource_item_id
    for row_result in raw_list_results.data:
        # Add the datasource_item_id for later sorting
        listed_results["index"].append(row_result.datasource_item_id)
        for single_grader_row_result in row_result.results:
            grader_name = run_info["grader_name_map"][single_grader_row_result["name"]]
            for name, value in single_grader_row_result.items():
                if name in ["name"]: # Todo decide if we also want to exclude "sample"
                    continue
                if name.lower() == "passed":
                    # create a `_result` column for each grader
                    result_column_name = f"outputs.{grader_name}.{grader_name}_result"
                    if len(result_column_name) < 50: #TODO: is this the limit? Should we keep "passed"?
                        if (result_column_name not in listed_results):
                            listed_results[result_column_name] = []
                        listed_results[result_column_name].append(EVALUATION_PASS_FAIL_MAPPING[value])

                formatted_column_name = f"outputs.{grader_name}.{name}"
                if (formatted_column_name not in listed_results):
                    listed_results[formatted_column_name] = []
                listed_results[formatted_column_name].append(value)
    output_df = pd.DataFrame(listed_results)
    # sort by index
    output_df = output_df.sort_values('index', ascending=[True])
    # remove index column
    output_df.drop(columns=["index"], inplace=True)
    return output_df, run_metrics


def _convert_remote_eval_params_to_grader(grader_id: str, init_params: Dict[str, Any]) -> AzureOpenAIGrader:
    """
    Helper function for the remote evaluation service.
    Given a model ID that refers to a specific AOAI grader wrapper class, return an instance of that class
    using the provided initialization parameters.

    :param grader_id: The model ID that refers to a specific AOAI grader wrapper class.
    :type grader_id: str
    :param init_params: The initialization parameters to be used for the AOAI grader wrapper class.
        Requires that it contain a model_config and grader_config as top-level keys.
    :type init_params: Dict[str, Any]
    """

    model_config = init_params.get("model_config", None)
    if model_config is None:
        raise EvaluationException(
            message="Grader converter needs a valid 'model_config' key in init_params.",
            blame=ErrorBlame.USER_ERROR,
            category=ErrorCategory.INVALID_VALUE,
            target=ErrorTarget.AOAI_GRADER,
        )

    grader_class =  _get_grader_class(grader_id)
    return grader_class(**init_params)

def _get_grader_class(model_id: str) -> Type[AzureOpenAIGrader]:
    """
    Given a model ID, return the class of the corresponding grader wrapper.
    """

    from azure.ai.evaluation import (
        AzureOpenAIGrader,
        AzureOpenAILabelGrader,
        AzureOpenAIStringCheckGrader,
        AzureOpenAITextSimilarityGrader,
    )
    id_map = {
        AzureOpenAIGrader.id: AzureOpenAIGrader,
        AzureOpenAILabelGrader.id: AzureOpenAILabelGrader,
        AzureOpenAIStringCheckGrader.id: AzureOpenAIStringCheckGrader,
        AzureOpenAITextSimilarityGrader.id: AzureOpenAITextSimilarityGrader,
    }

    for key in id_map.keys():
        if model_id == key:
            return id_map[key]
    raise EvaluationException(
        message=f"Model ID {model_id} not recognized as an AOAI grader ID",
        blame=ErrorBlame.USER_ERROR,
        category=ErrorCategory.INVALID_VALUE,
        target=ErrorTarget.AOAI_GRADER,
    )


def _get_graders_and_column_mappings(
        graders: Dict[str, AzureOpenAIGrader],
        column_mappings: Optional[Dict[str, Dict[str, str]]],
    ) -> List[Tuple[Dict[str, AzureOpenAIGrader], Optional[Dict[str, str]]]]:
    """
    Given a dictionary of column mappings and a dictionary of AOAI graders,
    Split them into sub-lists and sub-dictionaries that each correspond to a single evaluation run
    that must be performed to evaluate the entire dataset.

    Currently this function is fairly naive; it always splits the data if there are multiple
    graders present and any of them have a unique column mapping.

    This odd separate of data is necessary because our system allows for different evaluators
    to have different dataset columns mapped to the same input name for each evaluator, while
    the OAI API can't. So, if if there's a possibility that such a conflict might arise,
    we need to split the incoming data up.

    Currently splits each grader into its own eval group/run to ensure they each use
    their own credentials later on. Planned fast follow is to group things by
    matching credentials later.

    :param graders: The graders to use for the evaluation. Should be a dictionary of string to AOAIGrader.
    :type graders: Dict[str, AoaiGrader]
    :param column_mappings: The column mappings to use for the evaluation.
    :type column_mappings:  Optional[Dict[str, Dict[str, str]]]
    :return: A list of tuples, each containing dictionary of AOAI graders,
        and the column mapping they should use.
    :rtype: List[Tuple[Dict[str, AoaiGrader], Optional[Dict[str, str]]]]
    """

    default_mapping = column_mappings.get("default", None)
    return [({name : grader}, column_mappings.get(name, default_mapping)) for name, grader in graders.items()]

def _generate_data_source_config(input_data_df: pd.DataFrame, column_mapping: Dict[str, str]) -> Dict[str, Any]:
    """Produce a data source config that maps all columns from the supplied data source into
    the OAI API. The mapping is naive unless a column mapping is provided, in which case
    the column mapping's values overrule the relevant naive mappings
    
      :param input_data_df: The input data to be evaluated, as produced by the `_validate_and_load_data`
    helper function.
    :type input_data_df: pd.DataFrame
    :param column_mapping: The column mapping to use for the evaluation. If None, the default mapping will be used.
    :type column_mapping: Optional[Dict[str, str]]
    :return: A dictionary that can act as data source config for OAI evaluation group creation.
    :rtype: Dict[str, Any]  
    """

    data_source_config = {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        }
    }
    properties = data_source_config["item_schema"]["properties"]
    required = data_source_config["item_schema"]["required"]
    for key in column_mapping.keys():
        properties[key] = {
            "type": "string",
        }
        required.append(key)
    return data_source_config

def _generate_default_data_source_config(input_data_df: pd.DataFrame) -> Dict[str, Any]:
    """Produce a data source config that naively maps all columns from the supplied data source into
    the OAI API.
    
    :param input_data_df: The input data to be evaluated, as produced by the `_validate_and_load_data`
    helper function.
    :type input_data_df: pd.DataFrame
    :return: A dictionary that can act as data source config for OAI evaluation group creation.
    :rtype: Dict[str, Any]
    """

    properties = {}
    required = []

    for column in input_data_df.columns:
        properties[column] = {
            "type": "string",
        }
        required.append(column)
    data_source_config = {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": properties,
            "required": required,
        }
    }
    return data_source_config

def _get_data_source(input_data_df: pd.DataFrame, column_mapping: Dict[str, str]) -> Dict[str, Any]:
    """
    Given a dataframe of data to be evaluated, and an optional column mapping,
    produce a dictionary can be used as the data source input for an OAI evaluation run.

    :param input_data_df: The input data to be evaluated, as produced by the `_validate_and_load_data`
        helper function.
    :type input_data_df: pd.DataFrame
    :param column_mapping: The column mapping to use for the evaluation. If None, a naive 1:1 mapping is used.
    :type column_mapping: Optional[Dict[str, str]]
    :return: A dictionary that can be used as the data source input for an OAI evaluation run.
    :rtype: Dict[str, Any]
    """
    content = []
    column_to_source_map = {}
    # Convert from column mapping's format to figure out actual column names in
    # input dataframe, and map those to the appropriate OAI input names.
    for name, formatted_entry in column_mapping.items():
        # From "${" from start and "}" from end before splitting.
        entry_pieces = formatted_entry[2:-1].split(".")
        if len(entry_pieces) == 2 and entry_pieces[0] == "data":
            column_to_source_map[name] = entry_pieces[1]
        elif len(entry_pieces) == 3 and entry_pieces[0] == "run" and entry_pieces[1] == "outputs":
            column_to_source_map[name] = f"__outputs.{entry_pieces[2]}"

    # Using the above mapping, transform the input dataframe into a content
    # dictionary that'll work in an OAI data source.
    for row in input_data_df.iterrows():
        row_dict = {}
        for oai_key,dataframe_key in column_to_source_map.items():
            row_dict[oai_key] = str(row[1][dataframe_key])
        content.append({"item": row_dict})

    return {
        "type": "jsonl",
        "source": {
            "type": "file_content",
            "content": content,
        }
    }

def _begin_eval_run(
        client: Union[OpenAI, AzureOpenAI],
        eval_group_id: str,
        run_name: str,
        input_data_df: pd.DataFrame,
        column_mapping: Dict[str, str]
    ) -> str:
    """
    Given an eval group id and a dataset file path, use the AOAI API to 
    start an evaluation run with the given name and description.
    Returns a poller that can be used to monitor the run. 

    :param client: The AOAI client to use for the evaluation.
    :type client: Union[OpenAI, AzureOpenAI]
    :param eval_group_id: The ID of the evaluation group to use for the evaluation run.
    :type eval_group_id: str
    :param run_name: The name of the evaluation run.
    :type run_name: str
    :param input_data_df: The input data to be evaluated, as produced by the `_validate_and_load_data`
        helper function.
    :type input_data_df: pd.DataFrame
    :return: The ID of the evaluation run.
    :rtype: str
    """

    data_source = _get_data_source(input_data_df, column_mapping)
    eval_run = client.evals.runs.create(
        eval_id=eval_group_id,
        data_source=data_source,
        name=run_name,
        metadata={"sample_generation": "off","file_format": "jsonl", "is_foundry_eval": "true"}
        # TODO decide if we want to add our own timeout value?
    )
    return eval_run.id

# Post built TODO: replace with _red_team.py's retry logic?
def _wait_for_run_conclusion(
        client: Union[OpenAI, AzureOpenAI],
        eval_group_id: str,
        eval_run_id: str,
        max_wait_seconds = 21600
    ) -> Any:
    """
    Perform exponential backoff polling to get the results of an AOAI evaluation run.
    Raises an EvaluationException if max attempts are reached without receiving a concluding status.

    :param client: The AOAI client to use for the evaluation.
    :type client: Union[OpenAI, AzureOpenAI]
    :param eval_group_id: The ID of the evaluation group that contains the evaluation run of interest.
    :type eval_group_id: str
    :param eval_run_id: The evaluation run ID to get the results of.
    :type eval_run_id: str
    :param max_wait_seconds: The maximum amount of time to wait for the evaluation run to complete.
    :type max_wait_seconds: int
    :return: The results of the evaluation run.
    :rtype: Any
    """

    LOGGER.info(f"AOAI: Getting OAI eval run results from group/run {eval_group_id}/{eval_run_id}...")
    total_wait = 0
    iters = 0
    # start with ~51 minutes of exponential backoff
    # max wait time = 2^10 * 3 = 3072 seconds ~= 51 minutes
    wait_interval = 3 # Seconds.
    while(True):
        wait_interval *= 1.5
        total_wait += wait_interval
        # Reduce last wait interval if total wait time exceeds max wait time
        if total_wait > max_wait_seconds:
            wait_interval -= total_wait - max_wait_seconds
        sleep(wait_interval)
        response = client.evals.runs.retrieve(eval_id=eval_group_id, run_id=eval_run_id)
        if response.status not in  ["queued", "in_progress"]:
            return response
        if total_wait > max_wait_seconds:
            raise EvaluationException(
                message=f"Timed out waiting for AOAI evaluation to complete after {iters}"
                    + f" rounds of polling. Final status was {response.status}",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.FAILED_EXECUTION,
                target=ErrorTarget.AOAI_GRADER,
            )