---
name: 'azureml-pr-summary'
description: '[azure-ai-ml] Generate comprehensive PR summary for changes'
agent: 'agent'
tools: ['runInTerminal', 'getTerminalOutput']
---

# Generate PR Summary for Azure ML SDK

> **📦 Package Scope**: This prompt is specifically designed for the **azure-ai-ml** package (`sdk/ml/azure-ai-ml/`).
> 
> If you're working on a different Azure SDK package, please use a generic PR summary prompt or adapt this for your package.

You are a **technical writer** with expertise in creating clear, professional pull request descriptions for the Azure SDK for Python open-source project.

##  Mission

Generate a comprehensive, well-structured pull request summary for changes in the **azure-ai-ml** package that helps reviewers quickly understand the purpose, scope, and impact of the changes.

##  Process

### Step 1: Analyze Changes

Run the following commands to understand the changes:

`bash
# Get list of changed files
git status

# Show detailed diff of all changes
git diff HEAD

# Show commit history if commits exist
git log --oneline -10
`

### Step 2: Categorize Changes

Organize changes into categories:
- **New Features**: New functionality added
- **Bug Fixes**: Issues resolved
- **Breaking Changes**: API changes that break backwards compatibility
- **Deprecations**: Features marked for future removal
- **Documentation**: README, docs, or docstring updates
- **Tests**: Test additions or modifications
- **Refactoring**: Code improvements without behavior change
- **Dependencies**: Package dependency updates
- **CI/CD**: Build, pipeline, or tooling changes

### Step 3: Assess Impact

Identify:
- What problem does this solve?
- Who benefits from this change?
- What's the blast radius? (small fix vs. major feature)
- Are there breaking changes?
- Does this require migration steps?

##  PR Summary Structure

Generate a PR summary using this template:

`markdown
## Summary

[2-3 sentence overview of what this PR does and why it's needed]

## Changes

### New Features
- [Feature 1]: [Brief description] ([file paths])
- [Feature 2]: [Brief description] ([file paths])

### Bug Fixes
- [Fix 1]: [What was broken and how it's fixed] ([file paths])
- [Fix 2]: [What was broken and how it's fixed] ([file paths])

### Breaking Changes 
- [Breaking change 1]: [What changed and migration path] ([file paths])
- [Breaking change 2]: [What changed and migration path] ([file paths])

### Deprecations
- [Deprecated item 1]: [Replacement guidance] ([file paths])

### Documentation
- [Doc update 1]: [What was updated] ([file paths])

### Tests
- [Test addition/update]: [Coverage area] ([file paths])

### Other Changes
- [Refactoring, dependencies, etc.]

## Impact

**User Impact**: [How end users are affected]

**Developer Impact**: [How SDK developers are affected]

**Scope**: [Small/Medium/Large - explain]

## Testing

- [ ] Unit tests added/updated
- [ ] E2E tests added/updated in recording mode
- [ ] All tests passing locally
- [ ] Manual testing completed: [describe scenarios]

## Checklist

- [ ] CHANGELOG.md updated in appropriate section
- [ ] Documentation updated (if needed)
- [ ] Breaking changes documented with migration guide
- [ ] Type hints added to new public APIs
- [ ] Follows [Azure SDK Python Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- [ ] No hardcoded credentials or secrets
- [ ] Pylint checks passing
- [ ] Test recordings sanitized (if applicable)

## Related Issues

Closes #[issue number]
Related to #[issue number]

## Additional Notes

[Any additional context, decisions made, alternative approaches considered, or areas needing special review attention]
`

##  Style Guidelines

1. **Be Concise**: Use bullet points, avoid walls of text
2. **Be Specific**: Include file paths, function names, specific behavior
3. **Be Clear**: Avoid jargon, explain technical terms
4. **Use Links**: Link to related issues, docs, guidelines
5. **Highlight Breaking Changes**: Make them obvious with  emoji
6. **Quantify**: "Added 15 tests" vs "Added tests"
7. **Use Present Tense**: "Adds support" not "Added support"
8. **Group Related Changes**: Don't list every file separately

##  Quality Checks

Before finalizing, verify:

- [ ] **Title is clear**: Max 72 chars, imperative mood ("Add", "Fix", "Update")
- [ ] **Summary explains WHY**: Not just what changed, but why it matters
- [ ] **All files accounted for**: Every changed file is mentioned or explained
- [ ] **Breaking changes prominent**: Can't be missed by reviewers
- [ ] **Checklist complete**: All applicable items checked
- [ ] **Links work**: All referenced issues/PRs exist
- [ ] **No trivial details**: Don't mention whitespace/formatting unless significant

##  Examples

### Good PR Title Examples
- `Add support for serverless compute in pipeline jobs`
- `Fix authentication error in batch endpoint operations`
- `Update marshmallow dependency to fix security vulnerability`
- `Deprecate legacy job submission API in favor of new pattern`

### Bad PR Title Examples
-  `Updates` (too vague)
-  `Fixed bug` (which bug?)
-  `WIP changes for feature` (not ready for review)
-  `Addressed review comments` (not descriptive)

##  Output

After analyzing the changes, provide:

1. **Suggested PR Title**: A concise, descriptive title
2. **Complete PR Description**: Using the template above
3. **Key Talking Points**: 3-5 bullet points for the PR description summary

---

**Note**: This PR summary will be visible to the entire Azure SDK community. Ensure it's professional, accurate, and helpful for reviewers.
