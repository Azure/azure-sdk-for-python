# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import ABC, abstractmethod

class EvaluationServiceClientInterface(ABC):
    """Interface for the Evaluation Service Client."""

    @abstractmethod
    def check_annotation(self, *, annotation: str, **kwargs) -> None:
        """Check if the annotation is available."""
        pass

    @abstractmethod
    def submit_annotation(self, annotation: dict, **kwargs) -> None:
        """Submit the annotation to the service."""
        pass
    @abstractmethod
    def get_template_parameters_image(self, *, path, **kwargs) -> dict:
        """Get the template parameters for image. Poll for response"""
        pass

    @abstractmethod
    def submit_simulation(self, simulation: dict, **kwargs) -> None:
        """Submit the simulation to the service. Poll for response"""
        pass

    @abstractmethod
    def get_template_parameters(self, **kwargs) -> dict:
        """Get the template parameters."""
        pass

    def get_jail_break_dataset_with_type(self, *, type: str, **kwargs) -> dict:
        """Get the jail break dataset with type."""
        pass