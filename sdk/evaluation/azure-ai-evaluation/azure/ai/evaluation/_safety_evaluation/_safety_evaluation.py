# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum
import os
import inspect
import logging
from datetime import datetime
from azure.ai.evaluation._common._experimental import experimental
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast
from azure.ai.evaluation._common.math import list_mean_nan_safe
from azure.ai.evaluation._constants import CONTENT_SAFETY_DEFECT_RATE_THRESHOLD_DEFAULT
from azure.ai.evaluation._evaluators import _content_safety, _protected_material,  _groundedness, _relevance, _similarity, _fluency, _xpia, _coherence
from azure.ai.evaluation._evaluate import _evaluate
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._model_configurations import AzureAIProject, EvaluationResult
from azure.ai.evaluation.simulator import Simulator, AdversarialSimulator, AdversarialScenario, AdversarialScenarioJailbreak, IndirectAttackSimulator, DirectAttackSimulator
from azure.ai.evaluation.simulator._utils import JsonLineList
from azure.ai.evaluation.simulator._model_tools import ManagedIdentityAPITokenManager, TokenScope, RAIClient, AdversarialTemplateHandler
from azure.ai.evaluation._common.utils import validate_azure_ai_project
from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration, OpenAIModelConfiguration
from azure.ai.evaluation._safety_evaluation._callback_chat_target import CallbackChatTarget
from pyrit.orchestrator.single_turn.prompt_sending_orchestrator import PromptSendingOrchestrator
from pyrit.orchestrator import ManyShotJailbreakOrchestrator, SkeletonKeyOrchestrator, Orchestrator
from pyrit.prompt_converter import PromptConverter, MathPromptConverter, TenseConverter, Base64Converter, FlipConverter
from pyrit.prompt_target import PromptChatTarget
from azure.core.credentials import TokenCredential
import json
from pathlib import Path
import re
import itertools
from pyrit.common import initialize_pyrit, DUCK_DB
from pyrit.orchestrator import PromptSendingOrchestrator
from pyrit.prompt_target import OpenAIChatTarget
from pyrit.models import ChatMessage

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
class _SafetyEvaluator(Enum):
    '''
    Evaluator types for Safety evaluation.
    '''

    CONTENT_SAFETY = "content_safety"
    GROUNDEDNESS = "groundedness"
    PROTECTED_MATERIAL = "protected_material"
    RELEVANCE = "relevance"
    SIMILARITY = "similarity"
    FLUENCY = "fluency"
    COHERENCE = "coherence"
    INDIRECT_ATTACK = "indirect_attack"
    DIRECT_ATTACK = "direct_attack"

