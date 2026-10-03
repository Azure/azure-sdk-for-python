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

function validateAgentOutput(output) {
  if (!Array.isArray(output?.items) || output.items.length === 0 ||
      output.items.some(item => !item || typeof item.type !== "string") ||
      (output.errors !== undefined && (!Array.isArray(output.errors) || output.errors.length !== 0))) {
    throw new Error("Agent output must contain nonempty terminal items and no errors");
  }
  if (output.items.some(item => ["report_incomplete", "missing_tool", "missing_data"].includes(item.type))) {
    throw new Error("Agent reported incomplete work");
  }
}

function validateInvestigationOutputs(output, issueNumber, repository) {
  validateAgentOutput(output);
  const allowed = new Set(["add_comment", "close_issue", "assign_to_agent", "noop"]);
  if (output.items.some(item => !allowed.has(item.type))) {
    throw new Error("Unsupported investigation output type");
  }
  const mutations = output.items.filter(item => item.type !== "noop");
  if (mutations.length === 0) return output;
  if (output.items.some(item => item.type === "noop")) {
    throw new Error("Investigation cannot mix mutations with noop");
  }
  const number = positiveInteger(issueNumber, "Issue number");
  const scoped = output.items.map(item => {
    if (item.repo && item.repo.toLowerCase() !== repository.toLowerCase()) {
      throw new Error("Investigation output cannot target another repository");
    }
    for (const field of ["issue_number", "item_number", "pull_number"]) {
      if (item[field] !== undefined && positiveInteger(String(item[field]).replace(/^#/, ""), field) !== number) {
        throw new Error("Investigation output does not target the dispatched issue");
      }
    }
    return { ...item, issue_number: number, ...(item.type === "add_comment" ? { item_number: number } : {}) };
  });
  const comments = scoped.filter(item => item.type === "add_comment");
  const closures = scoped.filter(item => item.type === "close_issue");
  const assignments = scoped.filter(item => item.type === "assign_to_agent");
  if (comments.length > 1 || closures.length > 1 || assignments.length > 1 ||
      (closures.length && (comments.length || assignments.length))) {
    throw new Error("Investigation output contains conflicting or repeated actions");
  }
  if (closures.length && (typeof closures[0].body !== "string" || !closures[0].body.trim())) {
    throw new Error("Issue closure requires its explanation in the close_issue body");
  }
  if (assignments.length && comments.length !== 1) {
    throw new Error("Copilot assignment requires an analysis comment in the same output");
  }
  return { ...output, items: scoped };
}

module.exports = { positiveInteger, ineligibleReason, validateAgentOutput, validateInvestigationOutputs };
