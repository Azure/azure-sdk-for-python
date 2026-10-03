const { positiveInteger, ineligibleReason } = require("./issue_workflow_support.cjs");

async function prepareAssignment({ github, context, issueNumber, appliedItems, agentOutput }) {
  const number = positiveInteger(issueNumber, "Issue number");
  if (!Array.isArray(appliedItems) || !Array.isArray(agentOutput?.items) ||
      agentOutput.items.some(item => !item || typeof item.type !== "string") ||
      (agentOutput.errors !== undefined &&
        (!Array.isArray(agentOutput.errors) || agentOutput.errors.length !== 0))) {
    throw new Error("Invalid investigation requests or applied receipts");
  }
  if (agentOutput.items.some(item => ["report_incomplete", "missing_tool", "missing_data"].includes(item.type))) {
    throw new Error("Investigation reported incomplete work");
  }
  const assignRequests = agentOutput.items.filter(item => item.type === "assign_to_agent");
  if (assignRequests.length === 0) {
    return { reason: "assignment was not requested by the agent" };
  }
  if (assignRequests.length !== 1) {
    throw new Error("Expected at most one assign_to_agent request");
  }
  const request = assignRequests[0];
  const target = String(request.target ?? request.issue_number ?? "").trim();
  if (target !== String(number) && target !== `#${number}`) {
    throw new Error("The assign_to_agent request does not target the investigated issue");
  }

  const { data: issue } = await github.rest.issues.get({
    ...context.repo,
    issue_number: number,
  });
  if (issue.number !== number || Object.hasOwn(issue, "pull_request")) {
    throw new Error("The target is not the investigated issue");
  }
  const reason = ineligibleReason(issue, number);
  if (reason) return { reason };

  const commentReceipts = appliedItems.filter(item => item.type === "add_comment");
  if (commentReceipts.length === 0) {
    throw new Error("No applied comment receipt found");
  }

  let analysisPosted = false;
  for (const receipt of commentReceipts.reverse()) {
    const match = typeof receipt.url === "string" && receipt.url.match(/#issuecomment-(\d+)$/);
    if (!match) {
      throw new Error("Invalid applied comment receipt");
    }
    const { data: comment } = await github.rest.issues.getComment({
      ...context.repo,
      comment_id: positiveInteger(match[1], "Analysis comment ID"),
    });
    if (typeof issue.url !== "string" || comment.issue_url !== issue.url) {
      throw new Error("The posted investigation comment does not belong to the investigated issue");
    }
    if (typeof comment.body === "string" &&
        /^## .*Agentic Issue Investigation\b/m.test(comment.body) &&
        /^### Outcome\s+Recommended for Copilot automated fix\s*(?:\n### |$)/m.test(comment.body)) {
      analysisPosted = true;
      break;
    }
  }
  if (!analysisPosted) {
    throw new Error("No applied investigation analysis comment recommending Copilot was found");
  }

  return {
    output: {
      items: [{
        type: "assign_to_agent",
        name: "copilot",
        target: String(number),
        issue_number: number,
      }],
      errors: [],
    },
    config: {
      assign_to_agent: {
        allowed: ["copilot"],
        "ignore-if-error": true,
        max: 1,
        name: "copilot",
        target: String(number),
      },
    },
  };
}

module.exports = { prepareAssignment };
