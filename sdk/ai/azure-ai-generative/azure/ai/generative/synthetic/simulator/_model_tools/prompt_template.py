# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re
import json
from enum import Enum
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Union

from .encoding import encode_example, Encoding
from .defaults import (
    DEFAULT_PROMPT_TEMPLATE,
    DEFAULT_FEW_SHOT_EXAMPLE_PATTERN,
    DEFAULT_FEW_SHOT_EXAMPLE_SEPARATOR,
    DEFAULT_INPUT_EXAMPLE_PATTERN,
    DEFAULT_INPUT_EXAMPLE_SEPARATOR,
)


class SpecialTokensFormat(Enum):
    NONE = 0
    COMPLETION = 1  # Default completion prompt format
    CHAT = 2  # ChatML Prompt Format using special tokens
    CHAT_HARMONY_V3 = 3  # Harmony V3 ChatML Prompt Format using special tokens


class PromptTemplate:
    '''
    Holds the prompt_template for formatting the metaprompt, input, and few_shot examples.
    
    Decision layers this class handles:
    - When using Chat or Harmony_V3 format, special tokens need to be set around certain sections of the prompt.
    - When using a batched prompt, the inputs need to be separated into their own section from the outputs.
    - When using a zero-shot scenario, no labeled example section should appear in the prompt.
    '''

    def __init__(
        self,
        labeling_guidelines: str,
        label_keys: List[str],
        special_tokens_format: SpecialTokensFormat = SpecialTokensFormat.NONE,
        prompt_template: str = DEFAULT_PROMPT_TEMPLATE,
        few_shot_example_pattern: str = DEFAULT_FEW_SHOT_EXAMPLE_PATTERN,
        few_shot_example_separator: str = DEFAULT_FEW_SHOT_EXAMPLE_SEPARATOR,
        input_example_pattern: str = DEFAULT_INPUT_EXAMPLE_PATTERN,
        input_example_separator: str = DEFAULT_INPUT_EXAMPLE_SEPARATOR,
        metadata_keys: List[str] = [],
        **additional_inputs: Dict[str, str]
    ):
        '''Initialize a PromptTemplate from parameters.'''

        self.prompt_template = prompt_template
        self.labeling_guidelines = labeling_guidelines
        if label_keys is not None:
            self.label_keys = label_keys
        else:
            self.label_keys = []
        self.special_tokens_format = special_tokens_format
        self.few_shot_example_pattern = few_shot_example_pattern
        self.few_shot_example_separator = few_shot_example_separator
        self.input_example_pattern = input_example_pattern
        self.input_example_separator = input_example_separator
        if metadata_keys is not None:
            self.metadata_keys = metadata_keys
        else:
            self.metadata_keys = []
        self.additional_inputs = filter_dict(additional_inputs, remove=['labeling_guidelines', 'few_shot_examples', 'input_examples'])

        # Validate that example patterns have places for examples
        assert '{inputs}' in few_shot_example_pattern and '{labels}' in few_shot_example_pattern, \
            "few_shot_example_pattern should contain {inputs} and {labels}: " + few_shot_example_pattern
        assert '{inputs}' in input_example_pattern, \
            "input_example_pattern should contain {inputs}: " + input_example_pattern

        # Validate that {input_examples} is in the prompt template
        assert '{input_examples}' in prompt_template, \
            "prompt_template should contain {input_examples}. See: https://aml-babel.com/tools/lasertag/prompt-templates"

        # Use example_prefix to find and split output examples from the model
        example_heading = self.input_example_pattern.replace(r'{example_index}', r'[\d]+')
        self.output_split_pattern = re.compile(example_heading)


    @classmethod
    def from_files(
        cls, 
        input_filename: str, 
        few_shot_filename: Optional[str], 
        **config_params
    ):
        '''Load a PromptTemplate from parameters and infer missing params from the first
        example in each file.'''
        # Load one few_shot_example if possible
        if few_shot_filename is None:
            few_shot_example = None
        else:
            with open(few_shot_filename, 'r') as f:
                few_shot_example = dict(json.loads(f.readline().strip()))
        
        # Load one input_example
        with open(input_filename, 'r') as f:
            input_example = dict(json.loads(f.readline().strip()))
        
        return cls.from_examples(input_example, few_shot_example, **config_params)

    @classmethod
    def from_examples(
        cls, 
        input_example: Dict[str, Any], 
        few_shot_example: Optional[Dict[str, Any]], 
        **config_params
    ):
        '''Load a PromptTemplate from parameters and infer missing params from examples.'''
        # Validate few_shot_example
        if few_shot_example:
            for key, val in few_shot_example.items():
                validate_datatype(key, val)
        
        # If label_keys isn't defined, infer it from the examples
        if 'label_keys' not in config_params and few_shot_example is not None:
            input_keys = set(input_example.keys())
            few_shot_keys = set(few_shot_example.keys())
            config_params['label_keys'] = list(few_shot_keys - input_keys)
        elif 'label_keys' not in config_params or config_params['label_keys'] is None:
            config_params['label_keys'] = []

        return cls(**config_params)
    

    def set_special_tokens(self, format: SpecialTokensFormat):
        '''Sets the special token formatting of the prompt for the given format.'''
        # If changing from a previous special tokens format, reset all special tokens
        if format != self.special_tokens_format:
            for special_token in ['<|im_start|>', '<|im_end|>', '<|im_sep|>', '<|endofprompt|>']:
                self.prompt_template = self.prompt_template.replace(special_token, '')
                self.few_shot_example_separator = self.few_shot_example_separator.replace(special_token, '')
                self.input_example_separator = self.input_example_separator.replace(special_token, '')
                self.prompt_template = self.prompt_template.replace(special_token, '')
                self.batched_prompt_suffix = self.batched_prompt_suffix.replace(special_token, '')
        
        if format == SpecialTokensFormat.CHAT:
            self.prompt_template = '<|im_start|>\n' + self.prompt_template
            self.prompt_template = self.prompt_template.replace(
                '{input_examples}\n', '{input_examples}\n<|im_end|>\n\n<|im_start|>')
            self.batched_prompt_suffix = '<|im_end|>\n\n<|im_start|>' + self.batched_prompt_suffix
        elif format == SpecialTokensFormat.CHAT_HARMONY_V3:
            self.prompt_template = '<|im_start|>\n' + self.prompt_template
            self.batched_prompt_suffix = self.batched_prompt_suffix.replace(
                '{input_examples}\n', '{input_examples}\n<|im_end|>\n\n<|im_start|>')
            self.batched_prompt_suffix = '<|im_end|>\n\n<|im_start|>' + self.batched_prompt_suffix
            self.few_shot_example_separator += '<|im_sep|>\n'
            self.input_example_separator += '<|im_sep|>\n'
        elif format == SpecialTokensFormat.COMPLETION:
            self.prompt_template.replace('{few_shot_examples}', '{few_shot_examples}\n<|endofprompt|>')
        
    
    def format(
        self, 
        inputs: Union[Dict[str, str], List[Dict[str, str]]], 
        few_shots: Optional[List[Dict[str, str]]],
        encoding: Encoding = Encoding.JSON
    ) -> str:
        '''Formats the prompt with the given inputs and few_shot examples.
        Args:
            inputs: the inputs to the prompt.
            few_shots: the few_shot examples to the prompt.
        Returns:
            The formatted prompt.
        '''
        # Build the few_shot examples
        if few_shots is not None and len(few_shots):
            formatted_few_shots = []

            for i, example in enumerate(few_shots):
                example_values = self._encode_few_shot_example(example, encoding=encoding)
                example_str = replace_placeholders(
                    self.few_shot_example_pattern,
                    example_index=str(i + 1), 
                    inputs=example_values['inputs'],
                    labels=example_values['labels']
                )

                formatted_few_shots.append(example_str)
            
            few_shot_example_str = self.few_shot_example_separator.join(formatted_few_shots)
        else:
            few_shot_example_str = ''

        # Build the input examples
        if isinstance(inputs, dict):
            inputs = [inputs]
        
        formatted_input_examples = []
        for i, example in enumerate(inputs):
            example_values = self._encode_input_example(example, encoding=encoding)

            # Start example counter from the number of few_shot examples if using a single prompt
            if len(inputs) == 1 and few_shots is not None:
                i += len(few_shots)

            example_str = replace_placeholders(
                self.input_example_pattern,
                example_index=str(i + 1), 
                inputs=example_values['inputs']
            )

            formatted_input_examples.append(example_str)

        input_example_str = self.input_example_separator.join(formatted_input_examples)
        
        # Add the batched prompt suffix if using a batched prompt
        prompt_template = self.prompt_template
        
        # Build the prompt
        return replace_placeholders(
            prompt_template,
            labeling_guidelines=self.labeling_guidelines,
            few_shot_examples=few_shot_example_str,
            input_examples=input_example_str,
            **self.additional_inputs
        )
    
    def _encode_input_example(
        self,
        input_example: dict,
        encoding: Encoding = Encoding.JSON
    ) -> Dict[str, str]:
        '''Encode input example into encoding format.

        Args:
            input_example: input example
            example_index: index of example
            encoding: encoding structure for prompt examples. Should be in ['JSON', 'XML']

        Returns:
            example_str: encoded input example
        '''
        inputs_only = filter_dict(input_example, remove=self.label_keys + self.metadata_keys)
        inputs_str = encode_example(inputs_only, encoding)
        return {'inputs': inputs_str}


    def _encode_few_shot_example(
        self,
        few_shot_example: dict,
        encoding: Encoding = Encoding.JSON
    ) -> Dict[str, str]:
        '''Encode few_shot example into encoding format.

        Args:
            few_shot_example: few_shot example
            example_index: index of example
            encoding: encoding structure for prompt examples. Should be in ['JSON', 'XML']

        Returns:
            example_str: encoded few_shot example
        '''
        inputs_only = filter_dict(few_shot_example, remove=self.label_keys + self.metadata_keys)
        labels_only = filter_dict(few_shot_example, keep=self.label_keys)

        inputs_str = encode_example(inputs_only, encoding)
        labels_str = encode_example(labels_only, encoding)

        return {"inputs": inputs_str, "labels": labels_str}

    
    def split_output_examples(
        self,
        output_str: str
    ) -> List[str]:
        '''Attempt to split the output into a list of examples using 
        few_shot_example_pattern.

        Args:
            output_str: output examples
        
        Returns:
            output_examples: list of output examples
        '''
        output_str = output_str.strip()
        output_examples = [
            ex.strip() for ex in re.split(self.output_split_pattern, output_str) 
            if ex.strip()
        ]
        return output_examples


    def unlabel_few_shot_examples(self, examples: List[dict]):
        """
        Unlabel few_shot examples by removing label keys from examples and returning
        a list of unlabeled examples and a list of labels.
        """
        unlabeled_examples = []
        labels = []

        for example in examples:
            # get label
            label = filter_dict(example, keep=self.label_keys)
            labels.append(label)

            # get unlabeled example
            unlabeled_example = filter_dict(example, remove=self.label_keys)
            unlabeled_examples.append(unlabeled_example)

        return unlabeled_examples, labels

    def __repr__(self):
        return f'''PromptTemplate(
    prompt_template = {repr(self.prompt_template)[:50]}...,
    labeling_guidelines = {repr(self.labeling_guidelines)[:50]}...,
    input_example_pattern = {repr(self.input_example_pattern)},
    few_shot_example_pattern = {repr(self.few_shot_example_pattern)},
    input_example_separator = {repr(self.input_example_separator)},
    few_shot_example_separator = {repr(self.few_shot_example_separator)},
    label_keys = {self.label_keys},
    metadata_keys = {self.metadata_keys},
    additional_inputs = {self.additional_inputs}
)'''



