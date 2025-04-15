# @azure-tools/typespec-azure-rulesets

TypeSpec ruleset for Azure specs

## Install

```bash
npm install @azure-tools/typespec-azure-rulesets
```

## Usage

Add the following in `tspconfig.yaml`:

```yaml
linter:
  extends:
    - "@azure-tools/typespec-azure-rulesets/data-plane"
```

## RuleSets

Available ruleSets:

- `@azure-tools/typespec-azure-rulesets/data-plane`
- `@azure-tools/typespec-azure-rulesets/resource-manager`

## Rules

| Name | Description |
| ---- | ----------- |
