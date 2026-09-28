// cspell:ignore ffeb
const BLOCKING_LABELS = new Set([
  "needs-triage",
  "needs-team-triage",
  "issue-addressed",
  "needs-author-feedback",
]);

function positiveInteger(value, name) {
  const text = String(value).trim();
  if (!/^\+?\d+$/.test(text) || !Number.isSafeInteger(Number(text)) || Number(text) <= 0) {
    throw new Error(`${name} must be a positive integer`);
  }
  return Number(text);
}

function ineligibleReason(issue, issueNumber) {
  if (issue.number !== issueNumber || Object.hasOwn(issue, "pull_request")) {
    return "the target is not the triggering issue";
  }
  if (issue.state !== "open" || issue.locked !== false) {
    return "the issue is closed or locked";
  }
  if (!Array.isArray(issue.labels) || issue.labels.some(label =>
    !label || typeof label.name !== "string" || typeof label.color !== "string"
  )) {
    throw new Error("Issue labels are missing names or colors");
  }
  const names = new Set(issue.labels.map(label => label.name.toLowerCase()));
  if (!names.has("customer-reported")) {
    return "the issue is not customer-reported";
  }
  for (const name of BLOCKING_LABELS) {
    if (names.has(name)) {
      return `the issue has ${name}`;
    }
  }
  const colors = issue.labels.map(label => label.color.replace(/^#/, "").toUpperCase());
  if (colors.filter(color => color === "E99695").length !== 1) {
    return "the issue does not have exactly one service label";
  }
  if (colors.filter(color => color === "FFEB77").length !== 1) {
    return "the issue does not have exactly one category label";
  }
  return null;
}

async function prepareHandoff({ github, context, issueNumber, commentId }) {
  const number = positiveInteger(issueNumber, "Issue number");
  const analysisId = positiveInteger(commentId, "Analysis comment ID");
  const { data: issue } = await github.rest.issues.get({
    ...context.repo,
    issue_number: number,
  });
  const reason = ineligibleReason(issue, number);
  if (reason) {
    return { reason };
  }
  const { data: comment } = await github.rest.issues.getComment({
    ...context.repo,
    comment_id: analysisId,
  });
  if (typeof issue.url !== "string" || comment.issue_url !== issue.url ||
      typeof comment.body !== "string" || !/^## .*Agentic Issue Triage\b/m.test(comment.body)) {
    throw new Error("The posted triage analysis does not belong to the triggering issue");
  }
  const defaultBranch = context.payload.repository?.default_branch;
  if (typeof defaultBranch !== "string" || !defaultBranch) {
    throw new Error("The repository default branch is missing from the trusted event");
  }
  const ref = `refs/heads/${defaultBranch}`;
  return {
    output: {
      items: [{
        type: "dispatch_workflow",
        workflow_name: "issue-investigation",
        inputs: { issue_number: String(number) },
        ref,
      }],
      errors: [],
    },
    config: {
      dispatch_workflow: {
        workflows: ["issue-investigation"],
        max: 1,
        workflow_files: { "issue-investigation": ".lock.yml" },
        aw_context_workflows: ["issue-investigation"],
        allowed_refs: [ref],
      },
    },
  };
}

module.exports = { prepareHandoff };
