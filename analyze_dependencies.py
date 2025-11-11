#!/usr/bin/env python3
"""
Script to analyze model dependencies in the azure-ai-agentserver-core package
and identify which models can be safely removed.
"""

import re
import ast
from typing import Set, Dict, List, Tuple
from pathlib import Path

# Models that are directly imported by the other packages
REQUIRED_MODELS = {
    # From base models
    'CreateResponse',  # From _create_response.py, but needs AgentReference
    'Response',
    'ResponseStreamEvent',
    
    # From projects models - specifically imported
    'AgentId', 
    'ItemContentOutputText',  # inherits from ItemContent
    'ResponsesAssistantMessageItemResource',  # inherits from ResponsesMessageItemResource -> ItemResource
    'FunctionToolCallItemResource',  # inherits from ItemResource
    'FunctionToolCallOutputItemResource',  # inherits from ItemResource
    'ResponseCompletedEvent',  # inherits from ResponseStreamEvent
    'ResponseContentPartAddedEvent',  # inherits from ResponseStreamEvent
    'ResponseContentPartDoneEvent',  # inherits from ResponseStreamEvent
    'ResponseCreatedEvent',  # inherits from ResponseStreamEvent
    'ResponseErrorEvent',  # inherits from ResponseStreamEvent
    'ResponseFunctionCallArgumentsDeltaEvent',  # inherits from ResponseStreamEvent
    'ResponseFunctionCallArgumentsDoneEvent',  # inherits from ResponseStreamEvent
    'ResponseInProgressEvent',  # inherits from ResponseStreamEvent
    'ResponseOutputItemAddedEvent',  # inherits from ResponseStreamEvent
    'ResponseOutputItemDoneEvent',  # inherits from ResponseStreamEvent
    'ResponseTextDeltaEvent',  # inherits from ResponseStreamEvent
    'ResponseTextDoneEvent',  # inherits from ResponseStreamEvent
    
    # From CreateResponse dependency
    'AgentReference',
    
    # Additional dependencies that are needed
    'ItemContent',  # base class for ItemContentOutputText
    'ItemResource',  # base class for function tool call resources and messages
    'ResponsesMessageItemResource',  # parent of ResponsesAssistantMessageItemResource
    'CreatedBy',  # referenced by ItemResource
}

# Enums that are referenced
REQUIRED_ENUMS = {
    'ResponsesMessageRole',
}

def parse_class_definition(line: str) -> Tuple[str, List[str]]:
    """Parse a class definition line to extract class name and parent classes."""
    # Match class definition with optional inheritance
    match = re.match(r'class\s+(\w+)(\([^)]*\))?\s*:', line)
    if not match:
        return '', []
    
    class_name = match.group(1)
    parents_str = match.group(2)
    
    parents = []
    if parents_str:
        # Remove parentheses and split by comma
        parents_str = parents_str.strip('()')
        for parent in parents_str.split(','):
            parent = parent.strip()
            # Handle discriminator parameters
            if '=' not in parent:
                parents.append(parent)
    
    return class_name, parents

def extract_type_references(class_content: str) -> Set[str]:
    """Extract all type references from class content."""
    references = set()
    
    # Find type annotations
    type_annotations = re.findall(r':\s*([^=\n]+)', class_content)
    for annotation in type_annotations:
        # Extract model names from type annotations
        model_refs = re.findall(r'"_models\.(\w+)"', annotation)
        references.update(model_refs)
        
        # Also check for direct references
        model_refs = re.findall(r'_models\.(\w+)', annotation)
        references.update(model_refs)
        
        # Check for Union types
        union_refs = re.findall(r'Union\[[^\]]*"_models\.(\w+)"[^\]]*\]', annotation)
        references.update(union_refs)
    
    return references

def analyze_models_file(file_path: Path) -> Dict[str, Dict]:
    """Analyze the _models.py file to extract all class definitions and their dependencies."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    models = {}
    current_class = None
    current_content = []
    
    for i, line in enumerate(lines):
        # Check if this is a class definition
        if line.strip().startswith('class '):
            # Save previous class if exists
            if current_class:
                class_content = '\n'.join(current_content)
                type_refs = extract_type_references(class_content)
                models[current_class]['type_references'] = type_refs
            
            # Parse new class
            class_name, parents = parse_class_definition(line)
            if class_name:
                current_class = class_name
                models[class_name] = {
                    'line_number': i + 1,
                    'parents': parents,
                    'type_references': set()
                }
                current_content = [line]
        elif current_class:
            current_content.append(line)
            # Stop collecting when we hit the next class or end
            if line.strip() and not line.startswith(' ') and not line.startswith('\t') and not line.startswith('#'):
                if not line.strip().startswith('class '):
                    current_content.pop()  # Remove the non-class line
                    break
    
    # Handle last class
    if current_class:
        class_content = '\n'.join(current_content)
        type_refs = extract_type_references(class_content)
        models[current_class]['type_references'] = type_refs
    
    return models

def find_dependencies(models: Dict[str, Dict], required_set: Set[str]) -> Set[str]:
    """Find all dependencies of the required models."""
    all_required = set(required_set)
    to_process = list(required_set)
    
    # Add known base classes that are definitely needed
    base_classes = {'_Model', 'Model', 'ItemResource', 'ItemParam', 'Tool', 'ItemContent', 'CreatedBy'}
    for base in base_classes:
        if base in models:
            all_required.add(base)
            to_process.append(base)
    
    while to_process:
        current = to_process.pop()
        if current not in models:
            continue  # Skip if not in our models (might be from base library)
        
        model_info = models[current]
        
        # Add parent classes
        for parent in model_info['parents']:
            # Clean up parent name (remove _Model, etc.)
            clean_parent = parent.strip()
            if clean_parent == '_Model':
                clean_parent = 'Model'  # This is just the base model class
                continue  # Skip _Model as it's imported from utils
            
            if clean_parent not in all_required and clean_parent in models:
                all_required.add(clean_parent)
                to_process.append(clean_parent)
        
        # Add type references
        for ref in model_info['type_references']:
            if ref not in all_required and ref in models:
                all_required.add(ref)
                to_process.append(ref)
    
    # Remove _Model if it was added, as it's from utils
    all_required.discard('_Model')
    all_required.discard('Model')
    
    return all_required

def main():
    models_file = Path("c:/Users/llawrence/Desktop/Repo/azure-sdk-for-python/sdk/agentserver/azure-ai-agentserver-core/azure/ai/agentserver/core/models/projects/_models.py")
    
    print("Analyzing models file...")
    models = analyze_models_file(models_file)
    print(f"Found {len(models)} model classes")
    
    print("\nFinding dependencies...")
    all_required = find_dependencies(models, REQUIRED_MODELS)
    
    print(f"\nRequired models (including dependencies): {len(all_required)}")
    for model in sorted(all_required):
        print(f"  - {model}")
    
    print(f"\nModels that can be removed: {len(models) - len(all_required)}")
    removable = set(models.keys()) - all_required
    for model in sorted(removable):
        print(f"  - {model}")
    
    print(f"\nSummary:")
    print(f"Total models: {len(models)}")
    print(f"Required models: {len(all_required)}")
    print(f"Removable models: {len(removable)}")

if __name__ == "__main__":
    main()