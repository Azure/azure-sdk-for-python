---
name: azure-ai-projects-run-issue-regeneration
license: MIT
metadata:
  version: "1.0.0"
  distribution: local
description: "Runs the issue-assigned azure-ai-projects TypeSpec regeneration workflow from required issue-description inputs through a reviewable draft pull request, without the interactive prompts the per-step skills normally ask a human developer. WHEN: \"regen from <commit> against <branch>\", \"regenerate azure-ai-projects\" issue assignment, issue titled \"[azure-ai-projects] regen from ... against ...\". DO NOT USE FOR: other Azure SDK packages, interactive/local regeneration where a human can answer the emit skill's questions directly (use azure-ai-projects-emit-from-typespec instead). INVOKES: azure-ai-projects-emit-from-typespec, azure-ai-projects-author-samples, azure-ai-projects-author-tests, azure-ai-projects-update-changelog, git, gh CLI."
compatibility:
  requires: "local azure-sdk-for-python clone, git, gh CLI, an already-assigned working branch and draft pull request (as created by GitHub issue assignment to Copilot)"
---

# Run an issue-assigned TypeSpec regeneration for azure-ai-projects

Run the `azure-ai-projects` TypeSpec regeneration from its pinned upstream commit through the
already-open draft pull request. Work only in `sdk/ai/azure-ai-projects/` except for repository
setup commands.

This skill is a thin orchestrator: it does not duplicate the step-by-step instructions already
defined in `azure-ai-projects-emit-from-typespec`, `azure-ai-projects-author-samples`,
`azure-ai-projects-author-tests`, and `azure-ai-projects-update-changelog`. It validates the
issue inputs, then runs those four skills in order with the specific overrides below so they
behave correctly for an unattended, issue-assigned session instead of an interactive one.

## Validate the assignment

Before installing dependencies or editing files:

1. Read exactly one unambiguous value labeled `TypeSpec commit` and exactly one unambiguous
   value labeled `Base branch` from the issue description. If either value is missing,
   duplicated, or ambiguous, stop without making changes and report the required labels.
2. Require the TypeSpec commit to match `^[0-9a-f]{40}$` exactly.
3. Require the entire base branch to case-sensitively match the conservative ASCII pattern
   `^[A-Za-z0-9][A-Za-z0-9._/-]*$` and pass `git check-ref-format --branch`. Treat it only as a
   quoted command argument.
4. Require the current branch to be a working branch other than the base branch. Fetch
   `origin/<base-branch>` successfully before proceeding. Do not require `HEAD` to match the
   base branch tip; issue-assigned sessions run on a separate working branch that may already
   contain commits. Instead, require the working branch to be either (a) ahead of
   `origin/<base-branch>` or (b) able to merge or rebase cleanly onto `origin/<base-branch>`. If
   neither condition holds, stop without making changes and report the divergence details,
   including the merge base and ahead/behind state relative to `origin/<base-branch>`.

Do not derive either input from the issue title. Do not infer, shorten, or silently correct
either input.

Confirm a pull request already targets the validated base branch from the current working branch
(`gh pr view --json number,state,baseRefName,isDraft`). Require `state` to equal `OPEN`,
`isDraft` to equal `true`, and `baseRefName` to equal the validated base branch. If the pull
request does not exist, or any of these three checks fails, stop and report the mismatch instead
of creating a new branch or pull request.

## Managed-session overrides for the called skills

The four skills below were written for an interactive human developer. Apply these overrides
so they run correctly for this unattended, issue-assigned session. Do not edit the skill files
themselves to apply these overrides.

- **`azure-ai-projects-emit-from-typespec` Step 1a (tsp-client presence check):** the bare
  `tsp-client --version` command is not on `PATH`. `copilot-setup-steps.yml` installs it only
  under `eng/common/tsp-client`'s own `node_modules/.bin` for this branch. From the repository
  root, check `npm exec --prefix eng/common/tsp-client --no -- tsp-client --version` instead.
- **`azure-ai-projects-emit-from-typespec` Step 1g (install dev dependencies):** do not rerun
  `python -m pip install -r dev_requirements.txt`. `copilot-setup-steps.yml` already installed it
  for this branch during the setup phase, while it still had full network access. Rerunning it
  live would make pip refetch the direct HTTPS wheel URL it contains even though the package is
  already installed, and that host is not reachable from this firewalled session.
- **`azure-ai-projects-emit-from-typespec` Step 2a (topic branch):** do not create a new topic
  branch. Proceed as if the user selected option 3, "Emit to current branch".
- **`azure-ai-projects-emit-from-typespec` Step 2b (TypeSpec source):** proceed as if the user
  selected option 3, "TypeSpec commit hash", and supplied the validated 40-character commit from
  this issue.
