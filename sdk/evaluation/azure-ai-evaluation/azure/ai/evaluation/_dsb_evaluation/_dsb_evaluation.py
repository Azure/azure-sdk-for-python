# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum
import os
import inspect
from azure.ai.evaluation._common._experimental import experimental
from typing import Any, Callable, Dict, List, Optional, Union
from azure.ai.evaluation._evaluators import _content_safety, _protected_material,  _groundedness
from azure.ai.evaluation._evaluate import _evaluate
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._model_configurations import AzureAIProject, EvaluationResult
from azure.ai.evaluation.simulator import Simulator, AdversarialSimulator, AdversarialScenario
from azure.ai.evaluation.simulator._utils import JsonLineList
from azure.ai.evaluation._common.utils import validate_azure_ai_project
from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration, OpenAIModelConfiguration
from azure.core.credentials import TokenCredential
import json
from pathlib import Path

@experimental
class DSBEvaluator(Enum):
    '''
    Evaluator types for DSB evaluation.
    '''

    CONTENT_SAFETY = "content_safety"
    GROUNDEDNESS = "groundedness"
    PROTECTED_MATERIAL = "protected_material"

@experimental
class DSBEvaluation:
    def __init__(
        self,
        azure_ai_project: dict,
        credential: TokenCredential,
        model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration]
    ):
        '''
        Initializes a DSBEvaluation object.

        :param azure_ai_project: A dictionary defining the Azure AI project. Required keys are 'subscription_id', 'resource_group_name', and 'project_name'.
        :type azure_ai_project: Dict[str, str]
        :param credential: The credential for connecting to Azure AI project.
        :type credential: ~azure.core.credentials.TokenCredential
        :param model_config: A dictionary defining the configuration for the model. Acceptable types are AzureOpenAIModelConfiguration and OpenAIModelConfiguration.
        :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration, ~azure.ai.evaluation.OpenAIModelConfiguration]
        :raises ValueError: If the model_config does not contain the required keys or any value is None.
        '''
        self._validate_model_config(model_config)
        self.model_config = model_config
        validate_azure_ai_project(azure_ai_project)
        self.azure_ai_project = AzureAIProject(**azure_ai_project)
        self.credential=credential

    @staticmethod
    def _validate_model_config(model_config: Any):
        """
        Validates the model_config to ensure all required keys are present and have non-None values.
        If 'type' is not specified, it will attempt to infer the type based on the keys present.

        :param model_config: The model configuration dictionary.
        :type model_config: Dict[str, Any]
        :raises ValueError: If required keys are missing or any of the values are None.
        """
        # Attempt to infer 'type' if not provided
        if "type" not in model_config:
            if "azure_deployment" in model_config and "azure_endpoint" in model_config:
                model_config["type"] = "azure_openai"
            elif "model" in model_config:
                model_config["type"] = "openai"
            else:
                raise ValueError(
                    "Unable to infer 'type' from model_config. Please specify 'type' as 'azure_openai' or 'openai'."
                )

        if model_config["type"] == "azure_openai":
            required_keys = ["azure_deployment", "azure_endpoint"]
        elif model_config["type"] == "openai":
            required_keys = ["api_key", "model"]
        else:
            raise ValueError("model_config 'type' must be 'azure_openai' or 'openai'.")

        missing_keys = [key for key in required_keys if key not in model_config]
        if missing_keys:
            raise ValueError(f"model_config is missing required keys: {', '.join(missing_keys)}")
        none_keys = [key for key in required_keys if model_config.get(key) is None]
        if none_keys:
            raise ValueError(f"The following keys in model_config must not be None: {', '.join(none_keys)}")

    async def _simulate_dsb(
            self,
            target: Callable, 
            max_conversation_turns: int = 1,
            max_simulation_results: int = 3, 
            adversarial_scenario: Optional[AdversarialScenario] = None,
            source_text: Optional[str] = None,
    ) -> str:
        '''
        Generates synthetic conversations based on provided parameters.

        :param target: The target function to call during the simulation.
        :type target: Callable
        :param max_conversation_turns: The maximum number of turns in a conversation.
        :type max_conversation_turns: int
        :param max_simulation_results: The maximum number of simulation results to generate.
        :type max_simulation_results: int
        :param adversarial_scenario: The adversarial scenario to simulate. If None, the non-adversarial Simulator is used.
        :type adversarial_scenario: Optional[AdversarialScenario]
        :param source_text: The source text to use as grounding document in the simulation.
        :type source_text: Optional[str]
        '''
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
            context = latest_message.get("context", None)
            latest_context = None
            try:
                if self._check_target_returns_context(target):
                    response, latest_context = target(query=application_input)
                else:
                    response = target(query=application_input)
            except Exception as e:
                response = f"Something went wrong {e!s}"

            ## We format the response to follow the openAI chat protocol format
            formatted_response = {
                "content": response,
                "role": "assistant",
                "context": latest_context if latest_context else context,
            }
            ## NOTE: In the future, instead of appending to messages we should just return `formatted_response`
            messages["messages"].append(formatted_response) # type: ignore
            return {"messages": messages_list, "stream": stream, "session_state": session_state, "context": latest_context if latest_context else context}
        
        ## Run simulator
        simulator_outputs = None
        data_path = "simulator_outputs.jsonl"

        ## If adversarial_scenario is not provided, run Simulator
        if adversarial_scenario is None:
            simulator = Simulator(self.model_config)
            simulator_outputs = await simulator(
                max_conversation_turns=max_conversation_turns,
                max_simulation_results=max_simulation_results,
                target=callback,
                text=source_text if source_text else "",
            )

        ## Ryun AdversarialSimulator
        elif adversarial_scenario:
            simulator = AdversarialSimulator(azure_ai_project=self.azure_ai_project, credential=self.credential)
            simulator_outputs = await simulator(
                scenario=adversarial_scenario,
                max_conversation_turns=max_conversation_turns,
                max_simulation_results=max_simulation_results,
                target=callback,
                text=source_text,
            )

        ## If no outputs are generated, raise an exception
        if not simulator_outputs:
            msg = "No outputs generated by the simulator"
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.ADVERSARIAL_SIMULATOR,
                category=ErrorCategory.UNKNOWN,
                blame=ErrorBlame.USER_ERROR,
            )

        ## Write outputs to file according to scenario
        with Path(data_path).open("w") as f:
            if not adversarial_scenario or adversarial_scenario != AdversarialScenario.ADVERSARIAL_CONVERSATION:
                if source_text or self._check_target_returns_context(target):
                    eval_input_data_json_lines = ""
                    for output in simulator_outputs:
                        query = None
                        response = None
                        context = source_text
                        ground_truth = source_text
                        for message in output["messages"]:
                            if message["role"] == "user":
                                query = message["content"]
                            if message["role"] == "assistant":
                                response = message["content"]
                        if query and response:
                            eval_input_data_json_lines += (
                                json.dumps(
                                    {
                                        "query": query,
                                        "response": response,
                                        "context": context,
                                        "ground_truth": ground_truth,
                                    }
                                )
                                + "\n"
                            )
                    f.write(eval_input_data_json_lines)
                elif isinstance(simulator_outputs,JsonLineList):
                    f.writelines(simulator_outputs.to_eval_qr_json_lines())
                else:
                    f.writelines(output.to_eval_qr_json_lines() for output in simulator_outputs)
            else:
                f.writelines(
                    [json.dumps({"conversation": {"messages": conversation["messages"]}}) + "\n" for conversation in simulator_outputs]
                )
        return data_path

    def _get_evaluators(
            self,
            evaluators: List[DSBEvaluator], 
    ) -> Dict[str, Callable]:
        '''
        Returns a dictionary of evaluators based on the provided list of DSBEvaluator.

        :param evaluators: A list of DSBEvaluator.
        :type evaluators: List[DSBEvaluator]
        '''
        evaluators_dict = {}
        for evaluator in evaluators:
            if evaluator == DSBEvaluator.CONTENT_SAFETY:
                evaluators_dict["content_safety"] = _content_safety.ContentSafetyEvaluator(
                    azure_ai_project=self.azure_ai_project, credential=self.credential
                )
            elif evaluator ==  DSBEvaluator.GROUNDEDNESS:
                evaluators_dict["groundedness"] = _groundedness.GroundednessEvaluator(
                    model_config=self.model_config,
                )
            elif evaluator == DSBEvaluator.PROTECTED_MATERIAL:
                evaluators_dict["protected_material"] = _protected_material.ProtectedMaterialEvaluator(
                    azure_ai_project=self.azure_ai_project, credential=self.credential
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

    @staticmethod
    def _check_target_returns_context(target: Callable) -> bool:
        '''
        Checks if the target function returns a tuple. We assume the second value in the tuple is the "context".
        
        :param target: The target function to check.
        :type target: Callable
        '''
        sig = inspect.signature(target)
        ret_type = sig.return_annotation
        if ret_type == inspect.Signature.empty:
            return False
        if ret_type is tuple: 
            return True
        return False

    def _validate_args(
            self,
            evaluators: List[DSBEvaluator],
            target: Callable,
            source_text: Optional[str] = None,
    ):
        '''
        Validates the arguments provided to the __call__ function of the DSBEvaluation object.
        :param evaluators: A list of DSBEvaluator.
        :type evaluators: List[DSBEvaluator]
        :param target: The target function to call during the evaluation.
        :type target: Callable
        :param source_text: The source text to use as grounding document in the evaluation.
        :type source_text: Optional[str]
        '''
        if DSBEvaluator.GROUNDEDNESS in evaluators and not (self._check_target_returns_context(target) or source_text):
            msg = "GroundednessEvaluator requires either source_text or a target function that returns context"
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.GROUNDEDNESS_EVALUATOR,
                category=ErrorCategory.MISSING_FIELD,
                blame=ErrorBlame.USER_ERROR,
            )

    async def __call__(
            self,
            evaluators: List[DSBEvaluator],
            target: Callable,
            adversarial_scenario: Optional[AdversarialScenario] = None,
            max_conversation_turns: int = 1,
            max_simulation_results: int = 3,
            source_text: Optional[str] = None,
            data_path: Optional[Union[str, os.PathLike]] = None,
            output_path: Optional[Union[str, os.PathLike]] = None
        ) -> EvaluationResult:
        '''
        Evaluates the target function based on the provided parameters.
        
        :param evaluators: A list of DSBEvaluator.
        :type evaluators: List[DSBEvaluator]
        :param target: The target function to call during the evaluation.
        :type target: Callable
        :param adversarial_scenario: The adversarial scenario to simulate. If None, the non-adversarial Simulator is used.
        :type adversarial_scenario: Optional[AdversarialScenario]
        :param max_conversation_turns: The maximum number of turns in a conversation.
        :type max_conversation_turns: int
        :param max_simulation_results: The maximum number of simulation results to generate.
        :type max_simulation_results: int
        :param source_text: The source text to use as grounding document in the evaluation.
        :type source_text: Optional[str]
        :param data_path: The path to the data file generated by the Simulator. If None, the Simulator will be run.
        :type data_path: Optional[Union[str, os.PathLike]]
        :param output_path: The path to write the evaluation results to if set.
        :type output_path: Optional[Union[str, os.PathLike]]
        '''
        ## Validate arguments
        self._validate_args(
            evaluators=evaluators, 
            target=target, 
            source_text=source_text,
        )

        ## If `data_path` is not provided, run simulator
        if data_path is None:
            data_path = await self._simulate_dsb(
                target=target,
                adversarial_scenario=adversarial_scenario,
                max_conversation_turns=max_conversation_turns,
                max_simulation_results=max_simulation_results,
                source_text=source_text,
            )

        ## Get evaluators
        evaluators_dict = self._get_evaluators(evaluators)

        ## Run evaluation
        evaluate_outputs = _evaluate.evaluate(
            data=data_path,
            evaluators=evaluators_dict,
            azure_ai_project=self.azure_ai_project,
            output_path=output_path,
        )
        return evaluate_outputs