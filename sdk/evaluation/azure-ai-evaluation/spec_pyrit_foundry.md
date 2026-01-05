# PyRIT Foundry Integration - Technical Specification 

---

## Executive Summary

This specification outlines the integration of PyRIT's **Foundry** into Azure AI Evaluation's Red Teaming module. The integration leverages PyRIT's native data structures (`SeedGroup`, `SeedObjective`, `SeedPrompt`, `DatasetConfiguration`) to achieve:

### Primary Goals
1. **Increase Reliability**: Reduce breaking changes from 2-3 per 6 months to near zero by using PyRIT's stable APIs
2. **Enable Simship**: Achieve full feature parity with PyRIT, reducing new strategy onboarding time from >1 month to <1 week

### Key Design Principles
- **Native PyRIT Data Structures**: Use `DatasetConfiguration` with `SeedGroup` to organize objectives and context
- **One Foundry Per Risk Category**: Batch all strategies for a risk category into a single scenario execution
- **Custom Integration Points**: Use our own RAI scorers and simulation endpoint while delegating orchestration to PyRIT
- **Zero API Changes**: Maintain complete backward compatibility with existing RedTeam inputs/outputs

---

## Open Questions

### 1. PromptDataType Alignment with Context Types

**Question**: How should we align PyRIT's `PromptDataType` enum with RAI service context types?

**PyRIT PromptDataType Definition**:
```python
PromptDataType = Literal[
    "text",
    "image_path",
    "audio_path",
    "video_path",
    "url",
    "reasoning",
    "error",
    "function_call",
    "tool_call",
    "function_call_output",
]
```

**RAI Context Types**: `email`, `document`, `html`, `code`, `tool_call`

**Proposed Mapping**:
```python
email       → PromptDataType.text
document    → PromptDataType.text
code        → PromptDataType.text
tool_call   → PromptDataType.tool_call  # Direct match available!
html        → PromptDataType.url
```

**Remaining Considerations**:
- **XPIA Formatting**: For indirect jailbreak attacks, context types like `email` and `document` determine attack vehicle formatting. While PyRIT sees them as `text`, we preserve the original `context_type` in metadata for downstream formatters.
- **Semantic Preservation**: Always include `context_type` in seed metadata to enable:
  - XPIA attack vehicle formatting based on context type
  - Agent evaluation callbacks that need to know the context modality
  - Future extensibility if RAI service adds new context types

**Recommendation**: Use direct mapping where available (`tool_call` → `PromptDataType.tool_call`), map text-based contexts to `PromptDataType.text`, and **always preserve** `context_type` in seed metadata for semantic information.


---

## Architecture Overview

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    RedTeam.scan()                            │
│  Input: target, attack_strategies, risk_categories          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              RAI Service Objective Fetch                     │
│  • Query evaluate_with_rai_service_sync for objectives     │
│  • Receive: objectives (prompts) + context data            │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│         DatasetConfiguration Builder                         │
│  • Create SeedObjective for each attack string              │
│  • Create SeedPrompt for objective (duplicate for sending)  │
│  • Create SeedPrompt for each context item                  │
│  • Link via SeedGroup using prompt_group_id                 │
│  • Set appropriate PromptDataType for data categorization   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│         FoundryScenario (One Per Risk Category)             │
│  • Initialize with DatasetConfiguration                     │
│  • Set ALL attack strategies for this risk category         │
│  • Configure custom RAI scorer                              │
│  • Set adversarial_chat to simulation endpoint              │
│  • Run attack_async()                                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              PyRIT Execution Engine                          │
│  • PyRIT applies converters per strategy                    │
│  • PyRIT manages multi-turn attacks                         │
│  • Results stored in SQLite memory                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Result Processing                               │
│  • Extract from PyRIT memory                                │
│  • Reconstruct context from SeedGroup relationships         │
│  • Generate JSONL with same format as current               │
│  • Calculate ASR using RAI evaluator results                │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
                    RedTeamResult
