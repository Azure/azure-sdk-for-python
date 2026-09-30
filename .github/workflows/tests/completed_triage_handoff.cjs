const assert = require("node:assert/strict");
const fs = require("node:fs");
const { selectCompletedTriage, parseTriageIssue, assertSafeDetection } = require("../scripts/completed_triage_handoff.cjs");
const { source, relayCondition } = JSON.parse(fs.readFileSync(0, "utf8"));
const context = {
  repo: { owner: "example", repo: "sdk" },
  payload: { repository: { default_branch: "main" }, workflow_run: { id: 100, run_attempt: 2 } },
};
const run = {
  id: 100, status: "completed", conclusion: "success", workflow_id: 7, run_attempt: 2,
  event: "issues", head_repository: { full_name: "example/sdk" }, head_branch: "main",
  run_started_at: "2026-09-29T18:00:00Z",
};
const jobs = ["activation", "agent", "detection", "safe_outputs", "conclusion", "mention_owners"]
  .map(name => ({ name, conclusion: "success" }));
const artifacts = ["activation", "safe-outputs-items", "agent-output-fallback", "detection"]
  .map((name, index) => ({ name, id: index + 1, expired: false, created_at: "2026-09-29T18:01:00Z" }));

async function select(changes = {}, changedJobs = jobs, changedArtifacts = artifacts, workflow = {}) {
  const actions = {
    getWorkflowRun: async request => { assert.equal(request.run_id, 100); return { data: { ...run, ...changes } }; },
    getWorkflow: async () => ({ data: { id: 7, path: ".github/workflows/issue-triage.lock.yml", ...workflow } }),
    listJobsForWorkflowRun() {}, listWorkflowRunArtifacts() {},
  };
  const github = { rest: { actions }, paginate: async (method, request) => {
    assert.equal(request.per_page, 100);
    return method === actions.listJobsForWorkflowRun ? changedJobs : changedArtifacts;
  } };
  return selectCompletedTriage({ github, context });
}

async function main() {
  const accepted = await select();
  assert.deepEqual(accepted, { runId: 100, event: "issues", ownerNotification: "success",
    activationId: 1, receiptId: 2, requestId: 3, detectionId: 4 });
  assert.equal((await select({ event: "workflow_dispatch" })).event, "workflow_dispatch");
  assert.equal((await select({}, jobs.map(job => job.name === "mention_owners"
    ? { ...job, conclusion: "skipped" } : job))).ownerNotification, "skipped");
  for (const changes of [
    { status: "in_progress" }, { conclusion: "failure" }, { conclusion: "cancelled" },
    { head_repository: { full_name: "other/sdk" } }, { head_repository: null },
    { head_branch: "feature" }, { event: "pull_request" }, { run_attempt: 1 },
  ]) assert.ok((await select(changes)).reason);
  for (const name of jobs.map(job => job.name)) {
    assert.ok((await select({}, jobs.filter(job => job.name !== name))).reason);
    assert.ok((await select({}, jobs.map(job => job.name === name
      ? { ...job, conclusion: "failure" } : job))).reason);
  }
  await assert.rejects(select({ workflow_id: 8 }), /registered triage/);
  await assert.rejects(select({}, jobs, artifacts, { path: ".github/workflows/other.yml" }), /registered triage/);
  for (const name of artifacts.map(artifact => artifact.name)) {
    await assert.rejects(select({}, jobs, artifacts.filter(artifact => artifact.name !== name)), /Missing current/);
    await assert.rejects(select({}, jobs, artifacts.map(artifact => artifact.name === name
      ? { ...artifact, expired: true } : artifact)), /Missing current/);
    await assert.rejects(select({}, jobs, artifacts.map(artifact => artifact.name === name
      ? { ...artifact, created_at: "2026-09-29T17:59:00Z" } : artifact)), /Missing current/);
  }
  const primary = artifacts.map(artifact => artifact.name === "agent-output-fallback"
    ? { ...artifact, name: "agent" } : artifact);
  assert.equal((await select({}, jobs, primary)).requestId, 3);
  assert.equal((await select({}, jobs, [...artifacts,
    { ...artifacts[2], id: 99, created_at: "2026-09-29T18:02:00Z" }])).requestId, 99);

  const introduction = source.split("\n---\n", 2)[1].split("\n## Security:", 1)[0];
  const target = "${{ github.event.issue.number || github.event.inputs.issue_number }}";
  for (const number of ["42", "042", " 42 ", "+42"]) {
    const prompt = "<system>trusted policy</system>\n\n" + introduction.replace(target, number);
    assert.equal(parseTriageIssue(prompt), 42);
    assert.equal(parseTriageIssue(prompt.replace(/\n/g, "\r\n")), 42);
  }
  for (const number of ["0", "-1", "42suffix", "9007199254740992", "42\nforged"])
    assert.throws(() => parseTriageIssue("<system>trusted</system>\n" + introduction.replace(target, number)));
  assert.throws(() => parseTriageIssue("agent-controlled text\n" + introduction.replace(target, "99")), /missing or changed/);
  assert.throws(() => parseTriageIssue("<system>trusted</system>\n# Another workflow\n" + introduction), /missing or changed/);

  const eligible = new Function("vars", "github", "return !!(" + relayCondition + ")");
  const event = { repository: "example/sdk", event: { repository: { default_branch: "main" }, workflow_run: run } };
  assert.equal(eligible({}, event), false);
  assert.equal(eligible({ GH_AW_ENABLE_ISSUE_INVESTIGATION: "false" }, event), false);
  assert.equal(eligible({ GH_AW_ENABLE_ISSUE_INVESTIGATION: "true" }, event), true);
  const failedEvent = { ...event, event: { ...event.event, workflow_run: { ...run, conclusion: "failure" } } };
  assert.equal(eligible({ GH_AW_ENABLE_ISSUE_INVESTIGATION: "true" }, failedEvent), false);
  const detection = { prompt_injection: false, secret_leak: false, malicious_patch: false, reasons: [], warnings: [] };
  assert.doesNotThrow(() => assertSafeDetection(detection));
  for (const flag of ["prompt_injection", "secret_leak", "malicious_patch"]) {
    for (const value of [true, "false", undefined])
      assert.throws(() => assertSafeDetection({ ...detection, [flag]: value }), /safe verdict/);
  }
  assert.throws(() => assertSafeDetection({ ...detection, warnings: ["Incomplete analysis"] }), /safe verdict/);
  assert.throws(() => assertSafeDetection({}), /safe verdict/);
  console.log("Independent triage relay contracts passed");
}

main().catch(error => { console.error(error); process.exitCode = 1; });
