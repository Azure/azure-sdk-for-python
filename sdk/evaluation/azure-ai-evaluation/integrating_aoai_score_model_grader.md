# Integrating Azure OpenAI Score Model Grader

## Overview

This document provides a comprehensive plan for integrating the `AzureOpenAIScoreModelGrader` into the Azure AI Evaluation SDK. The Score Model Grader enables continuous scoring (0.0-1.0) with custom prompts, complementing the existing categorical and binary graders.

## Current State Analysis

### Existing AOAI Grader Architecture

The Azure AI Evaluation SDK currently supports three types of AOAI graders:

1. **`AzureOpenAIGrader`** (Base Class)
   - Located: `azure/ai/evaluation/_aoai/aoai_grader.py`
   - Handles model configuration and OpenAI client creation
   - Validates API keys and endpoints
   - Supports both Azure OpenAI and OpenAI configurations

2. **`AzureOpenAILabelGrader`** 
   - Located: `azure/ai/evaluation/_aoai/label_grader.py`
   - Wraps OpenAI's `LabelModelGrader`
   - Supports classification with predefined labels
   - Uses `pass_threshold` for binary pass/fail results

3. **`AzureOpenAIStringCheckGrader`**
   - Located: `azure/ai/evaluation/_aoai/string_check_grader.py`
   - Wraps OpenAI's `StringCheckGrader`
   - Supports string operations: `eq`, `ne`, `like`, `ilike`
   - Binary pass/fail results only

4. **`AzureOpenAITextSimilarityGrader`**
   - Located: `azure/ai/evaluation/_aoai/text_similarity_grader.py`
   - Wraps OpenAI's `TextSimilarityGrader`
   - Supports various similarity metrics (BLEU, ROUGE, cosine, etc.)
   - Uses `pass_threshold` for binary classification

### Integration Points

**Evaluation Pipeline:**
- `_evaluate_aoai.py` - Orchestrates AOAI evaluations
- `_split_evaluators_and_grader_configs()` - Separates AOAI graders from regular evaluators
- `_get_grader_class()` - Maps grader IDs to implementation classes
- Main `__init__.py` - Exports public API classes

**Key Functions:**
- `_begin_aoai_evaluation()` - Starts AOAI evaluation runs
- `_get_evaluation_run_results()` - Retrieves and formats results
- `_convert_remote_eval_params_to_grader()` - Creates grader instances from config

## Missing Component: Score Model Grader

### OpenAI SDK ScoreModelGrader Structure

Based on analysis of the OpenAI SDK, the `ScoreModelGrader` has the following structure:

```python
class ScoreModelGrader(BaseModel):
    input: List[Input]              # Conversation-style messages
    model: str                      # Grading model (e.g., "gpt-4")
    name: str                       # Grader name
    type: Literal["score_model"]    # Always "score_model"
    range: Optional[List[float]]    # Score range, defaults to [0, 1]
    sampling_params: Optional[object] # Model parameters

class Input(BaseModel):
    content: str                    # Message content with templates
    role: Literal["user", "assistant", "system", "developer"]
    type: Optional[Literal["message"]] = None
```

### Key Capabilities

**Continuous Scoring:**
- Returns floating-point scores (typically 0.0-1.0)
- Configurable score ranges (e.g., [0, 5], [0, 100])
- Pass/fail threshold for binary classification

**Flexible Prompting:**
- Multi-message conversations (system, user, assistant, developer roles)
- Template string support for dynamic content injection
- Custom evaluation criteria and instructions

**Model Configuration:**
- Supports any OpenAI-compatible model
- Configurable sampling parameters (temperature, max_tokens, etc.)
- Independent model selection for grading vs. evaluation

## Implementation Plan

### Phase 1: Core Implementation

#### Step 1.1: Create AzureOpenAIScoreModelGrader Class

**File:** `azure/ai/evaluation/_aoai/score_model_grader.py`

```python
from typing import Any, Dict, Union, List, Optional
from typing_extensions import Literal

from azure.ai.evaluation._model_configurations import (
    AzureOpenAIModelConfiguration, 
    OpenAIModelConfiguration
)
from openai.types.graders import ScoreModelGrader
from azure.ai.evaluation._common._experimental import experimental

from .aoai_grader import AzureOpenAIGrader


@experimental
class AzureOpenAIScoreModelGrader(AzureOpenAIGrader):
    """
    Wrapper class for OpenAI's score model graders.
    
    Enables continuous scoring evaluation with custom prompts and flexible
    conversation-style inputs. Supports configurable score ranges and 
    pass thresholds for binary classification.
    """
    
    id = "aoai://score_model"
    
    def __init__(
        self,
        *,
        model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
        input: List[Dict[str, str]], 
        model: str,
        name: str,
        range: Optional[List[float]] = None,
        sampling_params: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ):
        # Create OpenAI ScoreModelGrader instance
        grader_kwargs = {
            "input": input,
            "model": model, 
            "name": name,
            "type": "score_model"
        }
        
        if range is not None:
            grader_kwargs["range"] = range
        if sampling_params is not None:
            grader_kwargs["sampling_params"] = sampling_params
            
        grader = ScoreModelGrader(**grader_kwargs)
        
        super().__init__(
            model_config=model_config, 
            grader_config=grader, 
            **kwargs
        )
```

