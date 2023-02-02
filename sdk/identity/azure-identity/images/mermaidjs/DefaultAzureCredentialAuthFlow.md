```mermaid
%% STEPS TO GENERATE IMAGE
%% =======================
%% 1. Install mermaid CLI (see https://github.com/mermaid-js/mermaid-cli/blob/master/README.md)
%%    v8.14.0 is known good for our process. npm install -g @mermaid-js/mermaid-cli@8.14.0
%% 2. Run command: mmdc -i DefaultAzureCredentialAuthFlow.md -o DefaultAzureCredentialAuthFlow.svg

flowchart LR;
    A(Environment):::deployed ==> B(Workload Identity):::deployed ==> C(Managed Identity):::deployed ==> D(Azure Developer CLI):::developer ==> E(Azure CLI):::developer ==> F(Azure PowerShell):::developer ==> G(Interactive browser):::interactive;

    subgraph CREDENTIAL TYPES;
        direction LR;
        Deployed(Deployed service):::deployed ==> Developer(Developer):::developer ==> Interactive(Interactive developer):::interactive;

        %% Hide links between boxes in the legend by setting width to 0. The integers after "linkStyle" represent link indices.
        linkStyle 6 stroke-width:0px;
        linkStyle 7 stroke-width:0px;
    end;

    %% Define styles for credential type boxes
    classDef deployed fill:#95C37E, stroke:#71AD4C;
    classDef developer fill:#F5AF6F, stroke:#EB7C39;
    classDef interactive fill:#A5A5A5, stroke:#828282;

    %% Add API ref links to credential type boxes
    click A "https://learn.microsoft.com/python/api/azure-identity/azure.identity.environmentcredential?view=azure-python" _blank;
    click C "https://learn.microsoft.com/python/api/azure-identity/azure.identity.managedidentitycredential?view=azure-python" _blank;
    click E "https://learn.microsoft.com/python/api/azure-identity/azure.identity.azureclicredential?view=azure-python" _blank;
    click F "https://learn.microsoft.com/python/api/azure-identity/azure.identity.azurepowershellcredential?view=azure-python" _blank;
    click G "https://learn.microsoft.com/python/api/azure-identity/azure.identity.interactivebrowsercredential?view=azure-python" _blank;
```