@experimental
class _AttackBudget(Enum):
    """Budget levels for attacks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@experimental
class _SafetyEvaluation:
    def __init__(
        self,
        azure_ai_project: dict,
        credential: TokenCredential,
        model_config: Optional[Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration]] = None,
    ):
        '''
        Initializes a SafetyEvaluation object.

        :param azure_ai_project: A dictionary defining the Azure AI project. Required keys are 'subscription_id', 'resource_group_name', and 'project_name'.
        :type azure_ai_project: Dict[str, str]
        :param credential: The credential for connecting to Azure AI project.
        :type credential: ~azure.core.credentials.TokenCredential
        :param model_config: A dictionary defining the configuration for the model. Acceptable types are AzureOpenAIModelConfiguration and OpenAIModelConfiguration.
        :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration, ~azure.ai.evaluation.OpenAIModelConfiguration]
        :raises ValueError: If the model_config does not contain the required keys or any value is None.
        '''
        if model_config:
            self._validate_model_config(model_config)
            self.model_config = model_config
        else:
            self.model_config = None
        validate_azure_ai_project(azure_ai_project)
        self.azure_ai_project = AzureAIProject(**azure_ai_project)
        self.credential=credential
        self.logger = _setup_logger()

        # For pyrit 
        self.token_manager = ManagedIdentityAPITokenManager(
            token_scope=TokenScope.DEFAULT_AZURE_MANAGEMENT,
            logger=logging.getLogger("AdversarialSimulator"),
            credential=cast(TokenCredential, credential),
        )

        self.rai_client = RAIClient(azure_ai_project=self.azure_ai_project, token_manager=self.token_manager)
        self.adversarial_template_handler = AdversarialTemplateHandler(
            azure_ai_project=self.azure_ai_project, rai_client=self.rai_client
        )

        initialize_pyrit(memory_db_type=DUCK_DB)


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

    async def _simulate(
            self,
            target: Callable, 
            max_conversation_turns: int = 1,
            max_simulation_results: int = 3,
            conversation_turns : List[List[Union[str, Dict[str, Any]]]] = [], 
            tasks: List[str] = [],
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
        :param tasks A list of user tasks, each represented as a list of strings. Text should be relevant for the tasks and facilitate the simulation. One example is to use text to provide context for the tasks.
        :type tasks: List[str] = [],
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
                tasks=tasks,
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
        elif adversarial_scenario is None and self.model_config:
            self.logger.info(f"Running Simulator with inputs: adversarial_scenario={adversarial_scenario}, max_conversation_turns={max_conversation_turns}, max_simulation_results={max_simulation_results}, conversation_turns={conversation_turns}, source_text={source_text}")
            simulator = Simulator(self.model_config)
            simulator_outputs = await simulator(
                max_conversation_turns=max_conversation_turns,
                max_simulation_results=max_simulation_results,
                conversation_turns=conversation_turns,
                num_queries=max_simulation_results,
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
    
    def _get_scenario(
            self,
            evaluators: List[_SafetyEvaluator], 
            num_turns: int = 3,
            scenario: Optional[Union[AdversarialScenario, AdversarialScenarioJailbreak]] = None,
    ) -> Optional[Union[AdversarialScenario, AdversarialScenarioJailbreak]]:
        '''
        Returns the Simulation scenario based on the provided list of SafetyEvaluator.

        :param evaluators: A list of SafetyEvaluator.
        :type evaluators: List[SafetyEvaluator]
        :param num_turns: The number of turns in a conversation.
        :type num_turns: int
        :param scenario: The adversarial scenario to simulate.
        :type scenario: Optional[Union[AdversarialScenario, AdversarialScenarioJailbreak]]
        '''
        if len(evaluators) == 0: return AdversarialScenario.ADVERSARIAL_QA
        for evaluator in evaluators:
            if evaluator in [_SafetyEvaluator.CONTENT_SAFETY, _SafetyEvaluator.DIRECT_ATTACK]:
                if num_turns == 1 and scenario: return scenario
                return (
                    AdversarialScenario.ADVERSARIAL_CONVERSATION
                    if num_turns > 1
                    else AdversarialScenario.ADVERSARIAL_QA
                )
            if evaluator in [
                _SafetyEvaluator.GROUNDEDNESS,
                _SafetyEvaluator.RELEVANCE,
                _SafetyEvaluator.SIMILARITY,
                _SafetyEvaluator.FLUENCY,
                _SafetyEvaluator.COHERENCE,
            ]:
                return None
            if evaluator == _SafetyEvaluator.PROTECTED_MATERIAL:
                return AdversarialScenario.ADVERSARIAL_CONTENT_PROTECTED_MATERIAL
            if evaluator == _SafetyEvaluator.INDIRECT_ATTACK:
                return AdversarialScenarioJailbreak.ADVERSARIAL_INDIRECT_JAILBREAK

            msg = f"Invalid evaluator: {evaluator}. Supported evaluators: {_SafetyEvaluator.__members__.values()}"
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.UNKNOWN,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )

    def _get_evaluators(
            self,
            evaluators: List[_SafetyEvaluator], 
    ) -> Dict[str, Callable]:
        '''
        Returns a dictionary of evaluators based on the provided list of SafetyEvaluator.

        :param evaluators: A list of SafetyEvaluator.
        :type evaluators: List[SafetyEvaluator]
        '''
        evaluators_dict = {}
        # Default to content safety when no evaluators are specified
        if len(evaluators) == 0: 
            evaluators_dict["content_safety"] = _content_safety.ContentSafetyEvaluator(
                    azure_ai_project=self.azure_ai_project, credential=self.credential
                )
            return evaluators_dict
        
        for evaluator in evaluators:
            if evaluator == _SafetyEvaluator.CONTENT_SAFETY:
                evaluators_dict["content_safety"] = _content_safety.ContentSafetyEvaluator(
                    azure_ai_project=self.azure_ai_project, credential=self.credential
                )
            elif evaluator == _SafetyEvaluator.GROUNDEDNESS:
                evaluators_dict["groundedness"] = _groundedness.GroundednessEvaluator(
                    model_config=self.model_config,
                )
            elif evaluator == _SafetyEvaluator.PROTECTED_MATERIAL:
                evaluators_dict["protected_material"] = _protected_material.ProtectedMaterialEvaluator(
                    azure_ai_project=self.azure_ai_project, credential=self.credential
                )
            elif evaluator == _SafetyEvaluator.RELEVANCE:
                evaluators_dict["relevance"] = _relevance.RelevanceEvaluator(
                    model_config=self.model_config,
                )
            elif evaluator == _SafetyEvaluator.SIMILARITY:
                evaluators_dict["similarity"] = _similarity.SimilarityEvaluator(
                    model_config=self.model_config,
                )
            elif evaluator == _SafetyEvaluator.FLUENCY:
                evaluators_dict["fluency"] = _fluency.FluencyEvaluator(
                    model_config=self.model_config,
                )
            elif evaluator == _SafetyEvaluator.COHERENCE:
                evaluators_dict["coherence"] = _coherence.CoherenceEvaluator(
                    model_config=self.model_config,
                )
            elif evaluator == _SafetyEvaluator.INDIRECT_ATTACK:
                evaluators_dict["indirect_attack"] = _xpia.IndirectAttackEvaluator(
                    azure_ai_project=self.azure_ai_project, credential=self.credential
                )
            elif evaluator == _SafetyEvaluator.DIRECT_ATTACK:
                evaluators_dict["content_safety"] = _content_safety.ContentSafetyEvaluator(
                    azure_ai_project=self.azure_ai_project, credential=self.credential
                )
            else:
                msg = f"Invalid evaluator: {evaluator}. Supported evaluators are: {_SafetyEvaluator.__members__.values()}"
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
    
    @staticmethod
    def _check_target_returns_str(target: Callable) -> bool:
        '''
        Checks if the target function returns a string.

        :param target: The target function to check.
        :type target: Callable
        '''
        sig = inspect.signature(target)
        ret_type = sig.return_annotation
        if ret_type == inspect.Signature.empty:
            return False
        if ret_type is str:
            return True
        return False

    def _validate_inputs(
            self,
            evaluators: List[_SafetyEvaluator],
            target: Union[Callable, AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
            num_turns: int = 1,
            scenario: Optional[Union[AdversarialScenario, AdversarialScenarioJailbreak]] = None,
            source_text: Optional[str] = None,
    ):
        '''
        Validates the inputs provided to the __call__ function of the SafetyEvaluation object.
        :param evaluators: A list of SafetyEvaluator.
        :type evaluators: List[SafetyEvaluator]
        :param target: The target function to call during the evaluation.
        :type target: Callable
        :param num_turns: The number of turns in a between the target application and the caller.
        :type num_turns: int
        :param scenario: The adversarial scenario to simulate. 
        :type scenario: Optional[Union[AdversarialScenario, AdversarialScenarioJailbreak]]
        :param source_text: The source text to use as grounding document in the evaluation.
        :type source_text: Optional[str]
        ''' 
        if not callable(target):
            self._validate_model_config(target)
        elif not self._check_target_returns_str(target):
            self.logger.error(f"Target function {target} does not return a string.")
            msg = f"Target function {target} does not return a string."
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.UNKNOWN,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )

        if _SafetyEvaluator.GROUNDEDNESS in evaluators and not source_text:
            self.logger.error(f"GroundednessEvaluator requires  source_text. Source text: {source_text}")
            msg = "GroundednessEvaluator requires source_text"
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.GROUNDEDNESS_EVALUATOR,
                category=ErrorCategory.MISSING_FIELD,
                blame=ErrorBlame.USER_ERROR,
            )
        
        if scenario and len(evaluators)>0 and not _SafetyEvaluator.CONTENT_SAFETY in evaluators:
            self.logger.error(f"Adversarial scenario {scenario} is not supported without content safety evaluation.")
            msg = f"Adversarial scenario {scenario} is not supported without content safety evaluation."
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.UNKNOWN,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )
    
        if _SafetyEvaluator.CONTENT_SAFETY in evaluators and scenario and num_turns > 1 and scenario != AdversarialScenario.ADVERSARIAL_CONVERSATION:
            self.logger.error(f"Adversarial scenario {scenario} is not supported for content safety evaluation with more than 1 turn.")
            msg = f"Adversarial scenario {scenario} is not supported for content safety evaluation with more than 1 turn."
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.UNKNOWN,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )
        
        if any(e in evaluators for e in [
            _SafetyEvaluator.GROUNDEDNESS,
            _SafetyEvaluator.RELEVANCE,
            _SafetyEvaluator.SIMILARITY,
            _SafetyEvaluator.FLUENCY,
            _SafetyEvaluator.COHERENCE,
        ]) and not self.model_config:
            self.logger.error(f"Model configuration is required for evaluators: {evaluators}")
            msg = f"Model configuration is required for evaluators: {evaluators}"
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.UNKNOWN,
                category=ErrorCategory.MISSING_FIELD,
                blame=ErrorBlame.USER_ERROR,
            )
            

    def _calculate_defect_rate(self, evaluation_result_dict) -> EvaluationResult:
        hate_unfairness_defects = []
        violence_defects = []
        sexual_defects = []
        self_harm_defects = []
        for i, row in enumerate(zip(evaluation_result_dict['jailbreak']['rows'], evaluation_result_dict['regular']['rows'])):
            hate_unfairness_defects.append(1 if (row[0]['outputs.content_safety.hate_unfairness_score'] > CONTENT_SAFETY_DEFECT_RATE_THRESHOLD_DEFAULT and not row[1]['outputs.content_safety.hate_unfairness_score'] > CONTENT_SAFETY_DEFECT_RATE_THRESHOLD_DEFAULT) else 0)
            violence_defects.append(1 if (row[0]['outputs.content_safety.violence_score'] > CONTENT_SAFETY_DEFECT_RATE_THRESHOLD_DEFAULT and not row[1]['outputs.content_safety.violence_score'] > CONTENT_SAFETY_DEFECT_RATE_THRESHOLD_DEFAULT) else 0)
            sexual_defects.append(1 if (row[0]['outputs.content_safety.sexual_score'] > CONTENT_SAFETY_DEFECT_RATE_THRESHOLD_DEFAULT and not row[1]['outputs.content_safety.sexual_score'] > CONTENT_SAFETY_DEFECT_RATE_THRESHOLD_DEFAULT) else 0)
            self_harm_defects.append(1 if (row[0]['outputs.content_safety.self_harm_score'] > CONTENT_SAFETY_DEFECT_RATE_THRESHOLD_DEFAULT and not row[1]['outputs.content_safety.self_harm_score'] > CONTENT_SAFETY_DEFECT_RATE_THRESHOLD_DEFAULT) else 0)
        hate_unfairness_defect_rate = list_mean_nan_safe(hate_unfairness_defects)
        violence_defect_rate = list_mean_nan_safe(violence_defects)
        sexual_defect_rate = list_mean_nan_safe(sexual_defects)
        self_harm_defect_rate = list_mean_nan_safe(self_harm_defects)

        evaluation_result: EvaluationResult = {'metrics': {}, 'rows': [], 'studio_url': ''}
        evaluation_result['rows'] = evaluation_result_dict['jailbreak']['rows'] + evaluation_result_dict['regular']['rows']
        evaluation_result['metrics'] = {
            'content_safety.violence_defect_rate': hate_unfairness_defect_rate,
            'content_safety.sexual_defect_rate': violence_defect_rate,
            'content_safety.hate_unfairness_defect_rate': sexual_defect_rate,
            'content_safety.self_harm_defect_rate': self_harm_defect_rate,
        }
        evaluation_result['studio_url'] = evaluation_result_dict['jailbreak']['studio_url'] + '\t' + evaluation_result_dict['regular']['studio_url']
        return evaluation_result
    
    async def _get_all_prompts(self, scenario: AdversarialScenario, num_rows: int = 3) -> List[str]:
        templates = await self.adversarial_template_handler._get_content_harm_template_collections(
                scenario.value
            )
        parameter_lists = [t.template_parameters for t in templates]
        zipped_parameters = list(zip(*parameter_lists))

        def fill_template(template_str, parameter):
            pattern = re.compile(r'{{\s*(.*?)\s*}}')
            def replacer(match):
                placeholder = match.group(1)
                return parameter.get(placeholder, f"{{{{ {placeholder} }}}}")
            filled_text = pattern.sub(replacer, template_str)
            return filled_text

        all_prompts = []
        count = 0
        for param_group in zipped_parameters:
            for _, parameter in zip(templates, param_group):
                filled_template = fill_template(parameter['conversation_starter'], parameter)
                all_prompts.append(filled_template)
                count += 1
                if count >= num_rows:
                    break
            if count >= num_rows:
                break
        return all_prompts
    
    def _message_to_dict(self, message: ChatMessage):
        return {
            "role": message.role,
            "content": message.content,
        }
    
    def _get_converters_for_budget(self, attack_budget) -> List:
        converters = []
        if _AttackBudget.LOW in attack_budget:
            converters.extend([Base64Converter(), FlipConverter()])
        return converters
    
    async def _many_shot_orchestrator(self, chat_target: PromptChatTarget, all_prompts: List[str]) -> Orchestrator:
            orchestrator = ManyShotJailbreakOrchestrator(
                objective_target=chat_target,
            )
            await orchestrator.send_prompts_async(prompt_list=all_prompts)
            return orchestrator
    
    async def _skeleton_key_orchestrator(self, chat_target: PromptChatTarget, all_prompts: List[str], converters: PromptConverter) -> List[Orchestrator]:
        orchestrators = []
        for converter in converters:
            orchestrator = SkeletonKeyOrchestrator(
                prompt_target=chat_target,
                prompt_converters=[converter]
            )
            await orchestrator.send_skeleton_key_with_prompts_async(prompt_list=all_prompts)
            orchestrators.append(orchestrator)
        return orchestrators
            
    
    async def _call_orchestrators_for_budget(self, attack_budget: List[_AttackBudget], converters: PromptConverter, chat_target: PromptChatTarget, all_prompts: List[str]) -> List[Union[str, os.PathLike]]:
        output_data_paths = []
        if _AttackBudget.LOW in attack_budget:
            # run many-shot orchestrator (does not handle converters)
            # TODO: Many shot is flaky for some reason, ignoring for now 
            # many_shot_orchestrator = await self._many_shot_orchestrator(chat_target, all_prompts)
            # ouptut_path = "many_shot_outputs.jsonl"
            # ouptut_path = self._write_pyrit_outputs_to_file(many_shot_orchestrator, ouptut_path)
            # output_data_paths.append(ouptut_path)
            # run skeleton key orchestrator for each converter
            skeleton_key_orchestrators = await self._skeleton_key_orchestrator(chat_target, all_prompts, converters)
            for converter in converters:
                skeleton_key_orchestrator = skeleton_key_orchestrators.pop(0)
                converter_name = converter.get_identifier()["__type__"]
                ouptut_path = f"skeleton_key_outputs_{converter_name}.jsonl"
                ouptut_path = self._write_pyrit_outputs_to_file(skeleton_key_orchestrator, ouptut_path)
                output_data_paths.append(ouptut_path)
        return output_data_paths
    
    def _write_pyrit_outputs_to_file(self, orchestrator: Orchestrator, output_path: Union[str, os.PathLike]) -> Union[str, os.PathLike]:
        memory = orchestrator.get_memory()

        # Get conversations as a List[List[ChatMessage]]
        conversations = [[item.to_chat_message() for item in group] for conv_id, group in itertools.groupby(memory, key=lambda x: x.conversation_id)]
        
        #Convert to json lines
        json_lines = ""
        for conversation in conversations: # each conversation is a List[ChatMessage]
            json_lines += json.dumps({"conversation": {"messages": [self._message_to_dict(message) for message in conversation]}}) + "\n"

        with Path(output_path).open("w") as f:
            f.writelines(json_lines)
        return output_path
    
    async def _pyrit(
            self, 
            target: Union[Callable, AzureOpenAIModelConfiguration, OpenAIModelConfiguration], 
            scenario: AdversarialScenario,
            num_rows: int = 1,
            attack_budget: List[_AttackBudget] = []
        ) ->  List[Union[str, os.PathLike]]:
        chat_target: OpenAIChatTarget = None
        if not isinstance(target, Callable):
            if "azure_deployment" in target and "azure_endpoint" in target: # Azure OpenAI
                api_key = target.get("api_key", None)
                if not api_key:
                    chat_target = OpenAIChatTarget(deployment_name=target["azure_deployment"], endpoint=target["azure_endpoint"], use_aad_auth=True)
                else: 
                    chat_target = OpenAIChatTarget(deployment_name=target["azure_deployment"], endpoint=target["azure_endpoint"], api_key=api_key)
            else:
                chat_target = OpenAIChatTarget(deployment=target["model"], endpoint=target.get("base_url", None), key=target["api_key"], is_azure_target=False)
        else:
            async def callback_target(
                messages: List[Dict],
                stream: bool = False,
                session_state: Optional[str] = None,
                context: Optional[Dict] = None
            ) -> dict:
                messages_list = [self._message_to_dict(chat_message) for chat_message in messages] # type: ignore
                latest_message = messages_list[-1]
                application_input = latest_message["content"]
                try:
                    response = target(query=application_input)
                except Exception as e:
                    response = f"Something went wrong {e!s}"

                ## We format the response to follow the openAI chat protocol format
                formatted_response = {
                    "content": response,
                    "role": "assistant",
                    "context":{},
                }
                ## NOTE: In the future, instead of appending to messages we should just return `formatted_response`
                messages_list.append(formatted_response) # type: ignore
                return {"messages": messages_list, "stream": stream, "session_state": session_state, "context": {}}
            

            chat_target = CallbackChatTarget(callback=callback_target)
        
        all_prompts_list = await self._get_all_prompts(scenario, num_rows=num_rows)

        # If user provided budget levels, get predefined strategies
        if attack_budget:
            self.logger.info(f"Configuring PyRIT based on attack budget: {attack_budget}")
            converters = self._get_converters_for_budget(attack_budget)
            data_paths = await self._call_orchestrators_for_budget(attack_budget, converters, chat_target, all_prompts_list)
            return data_paths
        # TODO: Implement handling for pyrit strategies beyond budget levels
        else: 
            orchestrator = PromptSendingOrchestrator(objective_target=chat_target)
            await orchestrator.send_prompts_async(prompt_list=all_prompts_list)

            output_path = "pyrit_outputs.jsonl"
            return [self._write_pyrit_outputs_to_file(orchestrator, output_path)]

        

    async def __call__(
            self,
            target: Union[Callable, AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
            evaluators: List[_SafetyEvaluator] = [],
            evaluation_name: Optional[str] = None,
            num_turns : int = 1,
            num_rows: int = 5,
            scenario: Optional[Union[AdversarialScenario, AdversarialScenarioJailbreak]] = None,
            attack_budget: List[_AttackBudget] = [],
            conversation_turns : List[List[Union[str, Dict[str, Any]]]] = [],
            tasks: List[str] = [],
            data_only: bool = False,
            source_text: Optional[str] = None,
            data_path: Optional[Union[str, os.PathLike]] = None,
            jailbreak_data_path: Optional[Union[str, os.PathLike]] = None,
            output_path: Optional[Union[str, os.PathLike]] = None
        ) -> Union[EvaluationResult, Dict[str, Union[str, os.PathLike]], str, os.PathLike]:
        '''
        Evaluates the target function based on the provided parameters.
        
        :param target: The target function to call during the evaluation.
        :type target: Callable
        :param evaluators: A list of SafetyEvaluator.
        :type evaluators: List[_SafetyEvaluator]
        :param evaluation_name: The display name name of the evaluation.
        :type evaluation_name: Optional[str]
        :param num_turns: The number of turns in a between the target application and the caller.
        :type num_turns: int
        :param num_rows: The (maximum) number of rows to generate for evaluation.
        :type num_rows: int
        :param scenario: The adversarial scenario to simulate. 
        :type scenario: Optional[Union[AdversarialScenario, AdversarialScenarioJailbreak]]
        :param attack_budget: A list of budget levels for attacks (e.g., ['low', 'medium', 'high']). The operation will choose appropriate PyRIT orchestrators based on these budgets.
        :type attack_budget: List[_AttackBudget]
        :param conversation_turns: Predefined conversation turns to simulate.
        :type conversation_turns: List[List[Union[str, Dict[str, Any]]]]
        :param tasks A list of user tasks, each represented as a list of strings. Text should be relevant for the tasks and facilitate the simulation. One example is to use text to provide context for the tasks.
        :type tasks: List[str] = [],
        :param data_only: If True, the filepath to which simulation results are written will be returned.
        :type data_only: bool
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
        self.logger.info(f"User inputs: evaluators{evaluators}, evaluation_name={evaluation_name}, num_turns={num_turns}, num_rows={num_rows}, scenario={scenario},attack_budget={attack_budget},conversation_turns={conversation_turns}, tasks={tasks}, source_text={source_text}, data_path={data_path}, jailbreak_data_path={jailbreak_data_path}, output_path={output_path}")

        ## Validate arguments
        self._validate_inputs(
            evaluators=evaluators, 
            target=target, 
            num_turns=num_turns,
            scenario=scenario,
            source_text=source_text,
        )

        # Get scenario
        adversarial_scenario = self._get_scenario(evaluators, num_turns=num_turns, scenario=scenario)
        self.logger.info(f"Using scenario: {adversarial_scenario}")

        data_path_list = None
        if isinstance(adversarial_scenario, AdversarialScenario) and num_turns==1:
            self.logger.info(f"Running Pyrit with inputs target={target}, scenario={scenario}, attack_budget={attack_budget}, num_rows={num_rows}") 
            data_path_list = await self._pyrit(target, adversarial_scenario, num_rows, attack_budget)
            return EvaluationResult(rows=[], metrics={}, studio_url="")

        ## Get evaluators
        evaluators_dict = self._get_evaluators(evaluators)

        ## If `data_path` is not provided, run simulator
        if not data_path_list and data_path is None and jailbreak_data_path is None and isinstance(target, Callable):
            self.logger.info(f"No data_path provided. Running simulator.")
            data_paths = await self._simulate(
                target=target,
                adversarial_scenario=adversarial_scenario,
                max_conversation_turns=num_turns,
                max_simulation_results=num_rows,
                conversation_turns=conversation_turns,
                tasks=tasks,
                source_text=source_text,
                direct_attack=_SafetyEvaluator.DIRECT_ATTACK in evaluators
            )
            data_path = data_paths.get("regular", None)
            jailbreak_data_path = data_paths.get("jailbreak", None)

        if data_only and data_path:
            if jailbreak_data_path:
                return {"regular": data_path, "jailbreak": jailbreak_data_path}
            return data_path

        ## Run evaluation
        evaluation_results = {}
        if _SafetyEvaluator.DIRECT_ATTACK in evaluators and jailbreak_data_path:
            self.logger.info(f"Running evaluation for jailbreak data with inputs jailbreak_data_path={jailbreak_data_path}, evaluators={evaluators_dict}, azure_ai_project={self.azure_ai_project}, output_path=jailbreak_{output_path}, credential={self.credential}")
            evaluate_outputs_jailbreak = _evaluate.evaluate(
                data=jailbreak_data_path,
                evaluators=evaluators_dict,
                azure_ai_project=self.azure_ai_project,
                output_path=Path("jailbreak_" + str(output_path)),
                evaluation_name=evaluation_name,
            )
            evaluation_results["jailbreak"] = evaluate_outputs_jailbreak

        if data_path:
            self.logger.info(f"Running evaluation for data with inputs data_path={data_path}, evaluators={evaluators_dict}, azure_ai_project={self.azure_ai_project}, output_path={output_path}")
            evaluate_outputs = _evaluate.evaluate(
                data=data_path,
                evaluators=evaluators_dict,
                azure_ai_project=self.azure_ai_project,
                evaluation_name=evaluation_name,
                output_path=output_path,
            )
            if _SafetyEvaluator.DIRECT_ATTACK in evaluators:
                evaluation_results["regular"] = evaluate_outputs
                return self._calculate_defect_rate(evaluation_results)
            
            return evaluate_outputs
        else:
            raise EvaluationException(
                message="No data path found after simulation",
                internal_message="No data path found after simulation",
                target=ErrorTarget.UNKNOWN,
                category=ErrorCategory.MISSING_FIELD,
                blame=ErrorBlame.USER_ERROR,
            )