**Key Implementation Details:**
- Inherits from `AzureOpenAIGrader` for consistent model handling
- Wraps OpenAI's `ScoreModelGrader` following existing patterns
- Supports all ScoreModelGrader parameters
- Uses experimental decorator for preview functionality

#### Step 1.2: Update Module Exports

**File:** `azure/ai/evaluation/_aoai/__init__.py`

```python
from .aoai_grader import AzureOpenAIGrader
from .score_model_grader import AzureOpenAIScoreModelGrader  # Add this import

__all__ = [
    "AzureOpenAIGrader",
    "AzureOpenAIScoreModelGrader",  # Add this export
]
```

**File:** `azure/ai/evaluation/__init__.py`

```python
# Add import
from ._aoai.score_model_grader import AzureOpenAIScoreModelGrader

# Add to exports (around line 40)
```

#### Step 1.3: Update Grader Registry

**File:** `azure/ai/evaluation/_evaluate/_evaluate_aoai.py`

Update the `_get_grader_class()` function:

```python
def _get_grader_class(model_id: str) -> Type[AzureOpenAIGrader]:
    """Given a model ID, return the class of the corresponding grader wrapper."""
    
    from azure.ai.evaluation import (
        AzureOpenAIGrader,
        AzureOpenAILabelGrader,
        AzureOpenAIStringCheckGrader,
        AzureOpenAITextSimilarityGrader,
        AzureOpenAIScoreModelGrader,  # Add this import
    )
    
    id_map = {
        AzureOpenAIGrader.id: AzureOpenAIGrader,
        AzureOpenAILabelGrader.id: AzureOpenAILabelGrader,
        AzureOpenAIStringCheckGrader.id: AzureOpenAIStringCheckGrader,
        AzureOpenAITextSimilarityGrader.id: AzureOpenAITextSimilarityGrader,
        AzureOpenAIScoreModelGrader.id: AzureOpenAIScoreModelGrader,  # Add this
    }
    
    # ... rest of function unchanged
```

### Phase 2: Testing and Validation

#### Step 2.1: Create Unit Tests

**File:** `tests/unittests/test_aoai_score_model_grader.py`

```python
import pytest
from azure.ai.evaluation import AzureOpenAIScoreModelGrader
from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration


class TestAzureOpenAIScoreModelGrader:
    
    def test_initialization_with_required_params(self):
        """Test basic initialization with required parameters."""
        model_config = AzureOpenAIModelConfiguration(
            azure_endpoint="https://test.openai.azure.com/",
            api_key="test-key",
            azure_deployment="gpt-4"
        )
        
        grader = AzureOpenAIScoreModelGrader(
            model_config=model_config,
            input=[
                {"role": "system", "content": "You are a helpful evaluator."},
                {"role": "user", "content": "Rate this: {{ data.text }}"}
            ],
            model="gpt-4",
            name="Test Grader"
        )
        
        assert grader._grader_config.name == "Test Grader"
        assert grader._grader_config.model == "gpt-4"
        assert grader._grader_config.type == "score_model"
    
    def test_initialization_with_optional_params(self):
        """Test initialization with optional parameters."""
        # Test with range and sampling_params
        # ... implementation
    
    def test_client_creation(self):
        """Test that the grader can create appropriate OpenAI client."""
        # ... implementation
```

#### Step 2.2: Create Integration Tests

**File:** `tests/e2etests/test_aoai_score_model_integration.py`

```python
import pytest
from azure.ai.evaluation import evaluate, AzureOpenAIScoreModelGrader
from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration


@pytest.mark.skipif("not config.getoption('--live')")
class TestAzureOpenAIScoreModelIntegration:
    
    def test_evaluate_with_score_model_grader(self):
        """Test end-to-end evaluation with score model grader."""
        # Create test data
        # Configure grader
        # Run evaluation
        # Validate results format
        pass
```

#### Step 2.3: Update Sample and Documentation

**Sample File:** `samples/aoai_score_model_grader_sample.py` (already created)

**Documentation Updates:**
- Update README.md with new grader information
- Add API documentation
- Update migration guide if needed

### Phase 3: Advanced Features and Optimizations