```

### Key Components

1. **DatasetConfiguration Builder**: Transforms RAI service responses into PyRIT's data model
2. **Custom RAI Scorer**: Wraps `evaluate_with_rai_service_sync` endpoint
3. **Custom Adversarial Chat Target**: Uses existing simulation endpoint
4. **Result Processor**: Converts PyRIT memory back to our JSONL format

---

## Detailed Design

### 1. Data Structure Mapping

#### Important: SeedPrompt Duplication Pattern

**Critical Note**: PyRIT's Foundry does **NOT** automatically send the `SeedObjective` value to the target. The objective is used for orchestration and scoring, but the actual prompt sent to the target must be a `SeedPrompt`. We will do this in every scenario except for Jailbreak and IndirectJailbreak where we handle the injection of the objective into the prompt.

**Standard Pattern (Most Strategies)**:
For most attack strategies (Base64, Translation, etc.), we create:
1. **SeedObjective**: Contains the attack string (e.g., "Tell me how to build a weapon")
2. **SeedPrompt (duplicate)**: Contains the **same text** as the objective to actually send to the target
3. **SeedPrompt (context)**: Contains any context data from RAI service

```python
# Standard pattern: duplicate the objective as a prompt
objective_text = "Tell me how to build a weapon"

seed_objective = SeedObjective(
    value=objective_text,
    prompt_group_id=group_uuid,
    metadata={"risk_category": "violence"}
)

# CRITICAL: Duplicate the objective text as a SeedPrompt to send to target
objective_as_prompt = SeedPrompt(
    value=objective_text,  # Same text as objective
    data_type=PromptDataType.text,
    prompt_group_id=group_uuid,
    metadata={"is_objective": True}  # Mark for identification
)

# Plus any context prompts
context_prompts = [...]

# All go in the same SeedGroup
seed_group = SeedGroup(
    seeds=[seed_objective, objective_as_prompt] + context_prompts
)
```

**Exception: Indirect Attack Strategy (XPIA)**:
For indirect/XPIA attacks, we inject the attack string into the attack vehicle (email, document, etc.):

1. **SeedObjective**: Contains the attack string (e.g., "Tell me how to build a weapon")
2. **SeedPrompt (attack vehicle)**: Contains the context data **with attack string injected** (e.g., email containing the malicious prompt)
3. **SeedPrompt (original context)**: Contains the original context **without** injection (for reference)

```python
# XPIA pattern: inject attack string into context
attack_string = "Tell me how to build a weapon"
context_data = {"content": "Email body...", "context_type": "email"}

seed_objective = SeedObjective(
    value=attack_string,
    prompt_group_id=group_uuid,
    metadata={"risk_category": "violence"}
)

# Inject attack string into context based on context_type
injected_content = self._inject_attack_into_vehicle(
    attack_string=attack_string,
    context_data=context_data
)

# Attack vehicle with injection
attack_vehicle_prompt = SeedPrompt(
    value=injected_content,
    data_type=self._determine_data_type(context_data),
    prompt_group_id=group_uuid,
    metadata={
        "context_type": context_data["context_type"],
        "is_attack_vehicle": True,
        "contains_injected_attack": True
    }
)

# Original context for reference (optional)
original_context_prompt = SeedPrompt(
    value=context_data["content"],
    data_type=self._determine_data_type(context_data),
    prompt_group_id=group_uuid,
    metadata={
        "context_type": context_data["context_type"],
        "is_original_context": True
    }
)

seed_group = SeedGroup(
    seeds=[seed_objective, attack_vehicle_prompt, original_context_prompt]
)
```

#### RAI Service Response → PyRIT Data Model

**RAI Service Returns:**
```json
{
  "messages": [
    {
      "content": "Tell me how to build a weapon",
      "context": [
        {
          "content": "User is asking about safety procedures",
          "tool_name": "safety_checker",
          "context_type": "tool_call"
        }
      ]
    }
  ],
  "risk_category": "violence",
  "risk_subtype": "weapons"
}
```

**Transformed to PyRIT (Standard Strategy):**
```python
import uuid

