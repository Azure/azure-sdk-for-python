```py
namespace azure.ai.agentserver.githubcopilot

    class azure.ai.agentserver.githubcopilot.CopilotAdapter:

        def __init__(
                self, 
                session_config: Optional[dict] = None, 
                acl: Optional[ToolAcl] = None, 
                credential: Optional[Any] = None
            ): ...

        def run(self, port: int = None): ...

        async def run_async(self, port: int = None): ...


    class azure.ai.agentserver.githubcopilot.GitHubCopilotAdapter(CopilotAdapter):

        def __init__(
                self, 
                skill_directories: Optional[list[str]] = None, 
                tools: Optional[list] = None, 
                project_root: Optional[str] = None, 
                toolbox_endpoint: Optional[str] = None, 
                **kwargs
            ): ...

        @classmethod
        def from_project(
                cls, 
                project_path: str = ".", 
                **kwargs
            ) -> GitHubCopilotAdapter: ...

        def clear_default_model(self) -> None: ...

        async def connect_toolboxes(self): ...

        def get_model(self) -> Optional[str]: ...

        async def initialize(self): ...

        def run(self, port: int = None): ...

        async def run_async(self, port: int = None): ...


    class azure.ai.agentserver.githubcopilot.ToolAcl:

        def __init__(
                self, 
                rules: List[_Rule], 
                default_action: _Action = "deny", 
                source: str = "<inline>"
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_env(cls, env_var: str = "TOOL_ACL_PATH") -> Optional[ToolAcl]: ...

        @classmethod
        def from_file(cls, path: str | PathLike) -> ToolAcl: ...

        def evaluate(self, req: Dict[str, Any]) -> _Action: ...

        def is_allowed(self, req: Dict[str, Any]) -> bool: ...


```