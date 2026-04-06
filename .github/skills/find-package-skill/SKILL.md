---
name: find-package-skill
description: '**UTILITY SKILL** — Must be consulted before making any changes to packages under sdk/. Provides package-specific domain knowledge that prevents common mistakes. WHEN: "add feature to package", "fix bug in package", "modify package code", "regenerate from typespec", "change client library".'
---

# Find Package Skill

Before modifying any SDK package in this monorepo, check this registry to see
if a package-specific skill exists. Package skills contain tribal knowledge
(architecture, data flows, type mappings, pitfalls) that prevents common mistakes.

Always check this registry before modifying any SDK package — even if you think
you already know the package well.

## How to Use

1. Find the package you're modifying in the table below.
2. Read the SKILL.md at the listed path using the Read tool. Then read all files under the `references/` directory next to it for additional context.
3. If the package isn't listed, no package-specific skill exists yet — proceed normally.

## Package Skills

| Package                   | Path                                                                        |
| ------------------------- | --------------------------------------------------------------------------- |
| `azure-search-documents` | `sdk/search/azure-search-documents/.github/skills/azure-search-documents/SKILL.md` |