// cspell:ignore ffeb ededed
const assert = require("node:assert/strict");
const { positiveInteger, ineligibleReason, validateAgentOutput, validateInvestigationOutputs } = require("../scripts/issue_workflow_support.cjs");
const { prepareHandoff } = require("../scripts/issue_investigation_handoff.cjs");
const { prepareAssignment } = require("../scripts/copilot_assignment.cjs");
const passed = [];
async function test(name, run) { await run(); passed.push(name); }
const labels = [{ name: "customer-reported", color: "3800e0" }, { name: "KeyVault", color: "e99695" }, { name: "Client", color: "ffeb77" }];
const issue = { number: 42, state: "open", locked: false, labels, assignees: [{ login: "owner" }],
  url: "https://api.github.com/repos/example/sdk/issues/42" };
const context = { repo: { owner: "example", repo: "sdk" }, payload: { repository: { default_branch: "main" } } };
const receipt = { type: "add_comment", url: "https://github.com/example/sdk/issues/42#issuecomment-99" };
const triageComment = { issue_url: issue.url, body: "## Agentic Issue Triage\n\nAnalysis" };
const recommendation = { issue_url: issue.url, body: "## Agentic Issue Investigation\n\n### Outcome\n\nRecommended for Copilot automated fix\n\n### Summary\n\nBounded defect" };
function githubFor(current = issue, comment = triageComment, failure) {
  return { rest: { issues: {
    get: async () => { if (failure === "issue") throw new Error("Issue lookup failed"); return { data: current }; },
    getComment: async () => { if (failure === "comment") throw new Error("Comment lookup failed"); return { data: comment }; },
  } } };
}
function handoff(options = {}) {
  return prepareHandoff({ github: githubFor(), context, issueNumber: 42,
    appliedItems: [{ type: "assign_to_user" }, receipt],
    agentOutput: { items: [{ type: "assign_to_user", issue_number: 42, assignees: ["Owner"] }], errors: [] },
    ownerNotification: "skipped",
    normalizeAssignment: item => ({ success: true, issueNumber: item.issue_number, assignees: item.assignees }), ...options,
  });
}
function assignment(options = {}) {
  return prepareAssignment({ github: githubFor(issue, recommendation), context, issueNumber: 42,
    appliedItems: [receipt], agentOutput: { items: [{ type: "assign_to_agent", issue_number: 42 }], errors: [] }, ...options,
  });
}
function output(items, options = {}) { return validateInvestigationOutputs({ items, ...options }, 42, "example/sdk"); }

