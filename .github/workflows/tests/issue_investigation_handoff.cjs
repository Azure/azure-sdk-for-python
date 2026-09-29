// cspell:ignore ffeb ededed
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { prepareHandoff } = require("../scripts/issue_investigation_handoff.cjs");
const { deferScript } = JSON.parse(fs.readFileSync(0, "utf8"));

const labels = [
  { name: "customer-reported", color: "3800e0" },
  { name: "KeyVault", color: "e99695" },
  { name: "Client", color: "FFEB77" },
];
const context = {
  repo: { owner: "example", repo: "sdk" },
  payload: { repository: { default_branch: "main" } },
};
const issueUrl = "https://api.github.com/repos/example/sdk/issues/42";
const analysis = { issue_url: issueUrl, body: "## Agentic Issue Triage\n\nAnalysis" };
const receipt = { type: "add_comment", url: "https://github.com/example/sdk/issues/42#issuecomment-99" };
let cases = 0;

async function run(changes = {}, comment = analysis, event = context, inputs = {}) {
  const issue = { number: 42, url: issueUrl, state: "open", locked: false, labels, ...changes };
  const calls = [];
  const github = { rest: { issues: {
    get: async request => { calls.push(request); return { data: issue }; },
    getComment: async request => {
      calls.push(request);
      return { data: inputs.comments ? inputs.comments[request.comment_id] : comment };
    },
  } } };
  const result = await prepareHandoff({
    github, context: event, issueNumber: "42",
    appliedItems: [receipt],
    agentOutput: { items: [{ type: "mention_owners" }], errors: [] },
    ownerNotification: "success",
    normalizeAssignment: item => ({ success: true, issueNumber: item.issue_number, assignees: item.assignees }),
    ...inputs,
  });
  assert.deepEqual(calls[0], { ...context.repo, issue_number: 42 });
  if (result.output) {
    assert.ok(calls.length >= 2);
    assert.deepEqual(result.output.items, [{
      type: "dispatch_workflow", workflow_name: "issue-investigation",
      inputs: { issue_number: "42" }, ref: "refs/heads/main",
    }]);
    assert.equal(result.config.dispatch_workflow.max, 1);
    assert.deepEqual(result.config.dispatch_workflow.workflows, ["issue-investigation"]);
    assert.deepEqual(result.config.dispatch_workflow.allowed_refs, ["refs/heads/main"]);
  } else {
    assert.equal(calls.length, 1);
    assert.ok(result.reason);
  }
  cases++;
  return result;
}