#### Step 3.1: Enhanced Template Support

**Template Variables:**
- `{{ data.field_name }}` - Access input data fields
- `{{ outputs.evaluator_name }}` - Access other evaluator outputs
- Custom template functions for data formatting

**Implementation:**
- Validate template syntax during initialization
- Provide clear error messages for template issues
- Support nested field access (e.g., `{{ data.conversation.messages[0] }}`)

#### Step 3.2: Result Processing Enhancements

**Score Parsing:**
- Handle different score formats (JSON, plain text, structured)
- Extract reasoning/explanation from model responses
- Validate score ranges and handle edge cases

**Metrics Calculation:**
- Mean, median, standard deviation of scores
- Distribution analysis
- Correlation with other evaluators

#### Step 3.3: Performance Optimizations

**Batch Processing:**
- Group evaluations by model configuration
- Optimize API calls and reduce latency
- Implement retry logic with exponential backoff

**Caching:**
- Cache grader configurations
- Store evaluation results for reuse
- Implement result invalidation strategies

## Usage Examples

### Basic Conversation Quality Assessment

```python
from azure.ai.evaluation import evaluate, AzureOpenAIScoreModelGrader
from azure.ai.evaluation import AzureOpenAIModelConfiguration

# Configure model
model_config = AzureOpenAIModelConfiguration(
    azure_endpoint="https://your-endpoint.openai.azure.com/",
    api_key="your-api-key",
    azure_deployment="gpt-4"
)

# Create grader
quality_grader = AzureOpenAIScoreModelGrader(
    model_config=model_config,
    name="Conversation Quality",
    model="gpt-4",
    input=[
        {
            "role": "system",
            "content": "Rate conversation quality from 0.0 to 1.0"
        },
        {
            "role": "user", 
            "content": "Conversation: {{ data.conversation }}\\nScore:"
        }
    ],
    range=[0.0, 1.0],
    pass_threshold=0.7
)

# Run evaluation
results = evaluate(
    data="conversations.jsonl",
    evaluators={"quality": quality_grader}
)
```

### Multi-Criteria Evaluation

```python
# Multiple score model graders for comprehensive evaluation
evaluators = {
    "helpfulness": AzureOpenAIScoreModelGrader(
        model_config=model_config,
        name="Helpfulness",
        model="gpt-4",
        input=[...],  # Helpfulness-specific prompts
        pass_threshold=0.6
    ),
    "accuracy": AzureOpenAIScoreModelGrader(
        model_config=model_config,
        name="Factual Accuracy", 
        model="gpt-4",
        input=[...],  # Accuracy-specific prompts
        pass_threshold=0.8
    ),
    "clarity": AzureOpenAIScoreModelGrader(
        model_config=model_config,
        name="Response Clarity",
        model="gpt-4", 
        input=[...],  # Clarity-specific prompts
        pass_threshold=0.7
    )
}

results = evaluate(data="data.jsonl", evaluators=evaluators)
```

### Custom Score Ranges

```python
# 1-5 star rating system
star_rating_grader = AzureOpenAIScoreModelGrader(
    model_config=model_config,
    name="Star Rating",
    model="gpt-4",
    input=[
        {
            "role": "system",
            "content": "Rate from 1 (worst) to 5 (best) stars"
        },
        {
            "role": "user",
            "content": "Review: {{ data.review }}\\nStars (1-5):"
        }
    ],
    range=[1.0, 5.0],
    pass_threshold=3.0  # 3+ stars = pass
)
```

## Error Handling and Edge Cases

### Common Error Scenarios

1. **Invalid Template Syntax**
   - Missing closing braces
   - Invalid field references
   - Nested template errors

2. **Model Configuration Issues**
   - Invalid API keys or endpoints
   - Unsupported model names
   - Network connectivity problems

3. **Score Parsing Failures**
   - Non-numeric responses
   - Scores outside specified range
   - Malformed JSON responses

4. **Evaluation Pipeline Errors**
   - Data formatting issues
   - Column mapping conflicts
   - Resource quota limits

### Error Handling Implementation

```python
class AzureOpenAIScoreModelGrader(AzureOpenAIGrader):
    
    def _validate_grader_config(self) -> None:
        """Enhanced validation for score model graders."""
        super()._validate_grader_config()
        
        # Validate input messages
        if not self._grader_config.input:
            raise EvaluationException("Score model grader requires input messages")
        
        # Validate model name
        if not self._grader_config.model:
            raise EvaluationException("Score model grader requires model name")
        
        # Validate score range
        if self._grader_config.range:
            if len(self._grader_config.range) != 2:
                raise EvaluationException("Score range must contain exactly 2 values")
            if self._grader_config.range[0] >= self._grader_config.range[1]:
                raise EvaluationException("Invalid score range: min must be < max")
        
        # Validate template syntax in input messages
        self._validate_template_syntax()
    
    def _validate_template_syntax(self) -> None:
        """Validate template strings in input messages."""
        for msg in self._grader_config.input:
            content = msg.get("content", "")
            # Check for balanced braces, valid field references, etc.
            # ... implementation
```

