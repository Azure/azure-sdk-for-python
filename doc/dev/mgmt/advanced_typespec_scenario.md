## Azure Python SDK TypeSpec Migration – Advanced Scenarios

This document describes several advanced customization scenarios encountered during migration from Swagger to TypeSpec.

### 1. Renaming Parameters Nested in Anonymous Models

**Scenario**

The scenario involves renaming an input parameter in the generated Python SDK using `@@clientName` when the parameter is defined in an anonymous model used as the parameter type of an operation. TypeSpec currently does not allow direct references to such parameters because the anonymous model is not directly exposed.

In the original attempt, the operation was defined as:

```tsp
interface Agents {
  @post
  @route("/agents/{agent_name}")
  @tag("Agents")
  updateAgent is AgentOperation<
    {
      @path
      @clientName("name", "python")
      agent_name: string;

      ...UpdateAgentRequest;
    },
    AgentObject
  >;
}
```

and in `client.tsp`:

```tsp
@@clientName(Agents.updateAgent::parameters.agent_name, "name", "python");
```

When compiling, TypeSpec reports the following error:

```text
Model doesn't have member agent_name
```

This shows that the parameter defined in the anonymous model used as a template argument to `AgentOperation` is not directly addressable via `@@clientName`.

**Resolution**

To make the parameter accessible for renaming, the anonymous model is first factored out into a named alias. The pattern can be illustrated with the following simplified TypeSpec definitions:

```tsp
alias UpdateAgentParams = {
	@path agent_name: string;
};

interface MyOp {
  @post
  @route("/agents/{agent_name}")
  @tag("Agents")
  updateAgent1 is AgentOperation<
    {
      UpdateAgentParams: UpdateAgentParams;

      ...UpdateAgentRequest;
    },
    AgentObject
  >;
}
```

and in `client.tsp`:

```tsp
@@clientName(UpdateAgentParams.agent_name, "name")
```
