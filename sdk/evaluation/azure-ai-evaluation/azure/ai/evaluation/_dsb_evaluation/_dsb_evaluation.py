# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum
import os
import inspect
import logging
from datetime import datetime
from azure.ai.evaluation._common._experimental import experimental
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from azure.ai.evaluation._evaluators import _content_safety, _protected_material,  _groundedness, _relevance, _similarity, _fluency, _xpia
from azure.ai.evaluation._evaluate import _evaluate
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._model_configurations import AzureAIProject, EvaluationResult
from azure.ai.evaluation.simulator import Simulator, AdversarialSimulator, AdversarialScenario, AdversarialScenarioJailbreak, IndirectAttackSimulator, DirectAttackSimulator
from azure.ai.evaluation.simulator._utils import JsonLineList
from azure.ai.evaluation._common.utils import validate_azure_ai_project
from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration, OpenAIModelConfiguration
from azure.core.credentials import TokenCredential
import json
from pathlib import Path

logger = logging.getLogger(__name__)

def _setup_logger():
    """Configure and return a logger instance for the CustomAdversarialSimulator.

    :return: The logger instance.
    :rtype: logging.Logger
    """
    log_filename = datetime.now().strftime("%Y_%m_%d__%H_%M.log")
    logger = logging.getLogger("CustomAdversarialSimulatorLogger")
    logger.setLevel(logging.DEBUG)  
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

@experimental
class _DSBEvaluator(Enum):
    '''
    Evaluator types for DSB evaluation.
    '''

    CONTENT_SAFETY = "content_safety"
    GROUNDEDNESS = "groundedness"
    PROTECTED_MATERIAL = "protected_material"
    RELEVANCE = "relevance"
    SIMILARITY = "similarity"
    FLUENCY = "fluency"
    INDIRECT_ATTACK = "indirect_attack"
    DIRECT_ATTACK = "direct_attack"

