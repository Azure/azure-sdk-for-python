def get_default_arm_template():
    return {
        "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {
            "onlineEndpointProperties": {
                "defaultValue": {
                    "authMode": "Key",
                    "publicNetworkAccess": "Enabled",
                    "properties": {"enforce_access_to_default_secret_stores": "enabled"},
                },
                "type": "Object",
            },
            "onlineEndpointPropertiesTrafficUpdate": {
                "defaultValue": {
                    "traffic": {"[parameters('onlineDeploymentName')]": 100},
                    "authMode": "Key",
                    "publicNetworkAccess": "Enabled",
                    "properties": {"enforce_access_to_default_secret_stores": "enabled"},
                },
                "type": "Object",
            },
        },
        "resources": [
            {
                "type": "Microsoft.MachineLearningServices/workspaces/onlineEndpoints",
                "apiVersion": "2023-04-01-Preview",
                "name": "[concat(parameters('workspaceName'), '/', parameters('onlineEndpointName'))]",
                "location": "[parameters('location')]",
                "identity": {"type": "SystemAssigned"},
                "properties": "[parameters('onlineEndpointProperties')]",
                "copy": {"name": "onlineEndpointCopy", "count": 1, "mode": "serial"},
            },
            {
                "type": "Microsoft.MachineLearningServices/workspaces/onlineEndpoints/deployments",
                "apiVersion": "2023-04-01-Preview",
                "name": "[concat(parameters('workspaceName'), '/', parameters('onlineEndpointName'), '/', parameters('onlineDeploymentName'))]",
                "location": "[parameters('location')]",
                "dependsOn": [
                    "onlineEndpointCopy",
                ],
                "sku": {"capacity": "[parameters('deploymentInstanceCount')]", "name": "default"},
                "identity": {"type": "None"},
                "properties": "[parameters('onlineDeploymentProperties')]",
                "copy": {"name": "onlineDeploymentCopy", "count": 1, "mode": "serial"},
            },
            {
                "type": "Microsoft.Resources/deployments",
                "apiVersion": "2015-01-01",
                "name": "[concat('updateEndpointWithTraffic', '-', parameters('onlineEndpointName'))]",
                "dependsOn": ["onlineDeploymentCopy"],
                "properties": {
                    "mode": "Incremental",
                    "template": {
                        "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
                        "contentVersion": "1.0.0.0",
                        "resources": [
                            {
                                "type": "Microsoft.MachineLearningServices/workspaces/onlineEndpoints",
                                "apiVersion": "2023-04-01-Preview",
                                "location": "[parameters('location')]",
                                "name": "[concat(parameters('workspaceName'), '/', parameters('onlineEndpointName'))]",
                                "properties": "[parameters('onlineEndpointPropertiesTrafficUpdate')]",
                                "identity": {"type": "SystemAssigned"},
                            }
                        ],
                    },
                },
            },
        ],
        "outputs": {
            "online_endpoint_name": {
                "type": "string",
                "value": "[parameters('onlineEndpointName')]",
            },
            "online_deployment_name": {
                "type": "string",
                "value": "[parameters('onlineDeploymentName')]",
            },
        },
    }
