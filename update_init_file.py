#!/usr/bin/env python3
"""
Script to update the __init__.py file to only export the models that still exist
"""

from pathlib import Path

# Models that we kept (from the removal script)
KEPT_MODELS = {
    'AgentId', 'AgentReference', 'CreatedBy',
    'FunctionToolCallItemResource', 'FunctionToolCallOutputItemResource', 
    'ItemContent', 'ItemContentOutputText', 'ItemParam', 'ItemResource',
    'Response', 'ResponseCompletedEvent', 'ResponseContentPartAddedEvent',
    'ResponseContentPartDoneEvent', 'ResponseCreatedEvent', 'ResponseErrorEvent', 
    'ResponseFunctionCallArgumentsDeltaEvent', 'ResponseFunctionCallArgumentsDoneEvent',
    'ResponseInProgressEvent', 'ResponseOutputItemAddedEvent', 'ResponseOutputItemDoneEvent',
    'ResponseStreamEvent', 'ResponseTextDeltaEvent', 'ResponseTextDoneEvent',
    'ResponsesAssistantMessageItemResource', 'ResponsesMessageItemResource', 'Tool'
}

def update_init_file():
    init_file = Path("c:/Users/llawrence/Desktop/Repo/azure-sdk-for-python/sdk/agentserver/azure-ai-agentserver-core/azure/ai/agentserver/core/models/projects/__init__.py")
    backup_file = init_file.with_suffix('.py.backup')
    
    print(f"Creating backup at {backup_file}")
    with open(init_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(original_content)
    
    lines = original_content.split('\n')
    new_lines = []
    in_imports_section = False
    in_all_section = False
    
    for line in lines:
        if line.strip().startswith('from ._models import'):
            in_imports_section = True
            new_lines.append(line)
        elif in_imports_section and line.strip().startswith(')'):
            # End of imports section
            in_imports_section = False
            new_lines.append(line)
        elif in_imports_section:
            # Check if this line contains a model import
            stripped = line.strip()
            if stripped.endswith(','):
                model_name = stripped[:-1].strip()
            else:
                model_name = stripped
            
            if model_name in KEPT_MODELS:
                new_lines.append(line)
            else:
                print(f"Removing import: {model_name}")
        elif line.strip().startswith('__all__'):
            in_all_section = True
            new_lines.append(line)
        elif in_all_section and line.strip().startswith(']'):
            # End of __all__ section
            in_all_section = False
            new_lines.append(line)
        elif in_all_section:
            # Check if this line contains a model in __all__
            stripped = line.strip()
            if stripped.startswith('"') and stripped.endswith('",'):
                model_name = stripped[1:-2]  # Remove quotes and comma
            elif stripped.startswith('"') and stripped.endswith('"'):
                model_name = stripped[1:-1]  # Remove quotes
            else:
                model_name = ''
            
            if model_name in KEPT_MODELS:
                new_lines.append(line)
            else:
                if model_name:
                    print(f"Removing from __all__: {model_name}")
        else:
            new_lines.append(line)
    
    new_content = '\n'.join(new_lines)
    
    # Clean up any extra newlines
    import re
    new_content = re.sub(r'\n\n\n+', '\n\n', new_content)
    
    print(f"Writing updated __init__.py")
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Done!")

if __name__ == "__main__":
    update_init_file()