async function main() {
  for (const value of [1, 42, Number.MAX_SAFE_INTEGER, "42", "042", "00042", "+42", " 42 ", "9007199254740991"]) {
    await test(`positive integer ${JSON.stringify(value)}`, () => assert.equal(positiveInteger(value, "test"), Number(value)));
  }
  for (const value of [null, undefined, true, false, [], [42], { toString: () => "42" }, NaN, Infinity, -Infinity, 0, -1,
    1.5, Number.MAX_SAFE_INTEGER + 1, "", "-1", "1e2", "0x2a", "42suffix", "42 43", "4.2", "9007199254740992"]) {
    await test(`reject integer ${String(value)}`, () => assert.throws(() => positiveInteger(value, "test"), /positive integer/));
  }
  for (const category of ["Client", "Mgmt", "Service", "Central-EngSys", "Mgmt-EngSys", "Provisioning"]) {
    for (const color of ["ffeb77", "FFEB77", "#ffeb77", "#FFEB77"])
      await test(`category ${category} ${color}`, () => assert.equal(ineligibleReason({ ...issue, labels: [...labels.slice(0, 2), { name: category, color }] }, 42), null));
  }
  for (const service of ["KeyVault", "Storage", "Azure.Core", "Future Service"])
    for (const color of ["e99695", "E99695", "#e99695", "#E99695"])
      await test(`service ${service} ${color}`, () => assert.equal(ineligibleReason({ ...issue, labels: [labels[0], { name: service, color }, labels[2]] }, 42), null));
  await test("extra non-gating labels", () => assert.equal(ineligibleReason({ ...issue, labels: [...labels, { name: "needs-team-attention", color: "3ba0f8" }] }, 42), null));
  await test("customer label case", () => assert.equal(ineligibleReason({ ...issue, labels: [{ ...labels[0], name: "CUSTOMER-REPORTED" }, ...labels.slice(1)] }, 42), null));
  for (const [name, change] of [
    ["closed", { state: "closed" }], ["locked", { locked: true }], ["unknown lock", { locked: undefined }],
    ["PR", { pull_request: {} }], ["wrong issue", { number: 43 }], ["missing customer", { labels: labels.slice(1) }],
    ["missing service", { labels: [labels[0], labels[2]] }], ["missing category", { labels: labels.slice(0, 2) }],
    ["duplicate service", { labels: [...labels, { name: "Storage", color: "e99695" }] }],
    ["duplicate category", { labels: [...labels, { name: "Mgmt", color: "ffeb77" }] }],
  ]) await test(`ineligible ${name}`, () => assert.ok(ineligibleReason({ ...issue, ...change }, 42)));
  for (const blocker of ["needs-triage", "needs-team-triage", "issue-addressed", "needs-author-feedback"]) {
    const current = { ...issue, labels: [...labels, { name: blocker.toUpperCase(), color: "ededed" }] };
    await test(`handoff blocker ${blocker}`, async () => assert.ok((await handoff({ github: githubFor(current) })).reason));
    await test(`assignment blocker ${blocker}`, async () => assert.ok((await assignment({ github: githubFor(current, recommendation) })).reason));
  }
  for (const malformed of [null, [null], ["customer-reported"], [{ name: "Client" }], [{ name: null, color: "ffeb77" }]])
    await test(`malformed labels ${JSON.stringify(malformed)}`, () => assert.throws(() => ineligibleReason({ ...issue, labels: malformed }, 42)));

  for (const invalid of [null, {}, { items: [] }, { items: [null] }, { items: [{}] }, { items: [{ type: 1 }] },
    { items: [{ type: "noop" }], errors: ["failure"] }, { items: [{ type: "noop" }], errors: {} }])
    await test(`invalid terminal output ${JSON.stringify(invalid)}`, () => assert.throws(() => validateAgentOutput(invalid)));
  for (const type of ["report_incomplete", "missing_tool", "missing_data"])
    await test(`incomplete ${type}`, () => assert.throws(() => validateAgentOutput({ items: [{ type }] }), /incomplete/));
  await test("valid noop for invalid dispatch input", () => assert.doesNotThrow(() => validateInvestigationOutputs({ items: [{ type: "noop", message: "Invalid input" }] }, "0", "example/sdk")));
  await test("valid comment", () => assert.equal(output([{ type: "add_comment", body: "More information needed" }]).items[0].item_number, 42));
  await test("valid service closure", () => assert.equal(output([{ type: "close_issue", body: "Service-owned behavior" }]).items[0].issue_number, 42));
  await test("valid comment and assignment", () => assert.equal(output([{ type: "add_comment", body: recommendation.body }, { type: "assign_to_agent", issue_number: 42 }]).items.length, 2));
  for (const reference of [42, "42", "042", "+42", "#42", " #42 "]) {
    for (const field of ["issue_number", "item_number", "pull_number"])
      await test(`normalize ${field} ${JSON.stringify(reference)}`, () => assert.equal(output([{ type: "add_comment", [field]: reference, body: "Details" }]).items[0].issue_number, 42));
  }
  for (const field of ["issue_number", "item_number", "pull_number"])
    for (const reference of [43, "#43", [42], { number: 42 }, null, 0, "42x"])
      await test(`reject ${field} ${JSON.stringify(reference)}`, () => assert.throws(() => output([{ type: "close_issue", [field]: reference, body: "Details" }])));
  for (const repo of ["example/sdk", "EXAMPLE/SDK", " sdk ", " example/sdk ", "sdk", "", " ", null, undefined])
    await test(`same repository ${repo}`, () => assert.doesNotThrow(() => output([{ type: "close_issue", repo, body: "Details" }])));
  for (const repo of ["other/sdk", ["example/sdk"], 42, {}])
    await test(`cross repository ${JSON.stringify(repo)}`, () => assert.throws(() => output([{ type: "close_issue", repo, body: "Details" }]), /repository/));
  for (const items of [
    [{ type: "unknown" }], [{ type: "create_issue" }], [{ type: "add_comment" }, { type: "noop" }],
    [{ type: "add_comment" }, { type: "add_comment" }], [{ type: "close_issue", body: "Details" }, { type: "close_issue", body: "Details" }],
    [{ type: "close_issue", body: "Details" }, { type: "add_comment" }],
    [{ type: "close_issue", body: "Details" }, { type: "assign_to_agent" }],
    [{ type: "assign_to_agent" }], [{ type: "assign_to_agent" }, { type: "assign_to_agent" }],
    [{ type: "close_issue", body: "" }], [{ type: "close_issue", body: " " }], [{ type: "close_issue", body: {} }],
  ]) await test(`reject action combination ${JSON.stringify(items)}`, () => assert.throws(() => output(items)));

  await test("single-owner positive", async () => assert.ok((await handoff()).output));
  for (const repo of ["sdk", " example/sdk ", " EXAMPLE/SDK ", null, undefined]) {
    await test(`single-owner normalized repository ${String(repo)}`, async () => assert.ok((await handoff({
      agentOutput: { items: [{ type: "assign_to_user", issue_number: 42, repo, assignees: ["owner"] }] },
    })).output));
    await test(`assignment normalized repository ${String(repo)}`, async () => assert.ok((await assignment({
      agentOutput: { items: [{ type: "assign_to_agent", issue_number: 42, repo }] },
    })).output));
  }
  for (const repo of ["other/sdk", ["example/sdk"]]) {
    await test(`single-owner foreign request ${JSON.stringify(repo)}`, async () => assert.rejects(handoff({
      agentOutput: { items: [{ type: "assign_to_user", issue_number: 42, repo, assignees: ["owner"] }] },
    }), /repository/));
  }
  await test("single-owner two requests reject even if one matched", async () => assert.rejects(handoff({
    agentOutput: { items: [{ type: "assign_to_user", issue_number: 43, assignees: ["owner"] }, { type: "assign_to_user", issue_number: 42, assignees: ["owner"] }] },
  }), /exactly one/));
  for (const failure of ["issue", "comment"]) {
    await test(`handoff ${failure} API failure`, async () => assert.rejects(handoff({ github: githubFor(issue, triageComment, failure) }), /lookup failed/));
    await test(`assignment ${failure} API failure`, async () => assert.rejects(assignment({ github: githubFor(issue, recommendation, failure) }), /lookup failed/));
  }
  for (const reference of [42, "042", "+42", "#42", " #42 "]) {
    await test(`assignment canonical input ${JSON.stringify(reference)}`, async () => assert.ok((await assignment({ agentOutput: { items: [{ type: "assign_to_agent", issue_number: reference }] } })).output));
  }
  await test("assignment with omitted issue uses trusted configured target", async () => assert.ok((await assignment({ agentOutput: { items: [{ type: "assign_to_agent" }] } })).output));
  await test("assignment rejects foreign repo", async () => assert.rejects(assignment({ agentOutput: { items: [{ type: "assign_to_agent", issue_number: 42, repo: "other/sdk" }] } }), /repository/));
  await test("assignment rejects conflicting alias", async () => assert.rejects(assignment({ agentOutput: { items: [{ type: "assign_to_agent", issue_number: 42, item_number: 43 }] } }), /target/));
  for (const body of ["", "## Agentic Issue Investigation\n\n### Outcome\n\nRequires a human. Analysis provided below\n\n### Summary\nRecommended for Copilot automated fix", "Recommended for Copilot automated fix"]) {
    await test(`assignment rejects nonrecommendation ${JSON.stringify(body)}`, async () => assert.rejects(assignment({ github: githubFor(issue, { ...recommendation, body }) }), /analysis comment/));
  }
  console.log(JSON.stringify({ suite: "Issue workflow corner cases passed", count: passed.length, cases: passed }));
}
main().catch(error => { console.error(error); process.exitCode = 1; });
