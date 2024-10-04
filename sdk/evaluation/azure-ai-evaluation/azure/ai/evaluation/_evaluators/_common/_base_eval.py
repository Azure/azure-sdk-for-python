# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Dict, Callable, Any
import inspect

from abc import ABC

from promptflow._utils.async_utils import async_run_allowing_running_loop

from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from azure.ai.evaluation._common.math import list_mean


# TODO exception target pass down?
class EvaluatorBase(ABC):
    """Base class for all evaluators that are capable of accepting either a group of single values,
    or conversation as input. All such evaluators need to implement two functions of their own:
        - _convert_conversation_to_eval_input
        - _do_eval

    Additionally, __call__ should be overridden to reshape the function header as needed to produce more informative
    documentation, although ideally the actual child implementation of __call__ should just amount to
    'super().__init__()'.


    :param not_singleton_inputs: A list of strings that represent the names of
        inputs to the child evaluator's __call__ function that are NOT singleton inputs. By default, this
        is ["conversation", "kwargs"].
    :type not_singleton_inputs: List[str]
    :param eval_last_turn: If True, only the last turn of the conversation will be evaluated. Default is False.
    :type eval_last_turn: bool
    """

    # ~~~ METHODS THAT ALMOST ALWAYS NEED TO BE OVERRIDDEN BY CHILDREN~~~

    # Make sure to call super().__init__() in the child class's __init__ method.
    # pylint: disable=dangerous-default-value
    def __init__(
        self,
        *,
        not_singleton_inputs: List[str] = ["conversation", "kwargs"],
        eval_last_turn: bool = False,
    ):
        self._not_singleton_inputs = not_singleton_inputs
        self._eval_last_turn = eval_last_turn
        self._singleton_inputs = self._derive_singleton_inputs()
        self._async_evaluator = AsyncEvaluatorBase(self._real_call)

    # This needs to be overridden just to change the function header into something more informative,
    # and to be able to add a more specific docstring. The actual function contents should just be
    # super().__call__(<inputs>)
    def __call__(self, **kwargs) -> Dict:
        """Evaluate a given input. This method serves as a wrapper and is meant to be overridden by child classes for
        one main reason - to overwrite the method headers and docstring to include additional inputs as needed.
        The actual behavior of this function shouldn't change beyond adding more inputs to the
        async_run_allowing_running_loop call.

        :keyword kwargs: A dictionary that contains inputs needed to evaluate a conversation.
        :type kwargs: Dict
        :return: The evaluation result
        :rtype: Dict
        """
        return async_run_allowing_running_loop(self._async_evaluator, **kwargs)

    # Probably the only thing that can't be simplified. Each evaluator, or at least each family
    # of evaluators, will need to implement their own version of this function.
    async def _do_eval(self, eval_input: Any) -> Dict:
        """Evaluate the input and produce a response. Must be overridden to produce a functional evaluator.
        In the default case, all required inputs are assumed to be within eval_input, as user-friendly
        typing is handled above this function in favor of polymorphic simplicity. This function must be
        asynchronous.

        :param eval_input: Whatever inputs are needed for this evaluator to perform a single evaluation.
        :type eval_input: Any
        :return: A single evaluation result
        :rtype: Dict

        """
        raise EvaluationException(
            message="Not implemented",
            internal_message="BaseConversationEval's _do_eval method called somehow. This should be overridden.",
        )

    # ~~~ METHODS THAT MIGHT NEED TO BE OVERRIDDEN BY CHILDREN~~~

    def _derive_singleton_inputs(self) -> List[str]:
        """Inspect the evaluator's __call__ function to determine what singleton inputs are expected
        when the evaluator is being used in a non-conversation context.
        By default, it's assumed that any input that is NOT kwargs or a conversation are singleton inputs.
        Thankfully this works the way you'd hope, with the call_signature being based on the child
        function's signature, not the parent's.

        :return: A list of strings representing the names of singleton inputs.
        :rtype: List[str]
        """

        call_signature = inspect.signature(self.__call__)
        singletons = []
        for param in call_signature.parameters:
            if param not in self._not_singleton_inputs:
                singletons.append(param)
        return singletons

    def _derive_conversation_converter(self) -> Callable:
        """Produce the function that will be used to convert conversations to a list of evaluable inputs.
        This uses the inputs derived from the _derive_singleton_inputs function to determine which
        aspects of a conversation ought to be extracted.

        :return: The function that will be used to convert conversations to evaluable inputs.
        :rtype: Callable
        """
        include_context = "context" in self._singleton_inputs
        include_query = "query" in self._singleton_inputs
        include_response = "response" in self._singleton_inputs

        def converter(conversation: Dict) -> List:
            messages = conversation["messages"]
            global_context = conversation.get("context", None)
            # Extract queries, responses from conversation
            queries = []
            responses = []

            # Convert conversation slice into queries and responses.
            # Assume that 'user' role is asking queries and 'assistant' role is responding.
            if self._eval_last_turn and len(messages) > 1:
                messages = messages[-2:]

            for each_turn in messages:
                role = each_turn["role"]
                if role == "user":
                    queries.append(each_turn)
                elif role == "assistant":
                    responses.append(each_turn)
            # TODO complain if len(queries) != len(responses)?
            eval_inputs = []
            for query, response in zip(queries, responses):
                context = {}
                if include_context:
                    query_context = query.get("context", None)
                    response_context = response.get("context", None)
                    if global_context:
                        context["global_context"] = global_context
                    if query_context and not include_query:
                        context["query_context"] = query_context
                    if response_context and not include_response:
                        context["response_context"] = response_context

                eval_input = {}
                if include_query:
                    eval_input["query"] = query
                if include_response:
                    eval_input["response"] = response
                if include_context:
                    eval_input["context"] = str(context)
                eval_inputs.append(eval_input)
            return eval_inputs

        return converter

    def _convert_kwargs_to_eval_input(self, **kwargs) -> List:
        """Convert an arbitrary input into a list of inputs for evaluators.
        It is assumed that evaluators generally make use of their inputs in one of two ways.
        Either they receive a collection of keyname inputs that are all single values
        (like a query and response), or they receive conversation that iss a list of dictionary
        values.

        The self._singleton_inputs list assigned during initialization is used to find and extract
        singleton keywords, and self._allow_converssation_input is used to determine if a conversation
        is a valid input.

        If both conversations and singletons are allowed, the function will raise an exception if both
        are inputted.

        This function must be overridden by child classes IF they need to both a conversation and
        other inputs to be passed in.

        :keyword kwargs: The inputs to convert.
        :type kwargs: Dict
        :return: A list of arbitrary values that are valid inputs for this evaluator's do_eval function.
        :rtype: List
        """

        # Collect inputs
        conversation = kwargs.get("conversation", None)
        singletons = {}
        if len(self._singleton_inputs) > 0:
            singletons = {key: kwargs.get(key, None) for key in self._singleton_inputs}
        # Check that both conversation and other inputs aren't set
        if conversation is not None and any(singletons.values()):
            raise EvaluationException(
                message="Invalid input",
                internal_message=f"Both conversation and individual inputs were provided to {type(self).__name__}",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.INVALID_VALUE,
                target=ErrorTarget.CONVERSATION,
            )
        # Handle Conversation
        if conversation is not None:
            return self._derive_conversation_converter()(conversation)
        # Handle Singletons
        if all(value is not None for value in singletons.values()):
            return [singletons]  # TODO loosen requirements to allow for optional singletons?
        # Missing input
        raise EvaluationException(
            message="Missing input",
            internal_message=f"Neither conversation nor individual inputs provided to {type(self).__name__}.",
            blame=ErrorBlame.USER_ERROR,
            category=ErrorCategory.INVALID_VALUE,
            target=ErrorTarget.CONVERSATION,
        )

    def _aggregate_results(self, per_turn_results: List[Dict]) -> Dict:
        """Aggregate the evaluation results of each conversation turn into a single result.

        Exact implementation might need to vary slightly depending on the results produced.
        Default behavior is to average the all number-based outputs.

        :param per_turn_results: List of evaluation results for each turn in the conversation.
        :type per_turn_results: List[Dict]
        :return: A dictionary containing aggregated results, with numeric metrics having their
        means as top-level values in the dictionary, and all original
        values (including non-numerics) located in under the "evaluation_per_turn" key,
        which each sub-key being a metric and each sub-value being a the list of that metric's
        per-turn values.
        :rtype: Dict
        """

        aggregated = {}
        evaluation_per_turn = {}

        # Go over each turn, and rotate the results into a
        # metric: List[values] format for the evals_per_turn dictionary.
        for turn in per_turn_results:
            for metric, value in turn.items():
                if metric not in evaluation_per_turn:
                    evaluation_per_turn[metric] = []
                evaluation_per_turn[metric].append(value)

        # Find and average all numeric values
        for metric, values in evaluation_per_turn.items():
            if all(isinstance(value, (int, float)) for value in values):
                aggregated[metric] = list_mean(values)
        # Slap the per-turn results back in.
        aggregated["evaluation_per_turn"] = evaluation_per_turn

        return aggregated

    async def _real_call(self, **kwargs):
        """The asynchronous call where real end-to-end evaluation logic is performed.

        :keyword kwargs: The inputs to evaluate.
        :type kwargs: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        # Convert inputs into list of evaluable inputs.
        eval_input_list = self._convert_kwargs_to_eval_input(**kwargs)
        per_turn_results = []
        # Evaluate all inputs.
        for eval_input in eval_input_list:
            per_turn_results.append(await self._do_eval(eval_input))
        # Return results as-is if only one result was produced.

        if len(per_turn_results) == 1:
            return per_turn_results[0]
        if len(per_turn_results) == 0:
            return {}  # TODO raise something?
        # Otherwise, aggregate results.
        return self._aggregate_results(per_turn_results=per_turn_results)

    # ~~~ METHODS THAT SHOULD NEVER BE OVERRIDDEN BY CHILDREN~~~

    def _to_async(self):
        return self._async_evaluator


class AsyncEvaluatorBase:
    """The asynchronous evaluator hidden underneath all evaluators. This makes generous use passing functions
    to ensure that no one ever needs to extend or otherwise modify this class directly.
    """

    def __init__(self, real_call):  # DO NOT ADD TYPEHINT PROMPT FLOW WILL SCREAM AT YOU ABOUT META GENERATION
        self._real_call = real_call

    # Don't look at my shame. Nothing to see here....
    # Oh, you're still here? Ok, the reason this has such a gross call signature and behavior is due
    # to our broken async code not properly handling inputs; keyword arguments that aren't in the signature#
    # are just not passed into this function instead of ending up in kwargs.
    # Since we want this to be relatively call-agnostic, we just account for every input that any children
    # are known to throw at this, mash them into kwargs, and then pass them into the real call.
    async def __call__(self, *, query=None, response=None, context=None, conversation=None, **kwargs):
        if conversation is not None:
            kwargs["conversation"] = conversation
        if query is not None:
            kwargs["query"] = query
        if response is not None:
            kwargs["response"] = response
        if context is not None:
            kwargs["context"] = context
        return await self._real_call(**kwargs)
