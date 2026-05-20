# Validation Tools for Package Skills

## vally lint (Structural Validation)

**Source**: `microsoft/evaluate` (currently private, will be public)

```bash
# Install (once published)
npm install -g @microsoft/vally-cli

# Lint a skill
vally lint sdk/<service>/<package-name>/.github/skills/<package-name>

# Lint all skills in repo
vally lint .github/skills
```

### What it checks

| Check | What it does | Common failure |
|---|---|---|
| `spec-compliance` | Validates frontmatter (name, description), name-directory match | Directory name doesn't match `name` field (name must equal the distribution package name, e.g. `azure-ai-projects`) |
| `valid-refs` | All markdown links resolve to existing files | Broken link to reference file |
| `orphan-files` | No unreferenced files in references/ | File in references/ not linked from SKILL.md |
