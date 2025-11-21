#!/usr/bin/env python3
"""
Generate .env file from Azure AI Project endpoint.

This script discovers all necessary configuration by inspecting:
- Available model deployments
- Connected resources (Bing, AI Search, GitHub, etc.)
- AI Search indexes
- Project metadata

Usage:
    python generate_env_file.py <project_endpoint> [output_name]
    
Example:
    python generate_env_file.py https://my-project.services.ai.azure.com/api/projects/my-project e2etests
    
Output:
    Creates .env.generated.<output_name> file with discovered settings
"""

import sys
import os
import argparse
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential


def discover_model_deployment(project_client):
    """Find the default or best model deployment."""
    print("🔍 Discovering model deployments...")
    
    try:
        from azure.ai.projects.models import ModelDeployment
        
        # List all deployments
        deployments = list(project_client.deployments.list())
        
        if not deployments:
            print("   ⚠️  No deployments found")
            print("   Using default: gpt-4o")
            return "gpt-4o"
        
        # Preferred model order
        preferred_order = ["gpt-4o", "gpt-4", "gpt-35-turbo", "gpt-3.5-turbo"]
        found_deployment = None
        
        # First pass: look for preferred models
        for deployment in deployments:
            if isinstance(deployment, ModelDeployment):
                model_name = deployment.model_name.lower() if deployment.model_name else ""
                deployment_name = deployment.name.lower() if deployment.name else ""
                print(f"   Found deployment: {deployment.name} (Model: {deployment.model_name})")
                
                for preferred in preferred_order:
                    if preferred in model_name or preferred in deployment_name:
                        found_deployment = deployment.name
                        print(f"      ✅ Matches preferred model: {preferred}")
                        break
                
                if found_deployment:
                    break
        
        # If no preferred model found, use the first deployment
        if not found_deployment and deployments:
            first_deployment = deployments[0]
            if isinstance(first_deployment, ModelDeployment):
                found_deployment = first_deployment.name
                print(f"   Using first available deployment: {found_deployment}")
        
        if found_deployment:
            print(f"✅ Selected deployment: {found_deployment}")
            return found_deployment
        else:
            print("   ⚠️  Could not identify suitable deployment")
            print("   Using default: gpt-4o")
            return "gpt-4o"
        
    except Exception as e:
        print(f"⚠️  Could not discover deployments: {e}")
        print("   Using default: gpt-4o")
        return "gpt-4o"


def discover_connections(project_client):
    """Discover all project connections and categorize them."""
    print("\n🔍 Discovering connections...")
    
    connections = {
        "bing": None,
        "ai_search": None,
        "github_pat": None,
        "all": []
    }
    
    try:
        for connection in project_client.connections.list():
            conn_type = str(getattr(connection, 'type', 'Unknown'))
            conn_name = connection.name
            conn_id = connection.id
            is_default = getattr(connection, 'is_default', False)
            
            print(f"   Found: {conn_name} (Type: {conn_type}, Default: {is_default})")
            
            connections["all"].append({
                "name": conn_name,
                "type": conn_type,
                "id": conn_id,
                "is_default": is_default
            })
            
            # Categorize by type
            if "API_KEY" in conn_type and "bing" in conn_name.lower():
                if not connections["bing"] or is_default:
                    connections["bing"] = conn_id
                    print(f"      ✅ Selected as Bing connection")
            
            elif "AZURE_AI_SEARCH" in conn_type:
                if not connections["ai_search"] or is_default:
                    connections["ai_search"] = conn_id
                    print(f"      ✅ Selected as AI Search connection")
            
            elif "CUSTOM" in conn_type and ("github" in conn_name.lower() or "pat" in conn_name.lower()):
                if not connections["github_pat"] or is_default:
                    connections["github_pat"] = conn_id
                    print(f"      ✅ Selected as GitHub PAT connection")
        
        # Fallback: use first of each type if no specific match
        if not connections["bing"]:
            for conn in connections["all"]:
                if "API_KEY" in conn["type"]:
                    connections["bing"] = conn["id"]
                    print(f"   ⚠️  Using fallback Bing connection: {conn['name']}")
                    break
        
        if not connections["github_pat"]:
            for conn in connections["all"]:
                if "CUSTOM" in conn["type"]:
                    connections["github_pat"] = conn["id"]
                    print(f"   ⚠️  Using fallback MCP/GitHub connection: {conn['name']}")
                    break
        
        return connections
        
    except Exception as e:
        error_str = str(e)
        print(f"❌ Error discovering connections: {e}")
        
        # Check if it's a critical error that should stop execution
        if "429" in error_str or "Rate limit" in error_str:
            print("   ⚠️  Rate limit exceeded - this is a temporary error")
            return None  # Signal that we should abort
        elif "404" in error_str:
            print("   ⚠️  Resource not found - check endpoint URL")
            return None
        elif "401" in error_str or "403" in error_str:
            print("   ⚠️  Authentication error - check credentials")
            return None
        
        # For other errors, continue with empty connections
        return connections


def discover_ai_search_index(project_client, ai_search_connection_id):
    """Discover AI Search indexes."""
    print("\n🔍 Discovering AI Search indexes...")
    
    if not ai_search_connection_id:
        print("   ⚠️  No AI Search connection found")
        return "default-index"
    
    try:
        # Try to get AI Search connection details
        connection_name = ai_search_connection_id.split("/")[-1]
        connection = project_client.connections.get(connection_name, include_credentials=True)
        
        if hasattr(connection, 'target') and connection.target:
            print(f"   AI Search endpoint: {connection.target}")
        
        # For now, we can't easily list indexes without additional SDK
        # So we'll look for environment variable or use a default
        # In a real scenario, you'd use Azure Search SDK here
        
        print("   ℹ️  Cannot automatically discover index names")
        print("   ℹ️  Using placeholder - you may need to update this manually")
        return "vector-index"
        
    except Exception as e:
        print(f"   ⚠️  Could not query AI Search: {e}")
        return "vector-index"


