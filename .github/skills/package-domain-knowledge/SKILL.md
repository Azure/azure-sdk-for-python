---
name: package-domain-knowledge
description: 'MANDATORY — Before modifying any package under sdk/, read this registry to load the package-specific skill. Contains architecture, data flows, type mappings, and pitfalls that prevent common mistakes. ALWAYS read this skill when your task involves modifying SDK package code, adding features, fixing bugs, regenerating from autorest/typespec, or changing client libraries.'
---

# Package Domain Knowledge Registry

> **⚠️ MANDATORY: You MUST read this file before modifying any SDK package.**
> If you skip this step, you risk introducing bugs that are already documented
> in the package-specific skill.

## Automatic Loading

If you are modifying a package listed below, you **MUST**:

1. Read the `SKILL.md` at the listed path.
2. Read **all files** in the `references/` directory next to it.
3. Apply the knowledge from those files to your work.

Failure to do so risks introducing bugs, incorrect type mappings, or
architectural violations that the package skill specifically documents.

## How to Use

1. Find the package you're modifying in the table below.
2. Read the SKILL.md at the listed path using the Read tool. Then read all files under the `references/` directory next to it for additional context.
3. If the package isn't listed, no package-specific skill exists yet — proceed normally.

## Package Skills

| Package             | Path                                                                       |
| ------------------- | -------------------------------------------------------------------------- |
| `azure-data-tables` | `sdk/tables/azure-data-tables/.github/skills/azure-data-tables/SKILL.md`   |