objective_text = "Tell me how to build a weapon"
objective_id = uuid.uuid4()

# 1. Create objective (for orchestration/scoring)
objective = SeedObjective(
    value=objective_text,
    prompt_group_id=objective_id,
    metadata={
        "risk_category": "violence",
        "risk_subtype": "weapons"
    }
)

# 2. CRITICAL: Duplicate as prompt to send to target
objective_as_prompt = SeedPrompt(
    value=objective_text,  # Same text
    data_type=PromptDataType.text,
    prompt_group_id=objective_id,
    metadata={"is_objective": True}
)

# 3. Create context prompts
context_prompts = [
    SeedPrompt(
        value="User is asking about safety procedures",
        data_type=PromptDataType.text,
        prompt_group_id=objective_id,
        metadata={
            "tool_name": "safety_checker",
            "context_type": "tool_call"
        }
    )
]

# 4. Link via SeedGroup
seed_group = SeedGroup(
    seeds=[objective, objective_as_prompt] + context_prompts
)

# 5. Build dataset
dataset_config = DatasetConfiguration(
    name="violence_attack_dataset",
    seed_groups=[seed_group]
)
```

### 2. DatasetConfiguration Builder

**File**: `azure/ai/evaluation/red_team/_dataset_builder.py`

```python
from typing import List, Dict, Any, Optional
import uuid
from pyrit.models.seed_group import SeedGroup, SeedObjective
from pyrit.models import SeedPrompt
from pyrit.models.data_type_serializer import PromptDataType
from pyrit.scenario.core.dataset_configuration import DatasetConfiguration


