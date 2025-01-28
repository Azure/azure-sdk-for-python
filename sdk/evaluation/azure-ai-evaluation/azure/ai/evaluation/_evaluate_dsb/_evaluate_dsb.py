# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum
import os
from typing import Callable, Dict, List, Optional, Union
from azure.ai.evaluation._evaluators import _content_safety, _protected_material,  _groundedness
from azure.ai.evaluation._evaluate import _evaluate
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._model_configurations import AzureAIProject, EvaluationResult
from azure.ai.evaluation.simulator import AdversarialSimulator, AdversarialScenario
from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential
import json
from pathlib import Path

class DSBEvaluator(Enum):
    """Evaluator types

    """

    CONTENT_SAFETY = "content_safety"
    GROUNDEDNESS = "groundedness"
    PROTECTED_MATERIAL = "protected_material"

async def _simulate_dsb(
        azure_ai_project: AzureAIProject,
        target: Callable, 
        adversarial_scenario: AdversarialScenario, 
        credential: TokenCredential,
        max_conversation_turns: int = 1,
        max_simulation_results: int = 3
) -> str:
    

    ## Define callback
    async def callback(
        messages: List[Dict],
        stream: bool = False,
        session_state: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> dict:
        messages_list = messages["messages"] # type: ignore
        latest_message = messages_list[-1]
        application_input = latest_message["content"]
        latest_context = latest_message.get("context", None)
        try:
            response = target(query=application_input)
        except Exception as e:
            response = f"Something went wrong {e!s}"

        ## We format the response to follow the openAI chat protocol format
        formatted_response = {
            "content": response,
            "role": "assistant",
            "context": {latest_context},
        }
        ## NOTE: In the future, instead of appending to messages we should just return `formatted_response`
        messages["messages"].append(formatted_response) # type: ignore
        return {"messages": messages_list, "stream": stream, "session_state": session_state, "context": context}
    
    ## Run simulator
    simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=credential)
    simulator_outputs = await simulator(
        scenario=adversarial_scenario,
        max_conversation_turns=max_conversation_turns,
        max_simulation_results=max_simulation_results,
        target=callback,
    )

    ## Write outputs to file according to scenario
    data_path = "simulator_outputs.jsonl"
    with Path(data_path).open("w") as f:
        ## NOTE: Which scenarios need query response format vs. conversation format?
        if adversarial_scenario != AdversarialScenario.ADVERSARIAL_CONVERSATION:
            f.write(simulator_outputs.to_eval_qr_json_lines())
        else:
            f.writelines(
                [json.dumps({"conversation": {"messages": conversation["messages"]}}) + "\n" for conversation in simulator_outputs]
            )
    return data_path

def get_evaluators(
        evaluators: List[DSBEvaluator], 
        azure_ai_project: AzureAIProject,
        credential: TokenCredential, 
        model_config: Optional[dict] = None
) -> Dict[str, Callable]:
    evaluators_dict = {}
    for evaluator in evaluators:
        if evaluator == DSBEvaluator.CONTENT_SAFETY:
            evaluators_dict["content_safety"] = _content_safety.ContentSafetyEvaluator(
                azure_ai_project=azure_ai_project, credential=credential
            )
        elif evaluator ==  DSBEvaluator.GROUNDEDNESS:
            if not model_config:
                msg = "`model_config`parameter is required for GroundednessEvaluator"
                raise EvaluationException(
                    message=msg,
                    internal_message=msg,
                    target=ErrorTarget.GROUNDEDNESS_EVALUATOR,
                    category=ErrorCategory.MISSING_FIELD,
                    blame=ErrorBlame.USER_ERROR,
                )
            evaluators_dict["groundedness"] = _groundedness.GroundednessEvaluator(
                model_config=model_config,
            )
        elif evaluator == DSBEvaluator.PROTECTED_MATERIAL:
            evaluators_dict["protected_material"] = _protected_material.ProtectedMaterialEvaluator(
                azure_ai_project=azure_ai_project, credential=credential
            )
        else:
            msg = f"Invalid evaluator: {evaluator}. Supported evaluators are: {DSBEvaluator.__members__.values()}"
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.UNKNOWN, ## NOTE: We should add a target for this potentially
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )
    return evaluators_dict

async def evaluate_dsb(
        adversarial_scenario: AdversarialScenario,
        azure_ai_project: AzureAIProject,
        credential: TokenCredential,
        evaluators: List[DSBEvaluator],
        target: Callable,
        max_conversation_turns: int = 1,
        max_simulation_results: int = 3,
        data_path: Optional[Union[str, os.PathLike]] = None,
        model_config: Optional[dict] = None,
        output_path: Optional[Union[str, os.PathLike]] = None,
) -> EvaluationResult:
    ## If `data_path` is not provided, run simulator
    if data_path is None:
        data_path = await _simulate_dsb(
            azure_ai_project=azure_ai_project,
            target=target,
            adversarial_scenario=adversarial_scenario,
            credential=credential,
            max_conversation_turns=max_conversation_turns,
            max_simulation_results=max_simulation_results,
        )
    
    ## Get evaluators
    evaluators_dict = get_evaluators(evaluators, azure_ai_project, credential, model_config)

    ## Run evaluation
    evaluate_outputs = _evaluate.evaluate(
        data=data_path,
        evaluators=evaluators_dict,
        azure_ai_project=azure_ai_project,
        output_path=output_path,
    )
    return evaluate_outputs