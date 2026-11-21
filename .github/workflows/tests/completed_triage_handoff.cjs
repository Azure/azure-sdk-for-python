const assert = require("node:assert/strict");
const fs = require("node:fs");
const { selectCompletedTriage, parseTriageIssue, assertSafeDetection } = require("../scripts/completed_triage_handoff.cjs");
const { relayCondition } = JSON.parse(fs.readFileSync(0, "utf8"));
const passed = [];
async function test(name, execute) { await execute(); passed.push(name); }
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
  .map((name, index) => ({ id: 500 + index, name, conclusion: "success", run_attempt: 2 }));
const artifacts = ["safe-outputs-items", "agent-output-fallback", "detection"]
  .map((name, index) => ({ name, id: index + 1, expired: false, created_at: "2026-09-29T18:01:00Z" }));
function logLine(value, event = "issues") {
  const field = event === "issues" ? "GH_AW_GITHUB_EVENT_ISSUE_NUMBER" : "GH_AW_GITHUB_EVENT_INPUTS_ISSUE_NUMBER";
  return `2026-09-29T18:00:02.1234567Z   ${field}: ${value}\n` +
    `2026-09-29T18:00:02.2234567Z Your task is to analyze issue #${value} and perform initial triage following the decision flow below\n`;
}
async function select(changes = {}, changedJobs = jobs, changedArtifacts = artifacts, workflow = {}, options = {}) {
  const actions = {
    getWorkflowRun: async request => {
      assert.equal(request.run_id, 100);
      if (options.error === "run") throw new Error("run API unavailable");
      return { data: { ...run, ...changes } };
    },
    getWorkflow: async () => {
      if (options.error === "workflow") throw new Error("workflow API unavailable");
      return { data: { id: 7, path: ".github/workflows/issue-triage.lock.yml", ...workflow } };
    },
    listJobsForWorkflowRunAttempt() {}, listWorkflowRunArtifacts() {},
  };
  const github = { rest: { actions }, paginate: async (method, request) => {
    assert.equal(request.per_page, 100);
    assert.equal(request.run_id, 100);
    if (method === actions.listJobsForWorkflowRunAttempt) {
      assert.equal(request.attempt_number, 2);
      if (options.error === "jobs") throw new Error("jobs API unavailable");
      return changedJobs;
    }
    if (options.error === "artifacts") throw new Error("artifacts API unavailable");
    return changedArtifacts;
  }, request: async (endpoint, request) => {
    assert.equal(endpoint, "GET /repos/{owner}/{repo}/actions/jobs/{job_id}/logs");
    assert.equal(request.job_id, 500);
    if (options.error === "logs") throw new Error("logs API unavailable");
    return { data: options.log ?? logLine("42", changes.event ?? run.event) };
  } };
  return selectCompletedTriage({ github, context: options.context ?? context });
}