async function main() {
  assert.ok((await run()).output);
  for (const issueNumber of [42, "042", "00042", " 42 ", "+42"]) {
    assert.ok((await run({}, analysis, context, { issueNumber })).output);
  }
  assert.ok((await run({ labels: [labels[0], labels[1], { ...labels[2], color: labels[2].color.toLowerCase() }] })).output);
  for (const category of ["Client", "Mgmt", "Service", "Central-EngSys", "Mgmt-EngSys", "Provisioning"]) {
    assert.ok((await run({ labels: [labels[0], labels[1], { name: category, color: "#FFEB77" }] })).output);
  }
  for (const service of ["KeyVault", "Storage", "App Configuration", "Azure.Identity", "Future service"]) {
    assert.ok((await run({ labels: [labels[0], { name: service, color: "#E99695" }, labels[2]] })).output);
  }
  assert.ok((await run({ labels: [...labels, { name: "question", color: "ffffff" }] })).output);
  for (const changes of [
    { state: "closed" }, { locked: true }, { locked: undefined },
    { pull_request: {} }, { number: 43 },
    { labels: labels.slice(1) }, { labels: [labels[0], labels[2]] },
    { labels: labels.slice(0, 2) },
    { labels: [...labels, { name: "Storage", color: "e99695" }] },
    { labels: [...labels, { name: "Mgmt", color: "FFEB77" }] },
  ]) {
    assert.equal((await run(changes)).output, undefined);
  }
  for (const name of ["needs-triage", "needs-team-triage", "issue-addressed", "needs-author-feedback"]) {
    assert.equal((await run({ labels: [...labels, { name, color: "EDEDED" }] })).output, undefined);
  }
  for (const value of ["", "0", "-1", "42suffix", "1.5", "9007199254740992"]) {
    await assert.rejects(run({}, analysis, context, { issueNumber: value }), /positive integer/);
    await assert.rejects(run({}, analysis, context, {
      appliedItems: [{ ...receipt, url: `https://github.com/example/sdk/issues/42#issuecomment-${value}` }],
    }), /positive integer|comment receipt/);
    cases += 2;
  }
  await assert.rejects(run({ labels: ["customer-reported"] }), /names or colors/);
  await assert.rejects(run({}, { ...analysis, issue_url: issueUrl + "0" }), /does not belong/);
  await assert.rejects(run({}, { ...analysis, body: "No analysis was posted" }), /No applied triage analysis/);
  await assert.rejects(run({}, analysis, { ...context, payload: {} }), /default branch/);
  const unavailable = { rest: { issues: { get: async () => { throw new Error("API unavailable"); } } } };
  await assert.rejects(
    prepareHandoff({
      github: unavailable, context, issueNumber: "42",
      appliedItems: [receipt], agentOutput: { items: [{ type: "mention_owners" }], errors: [] },
    }),
    /API unavailable/
  );
  cases += 5;

  const singleOwner = {
    appliedItems: [
      { type: "assign_to_user", number: 42 },
      receipt,
      { ...receipt, url: "https://github.com/example/sdk/issues/42#issuecomment-100" },
    ],
    agentOutput: { items: [{ type: "assign_to_user", issue_number: 42, assignees: ["Owner"] }], errors: [] },
    ownerNotification: "skipped",
    comments: {
      99: { ...analysis, body: "Routing to the assigned owner." },
      100: analysis,
    },
  };
  assert.ok((await run({ assignees: [{ login: "owner" }] }, analysis, context, singleOwner)).output);
  await assert.rejects(run({}, analysis, context, singleOwner), /assignment route/);
  await assert.rejects(run({ assignees: [{ login: "someone-else" }] }, analysis, context, singleOwner), /assignment route/);
  await assert.rejects(run({ assignees: [{ login: "owner" }] }, analysis, context, {
    ...singleOwner, appliedItems: singleOwner.appliedItems.filter(item => item.type !== "assign_to_user"),
  }), /assignment route/);
  await assert.rejects(run({ assignees: [{ login: "owner" }] }, analysis, context, {
    ...singleOwner, appliedItems: [{ type: "assign_to_user", number: 43 }, singleOwner.appliedItems[1], singleOwner.appliedItems[2]],
  }), /assignment route/);
  await assert.rejects(run({ assignees: [{ login: "owner" }] }, analysis, context, {
    ...singleOwner, agentOutput: { items: [{ type: "assign_to_user", issue_number: 42, assignees: ["Owner"] }, { type: "assign_to_user", issue_number: 42, assignees: ["Owner2"] }] },
  }), /exactly one assignment request/);
  await assert.rejects(run({ assignees: [{ login: "owner" }] }, analysis, context, {
    ...singleOwner, agentOutput: { items: [{ type: "assign_to_user", issue_number: 43, assignees: ["owner"] }] },
  }), /assignment request is not a single valid assignment/);
  await assert.rejects(run({ assignees: [{ login: "owner" }] }, analysis, context, {
    ...singleOwner, appliedItems: singleOwner.appliedItems.slice(0, 2),
  }), /No applied triage analysis/);
  for (const ownerNotification of ["skipped", "failure", "cancelled"]) {
    await assert.rejects(run({}, analysis, context, { ownerNotification }), /notification did not succeed/);
  }
  for (const type of ["report_incomplete", "missing_tool", "missing_data"]) {
    await assert.rejects(run({}, analysis, context, { agentOutput: { items: [{ type }] } }), /incomplete work/);
  }
  await assert.rejects(run({}, analysis, context, { appliedItems: [] }), /No applied triage analysis/);
  await assert.rejects(run({}, analysis, context, { agentOutput: { items: [], errors: ["failure"] } }), /Invalid triage/);
  cases += 15;

  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "investigation-handoff-"));
  const file = path.join(directory, "output.json");
  const priorOutput = process.env.GH_AW_AGENT_OUTPUT;
  try {
    process.env.GH_AW_AGENT_OUTPUT = file;
    const pending = [
      { type: "dispatch_workflow", workflow_name: "issue-investigation" },
      { type: "add_labels", labels: ["customer-reported", "KeyVault", "Client"] },
      { type: "add_comment", body: analysis.body },
      { type: "mention_owners", owners: "example" },
      { type: "issue_investigation", issue_number: "42" },
    ];
    fs.writeFileSync(file, JSON.stringify({ items: pending, errors: [] }));
    const execute = new Function("require", "core", deferScript);
    execute(require, { info: () => {} });
    assert.deepEqual(JSON.parse(fs.readFileSync(file, "utf8")).items, pending.slice(1, 4));
    assert.equal((await run({ labels: [] })).output, undefined);
    assert.ok((await run()).output);
    fs.writeFileSync(file, JSON.stringify({ errors: [] }));
    assert.throws(() => execute(require, { info: () => {} }), /items array/);
    fs.writeFileSync(file, "{");
    assert.throws(() => execute(require, { info: () => {} }), SyntaxError);
    cases += 3;
  } finally {
    if (priorOutput === undefined) delete process.env.GH_AW_AGENT_OUTPUT;
    else process.env.GH_AW_AGENT_OUTPUT = priorOutput;
    fs.rmSync(directory, { recursive: true });
  }
  console.log(`Handoff runtime cases passed: ${cases}`);
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
