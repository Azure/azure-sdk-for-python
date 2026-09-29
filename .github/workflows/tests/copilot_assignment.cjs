const assert = require("node:assert/strict");
const { prepareAssignment } = require("../scripts/copilot_assignment.cjs");

const issueUrl = "https://api.github.com/repos/example/sdk/issues/42";
const analysis = {
  issue_url: issueUrl,
  body: "## 🔍 Agentic Issue Investigation\n\n### Outcome\n\nRecommended for Copilot automated fix\n\n### Summary\n\nDetails",
};
const receipt = { type: "add_comment", url: "https://github.com/example/sdk/issues/42#issuecomment-99" };
const context = { repo: { owner: "example", repo: "sdk" } };
let cases = 0;

async function run(changes = {}, comment = analysis, event = context, inputs = {}) {
  const issue = { number: 42, url: issueUrl, state: "open", locked: false, ...changes };
  const calls = [];
  const github = { rest: { issues: {
    get: async request => { calls.push(request); return { data: issue }; },
    getComment: async request => { calls.push(request); return { data: inputs.comments ? inputs.comments[request.comment_id] : comment }; },
  } } };
  const result = await prepareAssignment({
    github, context: event, issueNumber: "42",
    appliedItems: [receipt],
    agentOutput: { items: [{ type: "assign_to_agent", target: "42", issue_number: 42 }], errors: [] },
    ...inputs,
  });
  if (result.output) {
    assert.deepEqual(calls[0], { ...context.repo, issue_number: 42 });
    assert.deepEqual(calls[1], { ...context.repo, comment_id: 99 });
    assert.deepEqual(result.output.items, [{
      type: "assign_to_agent", name: "copilot", target: "42", issue_number: 42,
    }]);
    assert.equal(result.config.assign_to_agent.max, 1);
    assert.deepEqual(result.config.assign_to_agent.allowed, ["copilot"]);
    assert.equal(result.config.assign_to_agent["ignore-if-error"], true);
  }
  cases++;
  return result;
}

async function main() {
  assert.ok((await run()).output);
  assert.ok((await run({}, analysis, context, { agentOutput: { items: [{ type: "assign_to_agent", target: "#42" }], errors: [] } })).output);

  // Skipped when assignment not requested
  const notRequested = await run({}, analysis, context, { agentOutput: { items: [{ type: "noop" }], errors: [] } });
  assert.equal(notRequested.output, undefined);
  assert.ok(notRequested.reason.includes("not requested"));

  // Closed or locked
  assert.equal((await run({ state: "closed" })).output, undefined);
  assert.equal((await run({ locked: true })).output, undefined);

  // Rejections
  await assert.rejects(run({ pull_request: {} }), /not the investigated issue/);
  await assert.rejects(run({ number: 43 }), /not the investigated issue/);
  await assert.rejects(run({}, analysis, context, {
    agentOutput: { items: [{ type: "assign_to_agent", target: "43" }], errors: [] },
  }), /does not target/);
  await assert.rejects(run({}, analysis, context, {
    agentOutput: { items: [{ type: "assign_to_agent", target: "42" }, { type: "assign_to_agent", target: "42" }], errors: [] },
  }), /at most one/);
  await assert.rejects(run({}, analysis, context, { appliedItems: [] }), /No applied comment receipt/);
  await assert.rejects(run({}, { ...analysis, body: "Requires a human. Analysis provided below" }), /No applied investigation analysis/);
  await assert.rejects(run({}, { ...analysis, issue_url: issueUrl + "0" }), /does not belong/);
  for (const type of ["report_incomplete", "missing_tool", "missing_data"]) {
    await assert.rejects(run({}, analysis, context, { agentOutput: { items: [{ type }] } }), /incomplete work/);
  }
  for (const value of ["", "0", "-1", "42suffix", "1.5"]) {
    await assert.rejects(run({}, analysis, context, { issueNumber: value }), /positive integer/);
  }
  cases += 12;
  console.log(`Copilot assignment cases passed: ${cases}`);
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