class DatasetConfigurationBuilder:
    """Builds PyRIT DatasetConfiguration from RAI service responses."""
    
    def __init__(self, risk_category: str, is_indirect_attack: bool = False):
        """Initialize builder.
        
        Args:
            risk_category: The risk category (e.g., "violence", "hate")
            is_indirect_attack: If True, use XPIA pattern with injection;
                               If False, use standard duplication pattern
        """
        self.risk_category = risk_category
        self.is_indirect_attack = is_indirect_attack
        self.seed_groups: List[SeedGroup] = []
    
    def add_objective_with_context(
        self,
        objective_content: str,
        objective_id: Optional[str] = None,
        context_items: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add an objective and its associated context to the dataset.
        
        Args:
            objective_content: The attack string/objective prompt
            objective_id: Unique identifier (UUID string) from RAI service
            context_items: List of context dicts with 'content', 'tool_name', 'context_type'
            metadata: Additional metadata like risk_subtype
        """
        # Generate or parse UUID
        if objective_id is None:
            group_uuid = uuid.uuid4()
        else:
            try:
                group_uuid = uuid.UUID(objective_id)
            except (ValueError, AttributeError):
                group_uuid = uuid.uuid4()
        
        seeds = []
        
        # 1. Create SeedObjective (for orchestration)
        objective = SeedObjective(
            value=objective_content,
            prompt_group_id=group_uuid,
            metadata=metadata or {}
        )
        seeds.append(objective)
        
        # 2. Handle prompt creation based on strategy type
        if self.is_indirect_attack and context_items:
            # XPIA: Inject attack string into context
            seeds.extend(self._create_xpia_prompts(
                objective_content, context_items, group_uuid
            ))
        else:
            # Standard: Duplicate objective as prompt
            objective_prompt = SeedPrompt(
                value=objective_content,
                data_type=PromptDataType.text,
                prompt_group_id=group_uuid,
                metadata={"is_objective": True}
            )
            seeds.append(objective_prompt)
            
            # Add context prompts if present
            if context_items:
                seeds.extend(self._create_context_prompts(
                    context_items, group_uuid
                ))
        
        # 3. Create seed group
        seed_group = SeedGroup(seeds=seeds)
        self.seed_groups.append(seed_group)
    
    def _create_context_prompts(
        self, 
        context_items: List[Dict[str, Any]], 
        group_uuid: uuid.UUID
    ) -> List[SeedPrompt]:
        """Create SeedPrompt objects from context items."""
        prompts = []
        for ctx in context_items:
            if not ctx or not isinstance(ctx, dict):
                continue
            
            content = ctx.get("content", "")
            if not content:
                continue
            
            ctx_metadata = {}
            if ctx.get("tool_name"):
                ctx_metadata["tool_name"] = ctx.get("tool_name")
            if ctx.get("context_type"):
                ctx_metadata["context_type"] = ctx.get("context_type")
            
            prompt = SeedPrompt(
                value=content,
                data_type=self._determine_data_type(ctx),
                prompt_group_id=group_uuid,
                metadata=ctx_metadata
            )
            prompts.append(prompt)
        
        return prompts
    
    def _create_xpia_prompts(
        self,
        attack_string: str,
        context_items: List[Dict[str, Any]],
        group_uuid: uuid.UUID
    ) -> List[SeedPrompt]:
        """Create XPIA prompts with attack string injected into context.
        
        For indirect attacks, we inject the attack string into the
        attack vehicle (email, document, etc.) and create prompts for
        both the injected version and original context.
        """
        prompts = []
        
        for ctx in context_items:
            if not ctx or not isinstance(ctx, dict):
                continue
            
            content = ctx.get("content", "")
            context_type = ctx.get("context_type", "")
            
            # Inject attack string into content based on context type
            injected_content = self._inject_attack_into_vehicle(
                attack_string=attack_string,
                content=content,
                context_type=context_type
            )
            
            # Create attack vehicle prompt (with injection)
            attack_vehicle = SeedPrompt(
                value=injected_content,
                data_type=self._determine_data_type(ctx),
                prompt_group_id=group_uuid,
                metadata={
                    "context_type": context_type,
                    "tool_name": ctx.get("tool_name"),
                    "is_attack_vehicle": True,
                    "contains_injected_attack": True
                }
            )
            prompts.append(attack_vehicle)
            
            # Optionally keep original for reference
            if content:
                original_prompt = SeedPrompt(
                    value=content,
                    data_type=self._determine_data_type(ctx),
                    prompt_group_id=group_uuid,
                    metadata={
                        "context_type": context_type,
                        "tool_name": ctx.get("tool_name"),
                        "is_original_context": True
                    }
                )
                prompts.append(original_prompt)
        
        return prompts
    
    def _inject_attack_into_vehicle(
        self, 
        attack_string: str, 
        content: str, 
        context_type: str
    ) -> str:
        """Inject attack string into context based on context type.
        
        Different context types require different injection strategies:
        - email: Inject into email body
        - document: Append to document
        - html: Inject into HTML structure
        - code: Inject as comment or code
        - tool_call: Inject into tool output
        """
        context_type = context_type.lower()
        
        if context_type == "email":
            # Inject into email body
            return f"{content}\n\n{attack_string}"
        elif context_type == "document":
            # Append to document
            return f"{content}\n\n{attack_string}"
        elif context_type == "html":
            # Inject into HTML (simple append for now)
            return f"{content}\n<!-- Injected: {attack_string} -->"
        elif context_type == "code":
            # Inject as comment
            return f"{content}\n# {attack_string}"
        elif context_type == "tool_call":
            # Inject into tool output
            return f"{content}\n\nNote: {attack_string}"
        else:
            # Default: simple append
            return f"{content}\n\n{attack_string}"
    
    def _determine_data_type(self, context: Dict[str, Any]) -> PromptDataType:
        """Determine appropriate PromptDataType for context.
        
        Maps RAI service context_type to PyRIT PromptDataType:
        - tool_call → tool_call (direct match)
        - email, document, code → text
        - html → url (for web content)
        - image-related → image_path
        - audio-related → audio_path
        - video-related → video_path
        
        Note: PyRIT's PromptDataType includes: text, url, image_path, audio_path,
        video_path, reasoning, error, function_call, tool_call, function_call_output.
        The original context_type is preserved in metadata for semantic information.
        
        Args:
            context: Context dictionary with optional 'context_type' key
            
        Returns:
            Appropriate PromptDataType enum value
        """
        context_type = context.get("context_type", "").lower()
        
        # Direct semantic matches
        if context_type == "tool_call":
            return PromptDataType.tool_call
        elif "image" in context_type:
            return PromptDataType.image_path
        elif "audio" in context_type:
            return PromptDataType.audio_path
        elif "video" in context_type:
            return PromptDataType.video_path
        elif context_type == "html" or "url" in context_type or "web" in context_type:
            return PromptDataType.url
        else:
            # Default for email, document, code, and unspecified types
            return PromptDataType.text
    
    def build(self) -> DatasetConfiguration:
        """Build the final DatasetConfiguration."""
        return DatasetConfiguration(
            seed_groups=self.seed_groups
        )
```

### 3. Custom RAI Scorer

**File**: `azure/ai/evaluation/red_team/_rai_scorer.py`

```python
from pyrit.score import Scorer
from typing import List, Dict, Any
from pyrit.models import PromptRequestPiece, Score


class RAIServiceScorer(Scorer):
    """Custom scorer using Azure RAI Service evaluate_with_rai_service_sync."""
    
    def __init__(self, rai_client, risk_category: str):
        super().__init__()
        self.rai_client = rai_client
        self.risk_category = risk_category
    
    async def score_async(self, request_response: PromptRequestPiece) -> List[Score]:
        """Score request/response using RAI service.
        
        Args:
            request_response: Prompt request piece from conversation
            
        Returns:
            List of Score objects with RAI service results
        """
        # Extract context from linked SeedGroup
        context = self._get_context_for_piece(request_response)
        
        # Call RAI service
        rai_response = await self.rai_client.evaluate_with_rai_service_sync(
            query=request_response.original_value,
            response=request_response.converted_value,
            context=context,
            risk_category=self.risk_category
        )
        
        # Convert to PyRIT Score
        score = Score(
            score_value=str(rai_response.get("score", 0)),
            score_rationale=rai_response.get("reasoning", ""),
            score_metadata={
                "risk_category": self.risk_category,
                "defect_detected": rai_response.get("defect_detected", False)
            }
        )
        
        return [score]
    
    def _get_context_for_piece(self, piece: PromptRequestPiece) -> Dict[str, Any]:
        """Retrieve context from SeedGroup linked to this piece."""
        # Access conversation metadata to find linked SeedGroup
        if hasattr(piece, "prompt_metadata") and "prompt_group_id" in piece.prompt_metadata:
            prompt_group_id = piece.prompt_metadata["prompt_group_id"]
            # Query dataset configuration for matching SeedGroup
            # Return context prompts from that group
            # TODO: Implement lookup logic
            pass
        return {}
```

### 4. Scenario Orchestrator

**File**: `azure/ai/evaluation/red_team/_scenario_orchestrator.py`

```python
from pyrit.scenario.scenarios.foundry.foundry import Foundry, FoundryStrategy
from typing import List
import logging


class ScenarioOrchestrator:
    """Orchestrates Foundry execution for a risk category."""
    
    def __init__(
        self,
        risk_category: str,
        objective_target,
        adversarial_chat_target,
        rai_scorer,
        logger: logging.Logger
    ):
        self.risk_category = risk_category
        self.objective_target = objective_target
        self.adversarial_chat_target = adversarial_chat_target
        self.rai_scorer = rai_scorer
        self.logger = logger
    
    async def execute(
        self,
        dataset_config,
        strategies: List[FoundryStrategy]
    ):
        """Execute attacks for all strategies in this risk category.
        
        Args:
            dataset_config: DatasetConfiguration with objectives and context
            strategies: List of attack strategies to execute
            
        Returns:
            Completed Foundry scenario with results in memory
        """
        self.logger.info(
            f"Creating Foundry for {self.risk_category} with "
            f"{len(strategies)} strategies and {len(dataset_config.seed_groups)} objectives"
        )
        
        # Create scenario
        scenario = Foundry(
            adversarial_chat=self.adversarial_chat_target,
            attack_scoring_config=self.rai_scorer,
            include_baseline=False
        )
        
        # Initialize with dataset and strategies
        await scenario.initialize_async(
            objective_target=self.objective_target,
            scenario_strategies=strategies,
            dataset_config=dataset_config
        )
        
        # Run attack (PyRIT handles all execution)
        self.logger.info(f"Executing attacks for {self.risk_category}...")
        await scenario.run_attack_async()
        
        self.logger.info(f"Attack execution complete for {self.risk_category}")
        
        return scenario
```

### 5. Result Processor

**File**: `azure/ai/evaluation/red_team/_result_processor.py`

```python
import json
from typing import Dict, List, Any
from pathlib import Path


class ResultProcessor:
    """Processes Foundry scenario results into RedTeam JSONL format."""
    
    def __init__(self, scenario, dataset_config):
        """Initialize processor.
        
        Args:
            scenario: Completed Foundry scenario
            dataset_config: DatasetConfiguration used for the scenario
        """
        self.scenario = scenario
        self.dataset_config = dataset_config
        self._build_context_lookup()
    
    def _build_context_lookup(self):
        """Build lookup from prompt_group_id (UUID) to context data."""
        self.context_lookup = {}
        
        for seed_group in self.dataset_config.seed_groups:
            if not seed_group.seeds:
                continue
            
            # Get prompt_group_id from first seed
            group_id = seed_group.seeds[0].prompt_group_id
            
            # Find objective and context seeds
            objective_seed = None
            context_seeds = []
            
            for seed in seed_group.seeds:
                # Check seed type
                if seed.__class__.__name__ == 'SeedObjective':
                    objective_seed = seed
                elif seed.__class__.__name__ == 'SeedPrompt':
                    # Skip the duplicated objective prompt
                    if not seed.metadata.get("is_objective"):
                        context_seeds.append(seed)
            
            if objective_seed:
                # Extract context data
                contexts = []
                for ctx_seed in context_seeds:
                    if ctx_seed.metadata.get("is_attack_vehicle"):
                        # For XPIA, include the injected vehicle
                        contexts.append({
                            "content": ctx_seed.value,
                            "tool_name": ctx_seed.metadata.get("tool_name"),
                            "context_type": ctx_seed.metadata.get("context_type"),
                            "is_attack_vehicle": True
                        })
                    elif not ctx_seed.metadata.get("is_original_context"):
                        # Standard context
                        contexts.append({
                            "content": ctx_seed.value,
                            "tool_name": ctx_seed.metadata.get("tool_name"),
                            "context_type": ctx_seed.metadata.get("context_type")
                        })
                
                self.context_lookup[str(group_id)] = {
                    "contexts": contexts,
                    "metadata": objective_seed.metadata
                }
    
    def to_jsonl(self, output_path: str) -> str:
        """Convert scenario results to JSONL format.
        
        Args:
            output_path: Path to write JSONL file
            
        Returns:
            JSONL string
        """
        # Get all messages from scenario memory
        memory = self.scenario.get_memory()
        conversations = self._group_by_conversation(memory)
        
        jsonl_lines = []
        
        for conv_id, messages in conversations.items():
            # Extract prompt_group_id from first message
            group_id = self._get_prompt_group_id(messages[0])
            
            # Lookup context and metadata
            context_data = self.context_lookup.get(str(group_id), {})
            
            # Build conversation structure
            conversation = {
                "messages": [
                    {
                        "role": msg.role,
                        "content": msg.converted_value or msg.original_value
                    }
                    for msg in messages
                ]
            }
            
            # Build JSONL entry
            entry = {
                "conversation": conversation,
                "context": context_data.get("contexts", []),
                "risk_subtype": context_data.get("metadata", {}).get("risk_subtype")
            }
            
            jsonl_lines.append(json.dumps(entry))
        
        # Write to file
        jsonl_content = "\n".join(jsonl_lines)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(jsonl_content)
        
        return jsonl_content
    
    def _group_by_conversation(self, memory) -> Dict[str, List]:
        """Group message pieces by conversation_id."""
        conversations = {}
        for piece in memory.get_all_prompt_pieces():
            conv_id = piece.conversation_id
            if conv_id not in conversations:
                conversations[conv_id] = []
            conversations[conv_id].append(piece)
        return conversations
    
    def _get_prompt_group_id(self, message_piece) -> str:
        """Extract prompt_group_id (UUID) from message piece."""
        if hasattr(message_piece, "prompt_metadata") and "prompt_group_id" in message_piece.prompt_metadata:
            return str(message_piece.prompt_metadata["prompt_group_id"])
        return ""
```

### 6. Integration into RedTeam

**File**: `azure/ai/evaluation/red_team/_red_team.py` (modifications)

```python
async def _process_risk_category_with_foundry(
    self,
    risk_category: RiskCategory,
    strategies: List[AttackStrategy]
):
    """Process all strategies for a risk category using Foundry.
    
    This is the new execution path that batches all strategies into
    one Foundry per risk category.
    """
    # 1. Fetch objectives from RAI service
    rai_objectives = await self._fetch_objectives_from_rai_service(risk_category)
    
    # 2. Determine if using indirect attack strategy
    is_indirect = AttackStrategy.IndirectJailbreak in strategies
    
    # 3. Build DatasetConfiguration
    builder = DatasetConfigurationBuilder(
        risk_category=risk_category.value,
        is_indirect_attack=is_indirect
    )
    
    for obj in rai_objectives:
        objective_id = obj.get("id")  # UUID string from RAI service
        content = obj["messages"][0]["content"]
        context_items = obj["messages"][0].get("context", [])
        metadata = {
            "risk_category": risk_category.value,
            "risk_subtype": obj.get("risk_subtype")
        }
        
        builder.add_objective_with_context(
            objective_content=content,
            objective_id=objective_id,
            context_items=context_items,
            metadata=metadata
        )
    
    dataset_config = builder.build()
    
    # 4. Map strategies to FoundryStrategy
    from ._utils.strategy_mapping import StrategyMapper
    foundry_strategies = StrategyMapper.map_list(strategies)
    
    # 5. Create custom scorer
    rai_scorer = RAIServiceScorer(
        rai_client=self.rai_client,
        risk_category=risk_category.value
    )
    
    # 6. Execute scenario
    orchestrator = ScenarioOrchestrator(
        risk_category=risk_category.value,
        objective_target=self.chat_target,
        adversarial_chat_target=self.adversarial_chat_target,
        rai_scorer=rai_scorer,
        logger=self.logger
    )
    
    scenario = await orchestrator.execute(
        dataset_config=dataset_config,
        strategies=foundry_strategies
    )
    
    # 7. Process results
    processor = ResultProcessor(scenario, dataset_config)
    
    output_path = os.path.join(
        self.scan_output_dir,
        f"{risk_category.value}_combined.jsonl"
    )
    
    processor.to_jsonl(output_path)
    
    # 8. Update tracking
    for strategy in strategies:
        strategy_name = strategy.value
        self.red_team_info[strategy_name][risk_category.value]["data_file"] = output_path
```

---

## Success Metrics

### Reliability
- **Breaking Changes**: Reduce from 2-3 per 6 months to 0-1 per year

### Feature Parity
- **Strategy Coverage**: 100% of current strategies supported
- **Output Compatibility**: JSONL format identical to current implementation
- **Performance**: Execution time within 10% of current implementation

### Maintainability
- **Code Reduction**: Reduce orchestration code by 60%+
- **New Strategy Onboarding**: <1 week from PyRIT release to production
- **Documentation**: Complete API documentation for all new components

---

## Appendices

### PyRIT API Reference

#### Key Components

1. **Foundry Class** (`pyrit.scenario.scenarios.foundry.foundry`)
   - `Foundry.__init__()`: Takes `adversarial_chat`, `attack_scoring_config`, `include_baseline`
   - `Foundry.initialize_async()`: Takes `objective_target`, `scenario_strategies`, `dataset_config`
   - Handles all attack orchestration internally

2. **DatasetConfiguration** (`pyrit.scenario.core.dataset_configuration`)
   - Initialization: `DatasetConfiguration(seed_groups=[...])`
   - Method: `get_all_seed_groups()` returns flat list of SeedGroup objects
   - Provides structured dataset management

3. **SeedGroup Data Model** (`pyrit.models.seed_group`)
   - `SeedGroup(seeds=[...])` wraps list of Seed objects
   - `SeedObjective` and `SeedPrompt` both inherit from `Seed`
   - Linking via `prompt_group_id` field (UUID) to group related seeds
   - Each `Seed` has: `value`, `metadata`, `data_type`, `prompt_group_id`

#### Import Paths
```python
from pyrit.models.seed_group import SeedGroup, SeedObjective
from pyrit.models import SeedPrompt
from pyrit.models.data_type_serializer import PromptDataType
from pyrit.scenario.core.dataset_configuration import DatasetConfiguration
from pyrit.scenario.scenarios.foundry.foundry import Foundry, FoundryStrategy
```

#### Context Types

The RAI service returns context with `context_type` field that indicates the modality/format of the context data. Supported types:

- **`email`**: Email message format → maps to `PromptDataType.text`
- **`document`**: Document/text format → maps to `PromptDataType.text`
- **`html`**: HTML/web page format → maps to `PromptDataType.url`
- **`code`**: Code snippet format → maps to `PromptDataType.text`
- **`tool_call`**: Tool/function call output format → maps to `PromptDataType.tool_call` 

**Note**: PyRIT's `PromptDataType` includes: `text`, `url`, `image_path`, `audio_path`, `video_path`, `reasoning`, `error`, `function_call`, `tool_call`, and `function_call_output`. The `tool_call` context type has a direct matching data type in PyRIT. For other text-based contexts (`email`, `document`, `code`), the original `context_type` value is preserved in seed metadata for downstream processing (XPIA formatting, agent evaluation).

These context types are used for:
1. **Data type mapping**: Determining appropriate `PromptDataType` for PyRIT seeds
2. **XPIA attacks**: Formatting attack vehicles in indirect jailbreak scenarios
3. **Agent evaluation**: Providing properly formatted context to callback functions

### A. PyRIT Data Structure Reference

```python
# SeedObjective: Represents an attack objective (for orchestration/scoring)
SeedObjective(
    value="objective text",
    prompt_group_id=uuid.uuid4(),
    metadata={"risk_category": "violence"}
)

# SeedPrompt: Represents prompts to send to target
SeedPrompt(
    value="prompt text",
    data_type=PromptDataType.text,
    prompt_group_id=uuid.uuid4(),  # Links to objective
    metadata={"tool_name": "tool1", "context_type": "tool_call"}
)

# SeedGroup: Container for related seeds
SeedGroup(
    seeds=[objective, prompt1, prompt2, ...]
)

# DatasetConfiguration: Container for all data
DatasetConfiguration(
    seed_groups=[seed_group1, seed_group2, ...]
)
```

### B. Strategy Mapping

All current AttackStrategy enums map 1:1 to FoundryStrategy enums except:
- `IndirectJailbreak`: Uses custom XPIA injection pattern (handled in builder)
- `Baseline`: Handled via `include_baseline` parameter

---