def generate_env_file(project_endpoint, output_name="default"):
    """Generate .env file from project endpoint."""
    
    print("="*80)
    print("AZURE AI PROJECT .ENV GENERATOR")
    print("="*80)
    print(f"\n📍 Project Endpoint: {project_endpoint}")
    print(f"📄 Output File: .env.generated.{output_name}")
    print()
    
    # Create project client
    try:
        credential = DefaultAzureCredential()
        # Extract subscription, resource group, and project from endpoint
        # Format: https://<account>.services.ai.azure.com/api/projects/<project>
        project_client = AIProjectClient(
            endpoint=project_endpoint,
            credential=credential
        )
        print("✅ Connected to project")
    except Exception as e:
        print(f"❌ Failed to connect to project: {e}")
        sys.exit(1)
    
    # Discover all settings
    model_deployment = discover_model_deployment(project_client)
    connections = discover_connections(project_client)
    
    # Check if we got critical errors
    if connections is None or len(connections.get("all", [])) == 0:
        print("\n❌ FATAL ERROR: Could not discover any connections")
        print("   This likely indicates an API error (rate limit, authentication, etc.)")
        print("   No .env file will be generated. Please retry after resolving the issue.")
        sys.exit(1)
    
    ai_search_index = discover_ai_search_index(project_client, connections["ai_search"])
    
    # Generate .env content
    print("\n" + "="*80)
    print("GENERATING .ENV FILE")
    print("="*80)
    
    env_content = f"""# Auto-generated by generate_env_file.py
# Project: {project_endpoint}
# Generated: {os.popen('date /t').read().strip() if os.name == 'nt' else os.popen('date').read().strip()}

AZURE_AI_PROJECT_ENDPOINT={project_endpoint}
AZURE_AI_MODEL_DEPLOYMENT_NAME={model_deployment}

# Test configuration - for running tests in live mode without recording
AZURE_TEST_RUN_LIVE=true
AZURE_SKIP_LIVE_RECORDING=true

# Test environment variables (map from .env to test expected names)
# All these are required by the servicePreparer in test_base.py
AZURE_AI_PROJECTS_TESTS_PROJECT_ENDPOINT={project_endpoint}
AZURE_AI_PROJECTS_TESTS_AGENTS_PROJECT_ENDPOINT={project_endpoint}
AZURE_AI_PROJECTS_TESTS_TRACING_PROJECT_ENDPOINT={project_endpoint}

# Container App settings (placeholders - update if needed)
AZURE_AI_PROJECTS_TESTS_CONTAINER_APP_RESOURCE_ID=/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/00000/providers/Microsoft.App/containerApps/00000
AZURE_AI_PROJECTS_TESTS_CONTAINER_INGRESS_SUBDOMAIN_SUFFIX=00000

# Discovered connections
"""
    
    if connections["bing"]:
        env_content += f"AZURE_AI_PROJECTS_TESTS_BING_CONNECTION_ID={connections['bing']}\n"
    else:
        env_content += "AZURE_AI_PROJECTS_TESTS_BING_CONNECTION_ID=# NOT FOUND - UPDATE MANUALLY\n"
    
    if connections["ai_search"]:
        env_content += f"AZURE_AI_PROJECTS_TESTS_AI_SEARCH_CONNECTION_ID={connections['ai_search']}\n"
    else:
        env_content += "AZURE_AI_PROJECTS_TESTS_AI_SEARCH_CONNECTION_ID=# NOT FOUND - UPDATE MANUALLY\n"
    
    if connections["github_pat"]:
        env_content += f"AZURE_AI_PROJECTS_TESTS_MCP_PROJECT_CONNECTION_ID={connections['github_pat']}\n"
    else:
        env_content += "AZURE_AI_PROJECTS_TESTS_MCP_PROJECT_CONNECTION_ID=# NOT FOUND - UPDATE MANUALLY\n"
    
    # Add manual fields section
    env_content += "\n# TODO: Manual configuration required\n"
    
    if connections["ai_search"]:
        env_content += "AZURE_AI_PROJECTS_TESTS_AI_SEARCH_INDEX_NAME=\n"
    
    # Write file
    output_file = f".env.generated.{output_name}"
    try:
        with open(output_file, 'w') as f:
            f.write(env_content)
        print(f"\n✅ Generated: {output_file}")
        print("\n📋 Summary:")
        print(f"   - Model: {model_deployment}")
        print(f"   - Bing: {'✅ Found' if connections['bing'] else '❌ Not found'}")
        print(f"   - AI Search: {'✅ Found' if connections['ai_search'] else '❌ Not found'}")
        print(f"   - GitHub PAT: {'✅ Found' if connections['github_pat'] else '❌ Not found'}")
        print(f"   - Total connections: {len(connections['all'])}")
        print(f"\n✨ Review the generated file and update any missing values!")
        
    except Exception as e:
        print(f"❌ Failed to write file: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate .env file from Azure AI Project endpoint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_env_file.py https://my-project.services.ai.azure.com/api/projects/my-project
  python generate_env_file.py https://my-project.services.ai.azure.com/api/projects/my-project e2etests
        """
    )
    
    parser.add_argument(
        'project_endpoint',
        help='Azure AI Project endpoint URL'
    )
    
    parser.add_argument(
        'output_name',
        nargs='?',
        default='default',
        help='Output file suffix (creates .env.generated.<name>)'
    )
    
    args = parser.parse_args()
    
    generate_env_file(args.project_endpoint, args.output_name)


if __name__ == "__main__":
    main()
