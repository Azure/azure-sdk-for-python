function positiveInteger(value, name) {
  const text = String(value).trim();
  if (!/^\+?\d+$/.test(text) || !Number.isSafeInteger(Number(text)) || Number(text) <= 0) {
    throw new Error(`${name} must be a positive integer`);
  }
  return Number(text);
}

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
  if (issue.state !== "open" || issue.locked !== false) {
    return { reason: "the issue is closed or locked" };
  }

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
        /Recommended for Copilot automated fix/.test(comment.body)) {
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
