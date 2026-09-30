# Using the Azure SDK for Python with AI tools

AI-powered coding tools can help you write, understand, and debug applications that use the Azure SDK.
This page lists common options and integrations available today.

This page can be linked by [aka.ms/azsdk/python/ai](https://aka.ms/azsdk/python/ai)

## AI coding tools

Several tools support AI-assisted development with the Azure SDK:

| Tool | Description |
|---|---|
| [VS Code](https://code.visualstudio.com/) | Code editor with built-in AI features and Copilot integration |
| [GitHub Copilot](https://github.com/features/copilot) | AI code completion and chat inside VS Code, Visual Studio, JetBrains IDEs, and GitHub.com |
| [Copilot CLI](https://docs.github.com/en/copilot/github-copilot-in-the-cli/about-github-copilot-in-the-cli) | AI assistance for shell commands and Azure CLI usage |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | Terminal-based AI coding agent from Anthropic |
| [Cursor](https://www.cursor.com/) | AI-first code editor with chat and inline editing |
| [Aider](https://aider.chat/) | Terminal-based AI pair programming tool |

This is not an exhaustive list — most AI coding tools that support chat or code generation can work with the Azure SDK.

## Azure MCP Server

The [Azure MCP Server](https://learn.microsoft.com/azure/developer/azure-mcp-server/get-started) exposes Azure resource operations to AI tools through the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/).
This lets an AI coding agent query, create, and manage Azure resources directly during a conversation.

See the [getting started guide](https://learn.microsoft.com/azure/developer/azure-mcp-server/get-started) for setup instructions.

## Azure SDK skills

The Microsoft skills marketplace provides Azure SDK skills that give AI agents context about Azure SDK conventions, code generation, and package management. These skills work with CLI-based AI tools that support plugins, such as Claude Code and Copilot CLI.

Install the Microsoft skills marketplace:

```
/plugin marketplace add Microsoft/skills
```

Install the Azure SDK skills plugin:

```
/plugin install azure-sdk-python@skills
```

Verify installation:

```
/plugin list
```

Update the plugin:

```
/plugin update azure-sdk-python@skills
```

Skills provide domain-specific context that helps AI tools generate more accurate SDK code.

For operational Azure tasks (managing resources, querying services), see the [Azure skills](https://github.com/microsoft/azure-skills) repository.

## Further reading

- [Azure SDK for Python documentation](https://learn.microsoft.com/azure/developer/python/sdk/azure-sdk-overview)
- [Azure SDK design guidelines](https://azure.github.io/azure-sdk/python_design.html)
- [Azure MCP Server](https://learn.microsoft.com/azure/developer/azure-mcp-server/get-started)

## Feedback

If you have feedback on your AI experience with the Azure SDK for Python, [open an issue](https://github.com/Azure/azure-sdk-for-python/issues/new/choose) on the repository.