def filter_dict(
    d: Dict[str, Any], 
    remove: Optional[List[str]] = None, 
    keep: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Filter dictionary by removing keys in remove list."""
    if remove is None:
        remove = []
    if keep is None:
        keep = [k for k in d if k not in remove]
    return {k: v for k, v in d.items() if k in keep}


def replace_placeholders(
    prompt: str,
    **placeholders
) -> str:
    """Replace placeholders in prompt template with actual values.

    Args:
        prompt_template (str): Prompt template.
        **placeholders: Dictionary of substrings to their replacements.

    Returns:
        str: Filled-in prompt.
    """
    # Replacing placeholders using .replace is less efficient than .format(),
    # but avoids errors when format keys are present in the user's data
    # Ex: "<code>print(f'{data}')" but {data} is not intended to be a placeholder
    for placeholder, replacement in placeholders.items():
        prompt = prompt.replace("{" + placeholder + "}", str(replacement))
    return prompt


def validate_datatype(key: str, val: Any):
    '''Assert that the given value is a valid data type'''
    if isinstance(val, (bool, int, float, str)):
        return
    elif isinstance(val, dict):
        assert "value" in val, f"Each label in a few_shot example needs a 'value' key: {key} - {val}"
    else:
        raise ValueError(f"Unsupported data type in few_shot example: {key} - {val}")