async function main() {
  await test("successful issue run without activation artifact", async () => {
    assert.deepEqual(await select(), { runId: 100, attempt: 2, issueNumber: 42, event: "issues",
      ownerNotification: "success", receiptId: 1, requestId: 2, detectionId: 3 });
  });
  await test("workflow_dispatch uses the input context", async () => assert.equal((await select({ event: "workflow_dispatch" })).issueNumber, 42));
  await test("single owner legitimately skips mention job", async () => assert.equal((await select({}, jobs.map(job => job.name === "mention_owners"
    ? { ...job, conclusion: "skipped" } : job))).ownerNotification, "skipped"));
  for (const [name, changes] of [
    ["wrong run", { id: 101 }], ["running", { status: "in_progress" }], ["queued", { status: "queued" }],
    ...["failure", "cancelled", "skipped", "timed_out", "neutral", "action_required"].map(conclusion => [conclusion, { conclusion }]),
    ["foreign repository", { head_repository: { full_name: "other/sdk" } }], ["missing repository", { head_repository: null }],
    ["nondefault branch", { head_branch: "feature" }], ["pull request trigger", { event: "pull_request" }],
    ["push trigger", { event: "push" }], ["old attempt", { run_attempt: 1 }], ["new attempt", { run_attempt: 3 }],
  ]) await test(`skip parent: ${name}`, async () => assert.ok((await select(changes)).reason));
  await test("repository names are case insensitive", async () => assert.equal((await select({ head_repository: { full_name: "EXAMPLE/SDK" } })).runId, 100));
  for (const name of jobs.map(job => job.name)) {
    await test(`missing job ${name}`, async () => assert.ok((await select({}, jobs.filter(job => job.name !== name))).reason));
    await test(`duplicate job ${name}`, async () => assert.ok((await select({}, [...jobs, jobs.find(job => job.name === name)])).reason));
    for (const conclusion of ["failure", "cancelled", "timed_out", "neutral"]) {
      await test(`${name} ${conclusion}`, async () => assert.ok((await select({}, jobs.map(job => job.name === name
        ? { ...job, conclusion } : job))).reason));
    }
    await test(`stale attempt job ${name}`, async () => assert.ok((await select({}, jobs.map(job => job.name === name
      ? { ...job, run_attempt: 1 } : job))).reason));
  }
  await test("unregistered workflow ID", async () => assert.rejects(select({ workflow_id: 8 }), /registered triage/));
  await test("same name wrong workflow path", async () => assert.rejects(select({}, jobs, artifacts, { path: ".github/workflows/other.yml" }), /registered triage/));
  await test("invalid run timestamp", async () => assert.rejects(select({ run_started_at: "invalid" }), /start time/));
  for (const name of artifacts.map(artifact => artifact.name)) {
    for (const [description, transformed] of [
      ["absent", artifacts.filter(artifact => artifact.name !== name)],
      ["expired", artifacts.map(artifact => artifact.name === name ? { ...artifact, expired: true } : artifact)],
      ["old attempt", artifacts.map(artifact => artifact.name === name ? { ...artifact, created_at: "2026-09-29T17:59:00Z" } : artifact)],
      ["ambiguous", [...artifacts, { ...artifacts.find(artifact => artifact.name === name), id: 99 }]],
      ["unknown expiration", artifacts.map(artifact => artifact.name === name ? { ...artifact, expired: undefined } : artifact)],
      ["invalid timestamp", artifacts.map(artifact => artifact.name === name ? { ...artifact, created_at: "invalid" } : artifact)],
    ]) await test(`${name} ${description}`, async () => assert.rejects(select({}, jobs, transformed), /one current/));
  }
  await test("primary agent artifact fallback", async () => assert.equal((await select({}, jobs,
    artifacts.map(a => a.name === "agent-output-fallback" ? { ...a, name: "agent" } : a))).requestId, 2));
  await test("ignore artifacts from previous attempt", async () => assert.equal((await select({}, jobs, [...artifacts,
    { ...artifacts[0], id: 90, created_at: "2026-09-29T17:59:59Z" }])).receiptId, 1));
  for (const error of ["run", "workflow", "jobs", "artifacts", "logs"]) {
    await test(`API failure ${error}`, async () => assert.rejects(select({}, jobs, artifacts, {}, { error }), /API unavailable/));
  }
  for (const event of ["issues", "workflow_dispatch"]) {
    for (const number of ["42", "042", "00042", " 42 ", "+42", "9007199254740991"]) {
      await test(`${event} valid target ${number}`, () => assert.equal(parseTriageIssue(logLine(number, event), event), Number(number)));
    }
    for (const value of ["", "0", "-1", "42suffix", "42 99", "1.5", "9007199254740992", "***", "42\n99"]) {
      await test(`${event} invalid target ${JSON.stringify(value)}`, () => {

        assert.throws(() => parseTriageIssue(logLine(value, event), event));
      });
    }
    await test(`${event} CRLF and duplicate context`, () => assert.equal(parseTriageIssue((logLine("042", event) + logLine("42", event)).replace(/\n/g, "\r\n"), event), 42));
    await test(`${event} conflicting context`, () => assert.throws(() => parseTriageIssue(logLine("42", event) + logLine("43", event), event), /inconsistent/));
    await test(`${event} no timestamp is not a trusted line`, () => assert.throws(() => parseTriageIssue(logLine("42", event).replace(/^\S+ /, ""), event), /missing/));
    await test(`${event} context from unrelated field`, () => assert.throws(() => parseTriageIssue(logLine("42", event).replace("GH_AW_GITHUB_EVENT", "UNTRUSTED_EVENT"), event), /missing/));
  }
  await test("missing log", () => assert.throws(() => parseTriageIssue(null, "issues"), /missing/));
  await test("oversized log", () => assert.throws(() => parseTriageIssue("x".repeat(8 * 1024 * 1024 + 1), "issues"), /size/));
  await test("unsupported event", () => assert.throws(() => parseTriageIssue(logLine(42), "pull_request"), /Unsupported/));

  const eligible = new Function("vars", "github", "return !!(" + relayCondition + ")");
  const event = { repository: "example/sdk", event: { repository: { default_branch: "main" }, workflow_run: run } };
  for (const value of [undefined, "false", "1", " true ", true])
    await test(`opt-in remains off for ${String(value)}`, () => assert.equal(eligible({ GH_AW_ENABLE_ISSUE_INVESTIGATION: value }, event), false));
  await test("explicit opt-in", () => assert.equal(eligible({ GH_AW_ENABLE_ISSUE_INVESTIGATION: "true" }, event), true));
  await test("opt-in cannot override failed parent", () => assert.equal(eligible({ GH_AW_ENABLE_ISSUE_INVESTIGATION: "true" },
    { ...event, event: { ...event.event, workflow_run: { ...run, conclusion: "failure" } } }), false));
  const detection = { prompt_injection: false, secret_leak: false, malicious_patch: false, reasons: [], warnings: [] };
  await test("explicit clean detection", () => assert.doesNotThrow(() => assertSafeDetection(detection)));
  for (const flag of ["prompt_injection", "secret_leak", "malicious_patch"])
    for (const value of [true, "false", undefined, null, 0])
      await test(`detection ${flag} ${String(value)}`, () => assert.throws(() => assertSafeDetection({ ...detection, [flag]: value }), /safe verdict/));
  for (const change of [{ warnings: ["Incomplete analysis"] }, { reasons: null }, { warnings: null }])
    await test(`invalid detection ${JSON.stringify(change)}`, () => assert.throws(() => assertSafeDetection({ ...detection, ...change }), /safe verdict/));
  console.log(JSON.stringify({ suite: "Independent triage relay contracts passed", count: passed.length, cases: passed }));
}

main().catch(error => { console.error(error); process.exitCode = 1; });
