# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import jinja2
import logging
from typing import Dict, List, Tuple, Union

from azure.ai.generative.synthetic.simulator._model_tools import LLMBase, OpenAICompletionsModel, OpenAIChatCompletionsModel,\
    RetryClient, LLAMAChatCompletionsModel, LLAMACompletionsModel
from .conversation_turn import ConversationTurn
from .constants import ConversationRole


class ConversationBot:
    def __init__(
        self,
        role: ConversationRole,
        model: LLMBase,
        conversation_template: str,
        instantiation_parameters: Dict[str, str],
    ):
        """
        Create a ConversationBot with specific name, persona and a sentence that can be used as a conversation starter.

        Parameters
        ----------
        role: The role of the bot in the conversation, either USER or ASSISTANT
        model: The LLM model to use for generating responses
        conversation_template: A jinja2 template that describes the conversation, this is used to generate the prompt for the LLM
        instantiation_parameters: A dictionary of parameters that are used to instantiate the conversation template
            Dedicated parameters:
                - conversation_starter: A sentence that can be used as a conversation starter, if not provided,
                    the first turn will be generated using the LLM
        """
        if role == ConversationRole.USER and type(model) == LLAMAChatCompletionsModel:
            self.logger.info("We suggest using LLaMa chat model to simulate assistant not to simulate user")


        self.role = role
        self.conversation_template: jinja2.Template = jinja2.Template(
            conversation_template, undefined=jinja2.StrictUndefined
        )
        self.persona_template_args = instantiation_parameters
        if self.role == ConversationRole.USER:
            self.name = self.persona_template_args.get("name", role.value)
        else:
            self.name = self.persona_template_args.get("chatbot_name", role.value) or model.name
        self.model = model

        self.logger = logging.getLogger(repr(self))

        if role == ConversationRole.USER:
            if "conversation_starter" in self.persona_template_args:
                self.logger.info(
                    'This simulated bot will use the provided conversation starter '
                    f'"{repr(self.persona_template_args["conversation_starter"])[:400]}"'
                    'instead of generating a turn using a LLM'
                )
                self.conversation_starter = self.persona_template_args["conversation_starter"]
            else:
                self.logger.info('This simulated bot will generate the first turn as no conversation starter is provided')
                self.conversation_starter = None


    async def generate_response(
        self,
        session: RetryClient,
        conversation_history: List[ConversationTurn],
        max_history: int,
        turn_number: int = 0,
    ) -> Tuple[dict, dict, int, dict]:
        """
        Prompt the ConversationBot for a response.

        Parameters
        ----------
        session: The aiohttp session to use for the request.
        conversation_history: The turns in the conversation so far.
        request_params: Parameters used to query GPT-4 model.

        Returns
        -------
        response: The response from the ConversationBot.
        time_taken: The time taken to generate the response.
        full_response: The full response from the model.
        """

        # check if this is the first turn and the conversation_starter is not None,
        # return the conversations starter rather than generating turn using LLM
        if turn_number == 0 and self.conversation_starter is not None and self.conversation_starter != "":
            self.logger.info(f"Returning conversation starter: {self.conversation_starter}")
            time_taken = 0

            samples = [self.conversation_starter]
            finish_reason = ["stop"]

            parsed_response = {
                "samples": samples,
                "finish_reason": finish_reason,
                "id": None
            }
            full_response = parsed_response
            return parsed_response, {}, time_taken, full_response

        prompt = self.conversation_template.render(
            conversation_turns=conversation_history[-max_history:],
            role=self.role.value,
            **self.persona_template_args
        )

        messages = [{"role": "system", "content": prompt}]

        # The ChatAPI must respond as ASSISTANT, so if this bot is USER, we need to reverse the messages
        if (self.role == ConversationRole.USER) and (isinstance(self.model, OpenAIChatCompletionsModel) or isinstance(self.model, LLAMAChatCompletionsModel)):
            # in here we need to simulate the user, The chatapi only generate turn as assistant and can't generate turn as user
            # thus we reverse all rules in history messages, so that messages produced from the other bot passed here as user messages
            messages.extend([turn.to_openai_chat_format(reverse=True) for turn in conversation_history[-max_history:]])
            prompt_role = ConversationRole.USER.value
        else:
            messages.extend([turn.to_openai_chat_format() for turn in conversation_history[-max_history:]])
            prompt_role = self.role.value

        response = await self.model.get_conversation_completion(
            messages=messages,
            session=session,
            role=prompt_role,
        )

        return response['response'], response['request'], response['time_taken'], response['full_response']

    def __repr__(self):
        return f"Bot(name={self.name}, role={self.role.name}, model={self.model.__class__.__name__})"
