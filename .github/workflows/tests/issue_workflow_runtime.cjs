// cspell:ignore ffeb
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { prepareHandoff } = require("../scripts/issue_investigation_handoff.cjs");
const { validateAgentOutput, validateInvestigationOutputs } = require("../scripts/issue_workflow_support.cjs");
const { assignmentCondition } = JSON.parse(fs.readFileSync(0, "utf8"));
const runtime = process.env.GH_AW_RUNTIME;
assert.ok(runtime, "Set GH_AW_RUNTIME to the pinned workflow scripts");
const quiet = () => {};
global.core = {
  info: quiet, debug: quiet, warning: quiet, error: quiet,
  summary: { addRaw() { return this; }, async write() {} },
};
const context = {
  eventName: "workflow_dispatch", repo: { owner: "example", repo: "sdk" },
  payload: { inputs: { issue_number: "42" }, repository: { default_branch: "main" } }, serverUrl: "https://github.com",
};
global.context = context;
const labels = [
  { name: "customer-reported", color: "3800e0" },
  { name: "KeyVault", color: "e99695" },
  { name: "Client", color: "ffeb77" },
];
const issue = {
  number: 42, id: 42, title: "Fixture", state: "open", locked: false, labels, assignees: [],
  url: "https://api.github.com/repos/example/sdk/issues/42", html_url: "https://github.com/example/sdk/issues/42",
};
const calls = [];
let rejectComment = false;
global.github = { rest: { issues: {
  get: async request => ({ data: { ...issue, number: request.issue_number } }),
  getComment: async () => ({ data: { issue_url: issue.url, body: "## Agentic Issue Triage\n\nAnalysis" } }),
  addAssignees: async request => { issue.assignees = request.assignees.map(login => ({ login })); return { data: issue }; },
  createComment: async request => {
    calls.push(["comment", request.issue_number]);
    if (rejectComment) throw new Error("Comment API unavailable");
    return { data: { id: 99, html_url: issue.html_url + "#issuecomment-99" } };
  },
  update: async request => { calls.push(["close", request.issue_number]); return { data: { ...issue, state: "closed" } }; },
} } };

async function main() {
  const { main: assignOwner } = require(path.join(runtime, "assign_to_user.cjs"));
  const { extractCreatedItemFromResult } = require(path.join(runtime, "safe_output_manifest.cjs"));
  const { resolveIssueNumber, extractAssignees } = require(path.join(runtime, "safe_output_helpers.cjs"));
  const { processItems } = require(path.join(runtime, "safe_output_processor.cjs"));
  const request = { type: "assign_to_user", issue_number: 42, assignee: "Owner" };
  const ownerResult = await (await assignOwner({ max: 1 }))(request);
  assert.equal(ownerResult.success, true);
  const receipt = extractCreatedItemFromResult("assign_to_user", ownerResult);
  assert.equal(receipt.number, undefined, "Use the pinned serializer's real receipt shape");
  const handoff = await prepareHandoff({
    github, context, issueNumber: 42,
    appliedItems: [receipt, { type: "add_comment", url: issue.html_url + "#issuecomment-99" }],
    agentOutput: { items: [request], errors: [] }, ownerNotification: "skipped",
    normalizeAssignment: item => ({
      ...resolveIssueNumber(item), assignees: processItems(extractAssignees(item), [], 1, []),
    }),
  });
  assert.ok(handoff.output, "A real single-owner receipt must authorize a clean handoff");

  for (const output of [null, {}, { items: [] }, { items: [null] },
    { items: [{ type: "noop" }], errors: ["Failure"] },
    ...["missing_tool", "missing_data", "report_incomplete"].map(type => ({ items: [{ type }] })),
  ]) assert.throws(() => validateAgentOutput(output), /terminal|incomplete/);
  assert.doesNotThrow(() => validateAgentOutput({ items: [{ type: "noop" }], errors: [] }));
  assert.doesNotThrow(() => validateInvestigationOutputs({ items: [{ type: "noop" }] }, "0", "example/sdk"));
  const closeMessage = { type: "close_issue", issue_number: 42, body: "The service owns this documented behavior." };
  for (const output of [
    { items: [{ ...closeMessage, issue_number: 43 }] },
    { items: [{ ...closeMessage, repo: "other/sdk" }] },
    { items: [closeMessage, { type: "add_comment", body: "Second comment" }] },
    { items: [closeMessage, { type: "assign_to_agent", issue_number: 42 }] },
    { items: [{ type: "assign_to_agent", issue_number: 42 }] },
    { items: [{ ...closeMessage, body: "" }] },
    { items: [{ type: "unknown" }] },
  ]) assert.throws(() => validateInvestigationOutputs(output, 42, "example/sdk"));

  const { main: closeIssue } = require(path.join(runtime, "close_issue.cjs"));
  const options = { target: "42", max: 1, required_labels: ["customer-reported"], state_reason: "not_planned" };
  const scoped = validateInvestigationOutputs({ items: [closeMessage] }, 42, "example/sdk");
  const result = await (await closeIssue(options))(scoped.items[0]);
  assert.equal(result.success, true);
  assert.deepEqual(calls, [["comment", 42], ["close", 42]]);
  calls.length = 0;
  rejectComment = true;
  const failed = await (await closeIssue(options))(scoped.items[0]);
  assert.equal(failed.success, false);
  assert.deepEqual(calls, [["comment", 42]], "Comment failure must prevent closure");

  const { main: assignAgent } = require(path.join(runtime, "assign_to_agent.cjs"));
  const { computeSafeOutputsStatus } = require(path.join(runtime, "safe_outputs_status.cjs"));
  github.request = async () => { throw new Error("Bad credentials"); };
  const ignored = await (await assignAgent({ target: "42", allowed: ["copilot"], "ignore-if-error": true }))(
    { type: "assign_to_agent", issue_number: 42, agent: "copilot" }
  );
  assert.equal(ignored.skipped, true);
  const status = computeSafeOutputsStatus([{ type: "assign_to_agent", result: ignored, success: ignored.success }]);
  assert.equal(status.status, "completed_with_skips");
  assert.equal(status.itemsApplied, 0);
  assert.equal(status.itemsSkipped, 1);
  const confirmationFails = new Function("steps", "return " + assignmentCondition);
  const confirmation = (status, applied, skipped) => confirmationFails({ assignment: { outputs: {
    assignment_requested: "true", status, items_applied: String(applied), items_skipped: String(skipped),
  } } });
  assert.equal(confirmation(status.status, status.itemsApplied, status.itemsSkipped), false);
  assert.equal(confirmation("success", 1, 0), false);
  assert.equal(confirmation("success", 0, 0), true);
  assert.equal(confirmation("failure", 0, 0), true);
  assert.equal(confirmation("completed_with_skips", 0, 0), true);
  assert.equal(confirmation("completed_with_warnings", 1, 0), true);
  console.log("Pinned workflow runtime contracts passed");
}

main().catch(error => { console.error(error); process.exitCode = 1; });