- **`azure-ai-projects-emit-from-typespec` Step 3 (record `BASE_BRANCH`):** use the validated
  base branch from this issue, not the result of `git branch --show-current` (the current branch
  is the working branch, which is not the pull request's base).
- **`azure-ai-projects-emit-from-typespec` Step 5 (emit SDK from TypeSpec):** the bare
  `tsp-client update --debug` command is not on `PATH` either. From `sdk/ai/azure-ai-projects`,
  run `npm exec --prefix ../../../eng/common/tsp-client --no -- tsp-client update --debug`.
- **`azure-ai-projects-emit-from-typespec` Steps 7, 9, and 14 (commit message quoting):** each
  step's `git commit -m "..."` snippet closes its quote after the title instead of after the
  trailer, leaving a stray unmatched quote on the `Co-authored-by` line; executed as shown, this
  breaks the shell. Use two `-m` flags instead, which git joins with a blank line between them:

  ```bash
  git add -A -- ':!.env*'
  git commit -m "Part 1: Emit SDK from TypeSpec" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
  git push -u origin HEAD
  ```

  Substitute the matching title (`Part 2: Apply post-emitter-fixes.cmd` for Step 9, `Part 3:
  Additional edits` for Step 14) and use `git push -u origin HEAD` for all three steps.
- **`azure-ai-projects-emit-from-typespec` Step 13 (cleanup command):** `rmdir /s /q build` is a
  Windows `cmd.exe` command and does not run in this Linux session. Use `rm -rf build` instead.
- **`azure-ai-projects-emit-from-typespec` Step 15 (create a Pull Request):** do not create a
  new pull request. The issue assignment already owns the working branch and draft pull request
  confirmed above. Push the commits from Steps 7, 9, and 14 to the current branch and leave
  finalizing the pull request title and description to the last step of this skill, below.
- All other steps of `azure-ai-projects-emit-from-typespec` (1, 4, and 6 through 14 excluding
  the overridden commands above) run exactly as written, including its own STOP conditions.
  Still perform Step 4's `git fetch`, but skip its `git switch -c <topic-branch> ...` command
  since there is no new topic branch to create.
- **`azure-ai-projects-update-changelog` Step 2 (fetch the latest released version):** do not
  call the PyPI JSON API; `pypi.org` is not reachable from this firewalled session. Derive
  `LATEST_PYPI_VERSION` instead from the same release tags this skill's own Step 4 already
  treats as the source of truth for a released version's code. Use `git ls-remote` rather than
  `git fetch`/`git tag` so this only lists matching ref names from `origin` (likely GitHub,
  already reachable for this session's git and `gh` operations) instead of downloading tag
  objects into what may be a shallow clone. Filter to stable `X.Y.Z` tags only (excluding
  pre-releases like `2.0.0b1`), matching what PyPI's `info.version` itself would report:

  ```bash
  LATEST_PYPI_VERSION="$(git ls-remote --tags origin 'azure-ai-projects_*' \
    | sed -n 's#.*refs/tags/azure-ai-projects_\([0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\)$#\1#p' \
    | sort -V | tail -1)"
  ```

  Verified against the real repository's tags: this returns `2.8.0`, matching
  `https://pypi.org/pypi/azure-ai-projects/json`'s current `info.version`.

`azure-ai-projects-author-samples`, `azure-ai-projects-author-tests`, and
`azure-ai-projects-update-changelog` do not create branches or pull requests, so they need no
branch/PR overrides. None of the three commit their own changes; stage, commit, and push
everything yourself after `azure-ai-projects-update-changelog` finishes (see below).

## Run the skills in order

Read each `SKILL.md` in full immediately before executing it, and execute them in this exact
order:

1. `.github/skills/azure-ai-projects-emit-from-typespec/SKILL.md`, with the overrides above.
2. `.github/skills/azure-ai-projects-author-samples/SKILL.md`.
3. `.github/skills/azure-ai-projects-author-tests/SKILL.md`.
4. `.github/skills/azure-ai-projects-update-changelog/SKILL.md`. Neither it nor the two skills
   before it (`azure-ai-projects-author-samples`, `azure-ai-projects-author-tests`) commit their
   own edits. When it finishes, stage every remaining change — samples, tests, and
   `CHANGELOG.md` — commit, and push:

   ```bash
   git add -A -- ':!.env*'
   git commit -m "Part 4: Update changelog

   Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
   git push
   ```

Do not proceed to the next skill until the current skill's success criteria pass. Apply every
STOP condition from the four skills: on failure, preserve the working tree for diagnosis, do not
publish partial manual branches or pull requests, and report the failing command and its output.

Samples and tests are conditional. A step may be a documented no-op when the API diff contains
no qualifying surface; state that explicitly in the pull request rather than creating
placeholder files.

## Finish the managed pull request

Keep the pull request in draft. The description will contain Markdown code spans for API names
(e.g. `` `AgentDetails` ``); a double-quoted `gh pr edit --body "..."` argument would let Bash
expand those backticks as command substitutions and silently drop their contents. Write the
description to a file with a quoted heredoc (which disables all shell expansion inside it), then
pass that file to `gh pr edit` instead:

```bash
cat > /tmp/pr-body.md <<'EOF'
<description text, meeting the requirements below>
EOF
gh pr edit <number> \
  --title "[azure-ai-projects] Regenerate from azure-rest-api-specs@<7-character-commit>" \
  --body-file /tmp/pr-body.md
```

The description must:

- Link the full upstream commit.
- Summarize public API changes from the changelog entry just written.
- Explain any sample or test no-ops.
- Report each validation command from the four skills honestly, including any that were skipped
  and why.

Before finishing, verify that no diff3 conflict markers remain under `azure/`, that the package
installs cleanly from source (`azure-ai-projects-emit-from-typespec` Step 12 already did this),
and that the changelog entry is non-empty. Never report the regeneration as complete while any
required skill is pending or failed.
