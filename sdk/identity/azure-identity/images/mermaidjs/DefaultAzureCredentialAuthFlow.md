```mermaid
%% STEPS TO GENERATE IMAGE
%% =======================
%% 1. Install mermaid CLI (see https://github.com/mermaid-js/mermaid-cli/blob/master/README.md)
%% 2. Run command: mmdc -i DefaultAzureCredentialAuthFlow.md -o DefaultAzureCredentialAuthFlow.svg

flowchart LR;
    A(Environment):::deployed ==> B(Managed Identity):::deployed ==> C(VS Code):::developer ==> D(Azure CLI):::developer ==> E(Azure PowerShell):::developer ==> F(Interactive browser):::interactive;

    subgraph CREDENTIAL TYPES;
        direction LR;
        Deployed(Deployed service):::deployed ==> Developer(Developer):::developer ==> Interactive(Interactive developer):::interactive;

        %% Hide links between boxes in the legend by setting width to 0. The integers after "linkStyle" represent link indices.
        linkStyle 5 stroke-width:0px;
        linkStyle 6 stroke-width:0px;
    end;

    %% Define styles for credential type boxes
    classDef deployed fill:#71AD4C, stroke:#71AD4C;
    classDef developer fill:#EB7C39, stroke:#EB7C39;
    classDef interactive fill:#A6A6A6, stroke:#A6A6A6;

    %% Add API ref links to credential type boxes
    click A "https://docs.microsoft.com/python/api/azure-identity/azure.identity.environmentcredential?view=azure-python" _blank;
    click B "https://docs.microsoft.com/python/api/azure-identity/azure.identity.managedidentitycredential?view=azure-python" _blank;
    click C "https://docs.microsoft.com/python/api/azure-identity/azure.identity.visualstudiocodecredential?view=azure-python" _blank;
    click D "https://docs.microsoft.com/python/api/azure-identity/azure.identity.azureclicredential?view=azure-python" _blank;
    click E "https://docs.microsoft.com/python/api/azure-identity/azure.identity.azurepowershellcredential?view=azure-python" _blank;
    click F "https://docs.microsoft.com/python/api/azure-identity/azure.identity.interactivebrowsercredential?view=azure-python" _blank;
```