@experimental
class _DSBEvaluation:
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
        self.logger = _setup_logger()

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
            conversation_turns : List[List[Union[str, Dict[str, Any]]]] = [], 
            adversarial_scenario: Optional[Union[AdversarialScenario, AdversarialScenarioJailbreak]] = None,
            source_text: Optional[str] = None,
            direct_attack: bool = False,
    ) -> Dict[str, str]:
        '''
        Generates synthetic conversations based on provided parameters.

        :param target: The target function to call during the simulation.
        :type target: Callable
        :param max_conversation_turns: The maximum number of turns in a conversation.
        :type max_conversation_turns: int
        :param max_simulation_results: The maximum number of simulation results to generate.
        :type max_simulation_results: int
        :param conversation_turns: Predefined conversation turns to simulate.
        :type conversation_turns: List[List[Union[str, Dict[str, Any]]]]
        :param adversarial_scenario: The adversarial scenario to simulate. If None, the non-adversarial Simulator is used.
        :type adversarial_scenario: Optional[Union[AdversarialScenario, AdversarialScenarioJailbreak]]
        :param source_text: The source text to use as grounding document in the simulation.
        :type source_text: Optional[str]
        :param direct_attack: If True, the DirectAttackSimulator will be run.
        :type direct_attack: bool
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
        data_path = "simulator_outputs.jsonl"
        simulator_outputs = None
        jailbreak_outputs = None
        simulator_data_paths = {}

        # if IndirectAttack, run IndirectAttackSimulator
        if adversarial_scenario == AdversarialScenarioJailbreak.ADVERSARIAL_INDIRECT_JAILBREAK:
            self.logger.info(f"Running IndirectAttackSimulator with inputs: adversarial_scenario={adversarial_scenario}, max_conversation_turns={max_conversation_turns}, max_simulation_results={max_simulation_results}, conversation_turns={conversation_turns}, text={source_text}")
            simulator = IndirectAttackSimulator(azure_ai_project=self.azure_ai_project, credential=self.credential)
            simulator_outputs = await simulator(
                scenario=adversarial_scenario,
                max_conversation_turns=max_conversation_turns,
                max_simulation_results=max_simulation_results,
                conversation_turns=conversation_turns,
                text=source_text,
                target=callback,
            )
            
        # if DirectAttack, run DirectAttackSimulator
        elif direct_attack:
            self.logger.info(f"Running DirectAttackSimulator with inputs: adversarial_scenario={adversarial_scenario}, max_conversation_turns={max_conversation_turns}, max_simulation_results={max_simulation_results}")
            simulator = DirectAttackSimulator(azure_ai_project=self.azure_ai_project, credential=self.credential)
            simulator_outputs = await simulator(
                scenario=adversarial_scenario if adversarial_scenario else AdversarialScenario.ADVERSARIAL_REWRITE,
                max_conversation_turns=max_conversation_turns,
                max_simulation_results=max_simulation_results,
                target=callback)
            jailbreak_outputs = simulator_outputs["jailbreak"]
            simulator_outputs = simulator_outputs["regular"]
        
        ## If adversarial_scenario is not provided, run Simulator
        elif adversarial_scenario is None:
            self.logger.info(f"Running Simulator with inputs: adversarial_scenario={adversarial_scenario}, max_conversation_turns={max_conversation_turns}, max_simulation_results={max_simulation_results}, conversation_turns={conversation_turns}, source_text={source_text}")
            simulator = Simulator(self.model_config)
            simulator_outputs = await simulator(
                max_conversation_turns=max_conversation_turns,
                max_simulation_results=max_simulation_results,
                conversation_turns=conversation_turns,
                target=callback,
                text=source_text if source_text else "",
            )

        ## Run AdversarialSimulator
        elif adversarial_scenario:
            self.logger.info(f"Running AdversarialSimulator with inputs: adversarial_scenario={adversarial_scenario}, max_conversation_turns={max_conversation_turns}, max_simulation_results={max_simulation_results}, conversation_turns={conversation_turns}, source_text={source_text}")
            simulator = AdversarialSimulator(azure_ai_project=self.azure_ai_project, credential=self.credential)
            simulator_outputs = await simulator(
                scenario=adversarial_scenario,
                max_conversation_turns=max_conversation_turns,
                max_simulation_results=max_simulation_results,
                conversation_turns=conversation_turns,
                target=callback,
                text=source_text,
            )

        ## If no outputs are generated, raise an exception
        if not simulator_outputs:
            self.logger.error("No outputs generated by the simulator")
            msg = "No outputs generated by the simulator"
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.ADVERSARIAL_SIMULATOR,
                category=ErrorCategory.UNKNOWN,
                blame=ErrorBlame.USER_ERROR,
            )
        
        ## Write outputs to file according to scenario
        if direct_attack and jailbreak_outputs:
            jailbreak_data_path = "jailbreak_simulator_outputs.jsonl"
            with Path(jailbreak_data_path).open("w") as f:
                f.writelines(jailbreak_outputs.to_eval_qr_json_lines())
            simulator_data_paths["jailbreak"] = jailbreak_data_path
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
            simulator_data_paths["regular"] = data_path
            
        return simulator_data_paths

    def _get_evaluators(
            self,
            evaluators: List[_DSBEvaluator], 
    ) -> Dict[str, Callable]:
        '''
        Returns a dictionary of evaluators based on the provided list of DSBEvaluator.

        :param evaluators: A list of DSBEvaluator.
        :type evaluators: List[DSBEvaluator]
        '''
        evaluators_dict = {}
        for evaluator in evaluators:
            if evaluator == _DSBEvaluator.CONTENT_SAFETY:
                evaluators_dict["content_safety"] = _content_safety.ContentSafetyEvaluator(
                    azure_ai_project=self.azure_ai_project, credential=self.credential
                )
            elif evaluator == _DSBEvaluator.GROUNDEDNESS:
                evaluators_dict["groundedness"] = _groundedness.GroundednessEvaluator(
                    model_config=self.model_config,
                )
            elif evaluator == _DSBEvaluator.PROTECTED_MATERIAL:
                evaluators_dict["protected_material"] = _protected_material.ProtectedMaterialEvaluator(
                    azure_ai_project=self.azure_ai_project, credential=self.credential
                )
            elif evaluator == _DSBEvaluator.RELEVANCE:
                evaluators_dict["relevance"] = _relevance.RelevanceEvaluator(
                    model_config=self.model_config,
                )
            elif evaluator == _DSBEvaluator.SIMILARITY:
                evaluators_dict["similarity"] = _similarity.SimilarityEvaluator(
                    model_config=self.model_config,
                )
            elif evaluator == _DSBEvaluator.FLUENCY:
                evaluators_dict["fluency"] = _fluency.FluencyEvaluator(
                    model_config=self.model_config,
                )
            elif evaluator == _DSBEvaluator.INDIRECT_ATTACK:
                evaluators_dict["indirect_attack"] = _xpia.IndirectAttackEvaluator(
                    azure_ai_project=self.azure_ai_project, credential=self.credential
                )
            elif evaluator == _DSBEvaluator.DIRECT_ATTACK:
                continue
            else:
                msg = f"Invalid evaluator: {evaluator}. Supported evaluators are: {_DSBEvaluator.__members__.values()}"
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

    def _validate_inputs(
            self,
            evaluators: List[_DSBEvaluator],
            target: Callable,
            source_text: Optional[str] = None,
            adversarial_scenario: Optional[Union[AdversarialScenario, AdversarialScenarioJailbreak]] = None,
    ):
        '''
        Validates the inputs provided to the __call__ function of the DSBEvaluation object.
        :param evaluators: A list of DSBEvaluator.
        :type evaluators: List[DSBEvaluator]
        :param target: The target function to call during the evaluation.
        :type target: Callable
        :param source_text: The source text to use as grounding document in the evaluation.
        :type source_text: Optional[str]
        :param adversarial_scenario: The adversarial scenario to simulate. 
        :type adversarial_scenario: Optional[Union[AdversarialScenario, AdversarialScenarioJailbreak]]
        '''
        if _DSBEvaluator.GROUNDEDNESS in evaluators and not (self._check_target_returns_context(target) or source_text):
            self.logger.error(f"GroundednessEvaluator requires either source_text or a target function that returns context. Source text: {source_text}, _check_target_returns_context: {self._check_target_returns_context(target)}")
            msg = "GroundednessEvaluator requires either source_text or a target function that returns context"
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.GROUNDEDNESS_EVALUATOR,
                category=ErrorCategory.MISSING_FIELD,
                blame=ErrorBlame.USER_ERROR,
            )
        
        if _DSBEvaluator.INDIRECT_ATTACK in evaluators and adversarial_scenario != AdversarialScenarioJailbreak.ADVERSARIAL_INDIRECT_JAILBREAK:
            self.logger.error(f"IndirectAttackEvaluator requires adversarial_scenario to be set to ADVERSARIAL_INDIRECT_JAILBREAK. Adversarial scenario: {adversarial_scenario}")
            msg = "IndirectAttackEvaluator requires adversarial_scenario to be set to ADVERSARIAL_INDIRECT_JAILBREAK"
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.INDIRECT_ATTACK_EVALUATOR,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )
        if evaluators != [_DSBEvaluator.INDIRECT_ATTACK] and adversarial_scenario == AdversarialScenarioJailbreak.ADVERSARIAL_INDIRECT_JAILBREAK:
            self.logger.error(f"IndirectAttackEvaluator should be used when adversarial_scenario is set to ADVERSARIAL_INDIRECT_JAILBREAK. Evaluators {evaluators}")
            msg = "IndirectAttackEvaluator should be used when adversarial_scenario is set to ADVERSARIAL_INDIRECT_JAILBREAK"
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.INDIRECT_ATTACK_EVALUATOR,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )

        if _DSBEvaluator.PROTECTED_MATERIAL in evaluators and adversarial_scenario != AdversarialScenario.ADVERSARIAL_CONTENT_PROTECTED_MATERIAL:
            self.logger.error(f"ProtectedMaterialEvaluator requires adversarial_scenario to be set to ADVERSARIAL_CONTENT_PROTECTED_MATERIAL. Adversarial scenario: {adversarial_scenario}")
            msg = "ProtectedMaterialEvaluator requires adversarial_scenario to be set to ADVERSARIAL_CONTENT_PROTECTED_MATERIAL"
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.PROTECTED_MATERIAL_EVALUATOR,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )
        if evaluators != [_DSBEvaluator.PROTECTED_MATERIAL] and adversarial_scenario == AdversarialScenario.ADVERSARIAL_CONTENT_PROTECTED_MATERIAL:
            self.logger.error(f"ProtectedMaterialEvaluator should be used when adversarial_scenario is set to ADVERSARIAL_CONTENT_PROTECTED_MATERIAL. Evaluators: {evaluators}")
            msg = "ProtectedMaterialEvaluator should be used when adversarial_scenario is set to ADVERSARIAL_CONTENT_PROTECTED_MATERIAL"
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.PROTECTED_MATERIAL_EVALUATOR,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )
        if _DSBEvaluator.DIRECT_ATTACK in evaluators and len(evaluators) == 1:
            self.logger.error("DirectAttack should be used along with other evaluators") 
            msg = "DirectAttack should be used along with other evaluators"
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.DIRECT_ATTACK_SIMULATOR,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )            

    async def __call__(
            self,
            evaluators: List[_DSBEvaluator],
            target: Callable,
            adversarial_scenario: Optional[Union[AdversarialScenario, AdversarialScenarioJailbreak]] = None,
            max_conversation_turns: int = 1,
            max_simulation_results: int = 3,
            conversation_turns : List[List[Union[str, Dict[str, Any]]]] = [],
            source_text: Optional[str] = None,
            data_path: Optional[Union[str, os.PathLike]] = None,
            jailbreak_data_path: Optional[Union[str, os.PathLike]] = None,
            output_path: Optional[Union[str, os.PathLike]] = None
        ) -> Union[EvaluationResult, Dict[str, EvaluationResult]]:
        '''
        Evaluates the target function based on the provided parameters.
        
        :param evaluators: A list of DSBEvaluator.
        :type evaluators: List[_DSBEvaluator]
        :param target: The target function to call during the evaluation.
        :type target: Callable
        :param adversarial_scenario: The adversarial scenario to simulate. If None, the non-adversarial Simulator is used.
        :type adversarial_scenario: Optional[Union[AdversarialScenario, AdversarialScenarioJailbreak]]
        :param max_conversation_turns: The maximum number of turns in a conversation.
        :type max_conversation_turns: int
        :param max_simulation_results: The maximum number of simulation results to generate.
        :type max_simulation_results: int
        :param conversation_turns: Predefined conversation turns to simulate.
        :type conversation_turns: List[List[Union[str, Dict[str, Any]]]]
        :param source_text: The source text to use as grounding document in the evaluation.
        :type source_text: Optional[str]
        :param data_path: The path to the data file generated by the Simulator. If None, the Simulator will be run.
        :type data_path: Optional[Union[str, os.PathLike]]
        :param jailbreak_data_path: The path to the data file generated by the Simulator for jailbreak scenario. If None, the DirectAttackSimulator will be run.
        :type jailbreak_data_path: Optional[Union[str, os.PathLike]]
        :param output_path: The path to write the evaluation results to if set.
        :type output_path: Optional[Union[str, os.PathLike]]
        '''
        ## Log inputs 
        self.logger.info(f"User inputs: evaluators{evaluators}, adversarial_scenario={adversarial_scenario}, max_conversation_turns={max_conversation_turns}, max_simulation_results={max_simulation_results}, conversation_turns={conversation_turns}, source_text={source_text}, data_path={data_path}, jailbreak_data_path={jailbreak_data_path}, output_path={output_path}")

        ## Validate arguments
        self._validate_inputs(
            evaluators=evaluators, 
            target=target, 
            source_text=source_text,
            adversarial_scenario=adversarial_scenario
        )

        ## If `data_path` is not provided, run simulator
        if data_path is None and jailbreak_data_path is None:
            self.logger.info(f"No data_path provided. Running simulator.")
            data_paths = await self._simulate_dsb(
                target=target,
                adversarial_scenario=adversarial_scenario,
                max_conversation_turns=max_conversation_turns,
                max_simulation_results=max_simulation_results,
                conversation_turns=conversation_turns,
                source_text=source_text,
                direct_attack=_DSBEvaluator.DIRECT_ATTACK in evaluators
            )
            data_path = data_paths.get("regular", None)
            jailbreak_data_path = data_paths.get("jailbreak", None)

        ## Get evaluators
        evaluators_dict = self._get_evaluators(evaluators)
        evaluation_results = {}

        ## Run evaluation
        if _DSBEvaluator.DIRECT_ATTACK in evaluators and jailbreak_data_path:
            self.logger.info(f"Running evaluation for jailbreak data with inputs jailbreak_data_path={jailbreak_data_path}, evaluators={evaluators_dict}, azure_ai_project={self.azure_ai_project}, output_path=jailbreak_{output_path}, credential={self.credential}")
            evaluate_outputs_jailbreak = _evaluate.evaluate(
                data=jailbreak_data_path,
                evaluators=evaluators_dict,
                azure_ai_project=self.azure_ai_project,
                output_path=Path("jailbreak_" + str(output_path)),
                credential=self.credential,
            )
            evaluation_results["jailbreak"] = evaluate_outputs_jailbreak

        if data_path:
            self.logger.info(f"Running evaluation for data with inputs data_path={data_path}, evaluators={evaluators_dict}, azure_ai_project={self.azure_ai_project}, output_path={output_path}")
            evaluate_outputs = _evaluate.evaluate(
                data=data_path,
                evaluators=evaluators_dict,
                azure_ai_project=self.azure_ai_project,
                output_path=output_path,
            )
            if _DSBEvaluator.DIRECT_ATTACK in evaluators:
                evaluation_results["regular"] = evaluate_outputs
            else: 
                return evaluate_outputs
        return evaluation_results