#!/usr/bin/bash
fix_samples(){
  for fle in `ls $1/*.py | grep agent`;
  do
    new_name="`echo "$fle" | sed "s/agent/assistant/g"`"
    echo "$fle - > $new_name"
    sed "s/gent/ssistant/g" "$fle" \
     | sed "s/azure-ai-projects/azure-ai-assistants/g" \
     | sed "s/ai.projects/ai.assistants/g" \
     | sed "s/AIProjectClient/AssistantsClient/g" \
     | sed "s/project_client.assistants/project_client/g" \
     | sed "s/project_client/assistants_client/g" > $new_name
     rm -f "$fle"
  done
}

#fix_samples async_samples
#fix_samples .
#fix_samples multiagent
fix_samples ../tests