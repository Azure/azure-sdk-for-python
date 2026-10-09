const { positiveInteger, ineligibleReason } = require("./issue_workflow_support.cjs");

async function prepareHandoff({
  github, context, issueNumber, appliedItems, agentOutput, ownerNotification, normalizeAssignment,
}) {
  const number = positiveInteger(issueNumber, "Issue number");
  if (!Array.isArray(appliedItems) || !Array.isArray(agentOutput?.items) ||
      agentOutput.items.some(item => !item || typeof item.type !== "string") ||
      (agentOutput.errors !== undefined &&
        (!Array.isArray(agentOutput.errors) || agentOutput.errors.length !== 0))) {
    throw new Error("Invalid triage requests or applied receipts");
  }
  if (agentOutput.items.some(item => ["report_incomplete", "missing_tool", "missing_data"].includes(item.type))) {
    throw new Error("Triage reported incomplete work");
  }
  const { data: issue } = await github.rest.issues.get({
    ...context.repo,
    issue_number: number,
  });
  const reason = ineligibleReason(issue, number);
  if (reason) {
    return { reason };
  }
  const mentionRequested = agentOutput.items.some(item => item.type === "mention_owners");
  if (mentionRequested) {
    if (ownerNotification !== "success") {
      throw new Error("Requested owner notification did not succeed");
    }
  } else {
    const assignRequests = agentOutput.items.filter(item => item.type === "assign_to_user");
    if (assignRequests.length !== 1) {
      throw new Error("Expected exactly one assignment request for single-owner routing");
    }
    const normalized = normalizeAssignment(assignRequests[0]);
    if (!normalized.success || normalized.issueNumber !== number ||
        !Array.isArray(normalized.assignees) || normalized.assignees.length !== 1) {
      throw new Error("The assignment request is not a single valid assignment for this issue");
    }
    const requestedOwner = normalized.assignees[0].toLowerCase();
    // The pinned serializer omits assign_to_user.issueNumber. One normalized
    // request and one receipt still bind the applied operation to this issue.
    const appliedAssignments = appliedItems.filter(item => item.type === "assign_to_user");
    const assignment = appliedAssignments[0];
    if (ownerNotification !== "skipped" ||
        appliedAssignments.length !== 1 ||
        (assignment.number !== undefined && assignment.number !== number) ||
        (assignment.repo !== undefined && assignment.repo.toLowerCase() !== `${context.repo.owner}/${context.repo.repo}`.toLowerCase()) ||
        !issue.assignees?.some(assignee => assignee.login.toLowerCase() === requestedOwner)) {
      throw new Error("The single-owner assignment route was not completed");
    }
  }
  let analysisPosted = false;
  // The native comment_id output can refer to routing rather than analysis.
  for (const receipt of appliedItems.filter(item => item.type === "add_comment").reverse()) {
    const match = typeof receipt.url === "string" && receipt.url.match(/#issuecomment-(\d+)$/);
    if (!match) {
      throw new Error("Invalid applied comment receipt");
    }
    const { data: comment } = await github.rest.issues.getComment({
      ...context.repo,
      comment_id: positiveInteger(match[1], "Analysis comment ID"),
    });
    if (typeof issue.url !== "string" || comment.issue_url !== issue.url) {
      throw new Error("The posted triage comment does not belong to the triggering issue");
    }
    if (typeof comment.body === "string" && /^## .*Agentic Issue Triage\b/m.test(comment.body)) {
      analysisPosted = true;
      break;
    }
  }
  if (!analysisPosted) {
    throw new Error("No applied triage analysis comment was found");
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