## Testing Strategy

### Unit Testing

**Test Categories:**
1. **Initialization Tests** - Parameter validation, error handling
2. **Configuration Tests** - Model config validation, client creation
3. **Template Tests** - Template syntax validation, variable substitution
4. **Serialization Tests** - JSON serialization/deserialization

### Integration Testing

**Test Scenarios:**
1. **End-to-End Evaluation** - Complete evaluation pipeline
2. **Multi-Grader Scenarios** - Multiple graders with different configs
3. **Error Recovery** - Network failures, API errors, malformed responses
4. **Performance Testing** - Large datasets, concurrent evaluations

### Manual Testing Checklist

- [ ] Basic grader initialization with minimal parameters
- [ ] Advanced grader configuration with all optional parameters
- [ ] Template variable substitution with various data formats
- [ ] Score range validation and threshold behavior
- [ ] Integration with existing evaluation pipeline
- [ ] Error handling for common failure scenarios
- [ ] Performance with large datasets (100+ samples)
- [ ] Concurrent evaluation with multiple graders

## Deployment Considerations

### Backward Compatibility

- All changes are additive - no breaking changes to existing APIs
- New grader is marked as experimental initially
- Existing evaluations continue to work unchanged

### Documentation Updates

- Update API reference documentation
- Add usage examples to README
- Create migration guide for users
- Update troubleshooting guide

### Monitoring and Observability

- Add telemetry for score model grader usage
- Monitor evaluation success/failure rates
- Track performance metrics (latency, throughput)
- Log template parsing errors and API failures

## Success Criteria

### Functional Requirements

- [ ] `AzureOpenAIScoreModelGrader` class implemented and tested
- [ ] Integration with existing evaluation pipeline
- [ ] Support for all OpenAI ScoreModelGrader features
- [ ] Comprehensive error handling and validation
- [ ] Template variable substitution working correctly

### Quality Requirements

- [ ] Unit test coverage > 90%
- [ ] Integration tests passing
- [ ] Documentation complete and accurate
- [ ] Sample code working and demonstrative
- [ ] Performance acceptable (< 2x overhead vs. direct OpenAI calls)

### User Experience Requirements

- [ ] Consistent API with existing graders
- [ ] Clear error messages for common issues
- [ ] Comprehensive examples and documentation
- [ ] Smooth migration path from direct OpenAI usage

## Timeline Estimate

**Phase 1 - Core Implementation:** 3-5 days
- Day 1: Implement `AzureOpenAIScoreModelGrader` class
- Day 2: Update exports and grader registry
- Day 3: Create unit tests
- Day 4-5: Integration testing and bug fixes

**Phase 2 - Testing and Documentation:** 2-3 days  
- Day 1: Comprehensive testing
- Day 2: Documentation updates
- Day 3: Sample refinement and validation

**Phase 3 - Advanced Features:** 1-2 days (optional)
- Enhanced template support
- Performance optimizations
- Additional error handling

**Total Estimated Time:** 6-10 days

## Risk Assessment

### High Risk
- **OpenAI SDK Changes** - Risk of breaking changes in grader interfaces
- **Template Complexity** - Complex template syntax could be error-prone

### Medium Risk  
- **Performance Impact** - Additional API calls could affect evaluation speed
- **Error Handling Gaps** - Unforeseen edge cases in score parsing

### Low Risk
- **Integration Issues** - Existing pipeline is well-established
- **Backward Compatibility** - Additive changes only

### Mitigation Strategies
- Pin OpenAI SDK version to avoid breaking changes
- Implement comprehensive test suite with edge cases
- Add performance monitoring and optimization
- Create detailed error handling documentation

## Conclusion

This implementation plan provides a comprehensive roadmap for integrating the `AzureOpenAIScoreModelGrader` into the Azure AI Evaluation SDK. The approach leverages existing infrastructure while adding powerful continuous scoring capabilities that complement the current categorical and binary graders.

The phased implementation approach ensures:
- **Reliability** - Thorough testing at each stage
- **Maintainability** - Consistent with existing patterns
- **Usability** - Clear API and comprehensive documentation
- **Extensibility** - Foundation for future enhancements

Following this plan will result in a robust, well-tested implementation that provides users with flexible, powerful evaluation capabilities while maintaining the high quality and reliability standards of the Azure AI Evaluation SDK.
