#!/usr/bin/env python3
"""
Script to remove unused model classes from azure-ai-agentserver-core _models.py
"""

import re
from typing import Set, List
from pathlib import Path

# Keep only these models (from the dependency analysis)
KEEP_MODELS = {
    'AgentId', 'AgentReference', 'CreateResponse', 'CreatedBy',
    'FunctionToolCallItemResource', 'FunctionToolCallOutputItemResource', 
    'ItemContent', 'ItemContentOutputText', 'ItemParam', 'ItemResource',
    'Response', 'ResponseCompletedEvent', 'ResponseContentPartAddedEvent',
    'ResponseContentPartDoneEvent', 'ResponseCreatedEvent', 'ResponseErrorEvent', 
    'ResponseFunctionCallArgumentsDeltaEvent', 'ResponseFunctionCallArgumentsDoneEvent',
    'ResponseInProgressEvent', 'ResponseOutputItemAddedEvent', 'ResponseOutputItemDoneEvent',
    'ResponseStreamEvent', 'ResponseTextDeltaEvent', 'ResponseTextDoneEvent',
    'ResponsesAssistantMessageItemResource', 'ResponsesMessageItemResource', 'Tool'
}

def extract_class_blocks(content: str) -> List[tuple[str, int, int, str]]:
    """Extract all class definitions and their line ranges."""
    lines = content.split('\n')
    classes = []
    current_class = None
    current_start = None
    
    for i, line in enumerate(lines):
        if line.strip().startswith('class '):
            # Save previous class if exists
            if current_class and current_start is not None:
                classes.append((current_class, current_start, i - 1, '\n'.join(lines[current_start:i])))
            
            # Parse new class
            match = re.match(r'class\s+(\w+)', line)
            if match:
                current_class = match.group(1)
                current_start = i
        elif current_class and line.strip() and not line.startswith((' ', '\t', '#')):
            # This is the start of something new (not a class member)
            if not line.strip().startswith('class '):
                # Save current class and reset
                if current_start is not None:
                    classes.append((current_class, current_start, i - 1, '\n'.join(lines[current_start:i])))
                current_class = None
                current_start = None
    
    # Handle last class
    if current_class and current_start is not None:
        classes.append((current_class, current_start, len(lines) - 1, '\n'.join(lines[current_start:])))
    
    return classes

def remove_unused_models(file_path: Path, keep_models: Set[str]) -> str:
    """Remove unused model classes from the file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    classes = extract_class_blocks(content)
    
    print(f"Found {len(classes)} class definitions")
    
    # Mark lines to remove
    lines_to_remove = set()
    removed_classes = []
    
    for class_name, start_line, end_line, class_content in classes:
        if class_name not in keep_models:
            print(f"Removing class {class_name} (lines {start_line + 1}-{end_line + 1})")
            removed_classes.append(class_name)
            for line_num in range(start_line, end_line + 1):
                lines_to_remove.add(line_num)
    
    # Create new content without removed lines
    new_lines = []
    for i, line in enumerate(lines):
        if i not in lines_to_remove:
            new_lines.append(line)
    
    new_content = '\n'.join(new_lines)
    
    # Clean up any double newlines that might have been created
    new_content = re.sub(r'\n\n\n+', '\n\n', new_content)
    
    print(f"Removed {len(removed_classes)} classes:")
    for cls in sorted(removed_classes):
        print(f"  - {cls}")
    
    return new_content

def main():
    models_file = Path("c:/Users/llawrence/Desktop/Repo/azure-sdk-for-python/sdk/agentserver/azure-ai-agentserver-core/azure/ai/agentserver/core/models/projects/_models.py")
    backup_file = models_file.with_suffix('.py.backup')
    
    print(f"Creating backup at {backup_file}")
    with open(models_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(original_content)
    
    print(f"Processing {models_file}")
    new_content = remove_unused_models(models_file, KEEP_MODELS)
    
    print(f"Writing updated content to {models_file}")
    with open(models_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Done! File has been updated.")
    
    # Show stats
    original_lines = len(original_content.split('\n'))
    new_lines = len(new_content.split('\n'))
    print(f"Original: {original_lines} lines")
    print(f"New: {new_lines} lines") 
    print(f"Reduced by: {original_lines - new_lines} lines ({((original_lines - new_lines) / original_lines * 100):.1f}%)")

if __name__ == "__main__":
    main()