# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
from azure.ai.ml.entities._job.pipeline._pipeline_job_helpers import from_dict_to_rest_distribution


@pytest.mark.unittest
@pytest.mark.training_experiences_test
class TestDistributionHelpers:
    """Test distribution helper functions to ensure torch.distributed is supported"""

    def test_from_dict_to_rest_distribution_pytorch(self):
        """Test that pytorch type is properly handled"""
        distribution_dict = {
            "distribution_type": "pytorch",
            "process_count_per_instance": 4
        }
        result = from_dict_to_rest_distribution(distribution_dict)
        assert result is not None
        assert hasattr(result, 'process_count_per_instance')
        assert result.process_count_per_instance == 4

    def test_from_dict_to_rest_distribution_torch_distributed(self):
        """Test that torch.distributed type is properly handled"""
        distribution_dict = {
            "distribution_type": "torch.distributed",
            "process_count_per_instance": 4
        }
        result = from_dict_to_rest_distribution(distribution_dict)
        assert result is not None
        assert hasattr(result, 'process_count_per_instance')
        assert result.process_count_per_instance == 4

    def test_from_dict_to_rest_distribution_pytorch_case_insensitive(self):
        """Test that PyTorch (mixed case) type is properly handled"""
        distribution_dict = {
            "distribution_type": "PyTorch",
            "process_count_per_instance": 2
        }
        result = from_dict_to_rest_distribution(distribution_dict)
        assert result is not None
        assert result.process_count_per_instance == 2

    def test_from_dict_to_rest_distribution_torch_distributed_case_insensitive(self):
        """Test that torch.distributed (mixed case) type is properly handled"""
        distribution_dict = {
            "distribution_type": "Torch.Distributed",
            "process_count_per_instance": 2
        }
        result = from_dict_to_rest_distribution(distribution_dict)
        assert result is not None
        assert result.process_count_per_instance == 2
