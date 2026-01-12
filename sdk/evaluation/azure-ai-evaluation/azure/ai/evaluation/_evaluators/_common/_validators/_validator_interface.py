# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Abstract interface for all validators.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class ValidatorInterface(ABC):
    """
    Abstract base class defining the interface that all validators must implement.
    
    This interface ensures consistent validation behavior across different validator types,
    requiring each validator to implement the validate_eval_input method.
    """

    @abstractmethod
    def validate_eval_input(self, eval_input: Dict[str, Any]) -> bool:
        """
        Validate the evaluation input dictionary.
        
        Args:
            eval_input: Dictionary containing evaluation inputs to validate.
            
        Returns:
            True if validation passes.
            
        Raises:
            EvaluationException: If validation fails.
        """
        pass
