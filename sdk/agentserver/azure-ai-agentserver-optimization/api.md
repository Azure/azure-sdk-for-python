```py
namespace azure.ai.agentserver.optimization

    def azure.ai.agentserver.optimization.load_config(
            *, 
            config_dir: str | Path | None = ..., 
            credential: TokenCredential | None = ...
        ) -> OptimizationConfig | None: ...


    def azure.ai.agentserver.optimization.load_skills_from_dir(skills_dir: Path) -> list[Skill]: ...


    class azure.ai.agentserver.optimization.CandidateConfig:

        def __init__(
                self, 
                *, 
                instructions: str | None = ..., 
                model: str | None = ..., 
                name: str | None = ..., 
                skills: list[Skill] | None = ..., 
                temperature: float | None = ..., 
                tool_definitions: list[dict] | None = ...
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, data: dict[str, Any]) -> CandidateConfig: ...


    class azure.ai.agentserver.optimization.OptimizationConfig:
        property has_skills: bool    # Read-only
        BASELINE_DIR: ClassVar[str] = baseline
        DEFAULT_LOCAL_DIR: ClassVar[str] = .agent_configs
        ENV_CANDIDATE_ID: ClassVar[str] = OPTIMIZATION_CANDIDATE_ID
        ENV_CONFIG: ClassVar[str] = OPTIMIZATION_CONFIG
        ENV_LOCAL_DIR: ClassVar[str] = OPTIMIZATION_LOCAL_DIR
        ENV_RESOLVE_ENDPOINT: ClassVar[str] = OPTIMIZATION_RESOLVE_ENDPOINT
        INSTRUCTIONS_FILE: ClassVar[str] = instructions.md
        METADATA_FILE: ClassVar[str] = metadata.yaml
        SKILLS_DIR: ClassVar[str] = skills
        SKILL_FILE: ClassVar[str] = SKILL.md
        TOOLS_FILE: ClassVar[str] = tools.json

        def __init__(
                self, 
                *, 
                candidate_id: str | None = ..., 
                instructions: str | None = ..., 
                model: str | None = ..., 
                skills: list[Skill] | None = ..., 
                skills_dir: str | None = ..., 
                source: str = "defaults", 
                temperature: float | None = ..., 
                tool_definitions: list[dict] | None = ...
            ) -> None: ...

        def __repr__(self) -> str: ...

        def apply_tool_descriptions(self, tools: list) -> list: ...

        def compose_instructions(self) -> str: ...


    class azure.ai.agentserver.optimization.Skill:

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                name: str, 
                description: str, 
                body: str = ""
            ) -> None: ...

        def __repr__(self) -> str: ...


```