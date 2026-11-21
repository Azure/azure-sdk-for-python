// cspell:ignore ffeb
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { script, condition } = JSON.parse(fs.readFileSync(0, "utf8"));
const runtime = process.env.GH_AW_RUNTIME;
assert.ok(runtime, "The pinned native runtime is required");
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const execute = new AsyncFunction("require", "core", "github", "context", "exec", "io", "getOctokit", script);
const confirmFails = new Function("steps", "return !!(" + condition + ")");
const labels = [{ name: "customer-reported", color: "3800e0" }, { name: "KeyVault", color: "e99695" }, { name: "Client", color: "ffeb77" }];
const issue = { number: 42, state: "open", locked: false, labels, assignees: [{ login: "owner" }], url: "https://api.github.com/repos/example/sdk/issues/42" };
const passed = [];

async function scenario(name, changes = {}) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "relay-contract-"));
  const saved = { ...process.env };
  const outputs = {};
  const writes = [];
  const core = Object.fromEntries(["debug", "info", "notice", "warning", "error"].map(key => [key, () => {}]));
  core.setOutput = (key, value) => { outputs[key] = String(value); };
  const context = { repo: { owner: "example", repo: "sdk" }, eventName: "workflow_run",
    ref: "refs/heads/main", serverUrl: "https://github.com", payload: { repository: { default_branch: "main" } } };
  const github = { hook: { before() {} }, rest: {
    actions: {
      getWorkflowRun: async request => {
        assert.equal(request.run_id, 100);
        return { data: { status: "completed", conclusion: "success", run_attempt: changes.rerun ? 2 : 1 } };
      },
      createWorkflowDispatch: async request => {
        if (changes.dispatchError) throw new Error("Dispatch API unavailable");
        writes.push(request);
        return { data: { workflow_run_id: 200 } };
      },
    },
    issues: {
      get: async request => { assert.equal(request.issue_number, 42); return { data: { ...issue, ...(changes.issue ?? {}) } }; },
      getComment: async () => ({ data: { issue_url: issue.url,
        body: changes.wrongComment ? "Routing only" : "## Agentic Issue Triage\n\nAnalysis" } }),
    },
  } };
  const data = {
    "triage-detection/detection_result.json": {
      prompt_injection: false, secret_leak: false, malicious_patch: false, reasons: [],
      warnings: changes.warning ? ["uncertain"] : [],
    },
    "triage-requests/agent_output.json": {
      items: [{ type: "assign_to_user", issue_number: 42, assignee: "owner" }], errors: changes.incomplete ? ["failed"] : [],
    },
  };
  try {
    process.env.RUNNER_TEMP = temp;
    process.env.GITHUB_WORKSPACE = temp;
    process.env.TRIAGE_EVENT = "issues";
    process.env.TRIAGE_ISSUE_NUMBER = "42";
    process.env.TRIAGE_RUN_ID = "100";
    process.env.TRIAGE_RUN_ATTEMPT = "1";
    process.env.TRIAGE_OWNER_NOTIFICATION = "skipped";
    process.env.GH_AW_DETECTION_CONCLUSION = "success";
    delete process.env.GH_AW_SAFE_OUTPUTS_STAGED;
    const helperDirectory = path.join(temp, "triage-handoff", ".github", "workflows", "scripts");
    fs.mkdirSync(helperDirectory, { recursive: true });
    fs.cpSync(path.join(__dirname, "..", "scripts"), helperDirectory, { recursive: true });
    for (const [name, value] of Object.entries(data)) {
      const file = path.join(temp, ...name.split("/"));
      fs.mkdirSync(path.dirname(file), { recursive: true });
      fs.writeFileSync(file, JSON.stringify(value));
    }
    const receipts = changes.staged ? [] : [
      { type: "assign_to_user" },
      { type: "add_comment", url: "https://github.com/example/sdk/issues/42#issuecomment-99" },
    ];
    fs.mkdirSync(path.join(temp, "triage-receipts"));
    fs.writeFileSync(path.join(temp, "triage-receipts", "safe-output-items.jsonl"), receipts.map(item => JSON.stringify(item)).join("\n"));
    const proxyRequire = name => {
      if (name === path.join(temp, "gh-aw", "actions", "constants.cjs")) {
        return { MANIFEST_FILE_PATH: path.join(temp, "manifest.jsonl") };
      }
      if (name === path.join(temp, "gh-aw", "actions", "process_safe_outputs.cjs")) {
        return { main: async () => {
          const envelope = JSON.parse(fs.readFileSync(process.env.GH_AW_AGENT_OUTPUT, "utf8"));
          const config = JSON.parse(process.env.GH_AW_SAFE_OUTPUTS_HANDLER_CONFIG);
          assert.deepEqual(Object.keys(config), ["dispatch_workflow"]);
          assert.equal(envelope.items.length, 1);
          const handler = await require(path.join(runtime, "dispatch_workflow.cjs")).main(config.dispatch_workflow);
          const result = await handler(envelope.items[0], {});
          const { computeSafeOutputsStatus } = require(path.join(runtime, "safe_outputs_status.cjs"));
          const status = computeSafeOutputsStatus([{ success: result.success, result }]);
          core.setOutput("status", status.status);
          core.setOutput("items_applied", status.itemsApplied);
        } };
      }
      if (name.startsWith(path.join(temp, "gh-aw", "actions") + path.sep)) return require(path.join(runtime, path.basename(name)));
      return require(name);
    };
    if (changes.throws) {
      await assert.rejects(execute(proxyRequire, core, github, context, {}, {}, () => github), changes.throws);
      assert.equal(writes.length, 0);
    } else {
      await execute(proxyRequire, core, github, context, {}, {}, () => github);
      if (changes.noDispatch || changes.dispatchError) {
        assert.equal(writes.length, 0);
      } else {
        assert.equal(writes.length, 1);
        const write = writes[0];
        assert.equal(write.owner, "example");
        assert.equal(write.repo, "sdk");
        assert.equal(write.workflow_id, "issue-investigation.lock.yml");
        assert.equal(write.ref, "refs/heads/main");
        assert.equal(write.inputs.issue_number, "42");
      }
      assert.equal(confirmFails({ handoff: { outputs } }), !!changes.dispatchError);
    }
    passed.push(name);
  } finally {
    for (const key of Object.keys(process.env)) if (!(key in saved)) delete process.env[key];
    Object.assign(process.env, saved);
    fs.rmSync(temp, { recursive: true, force: true });
  }
}
(async () => {
  await scenario("actual relay script and pinned dispatcher: clean single-owner route");
  await scenario("rerun starts during artifact validation", { rerun: true, noDispatch: true });
  await scenario("staged run has no applied receipts", { staged: true, noDispatch: true });
  await scenario("closed issue after completion", { issue: { state: "closed" }, noDispatch: true });
  await scenario("manual triage label added after completion", { issue: { labels: [...labels, { name: "needs-triage", color: "ffffff" }] }, noDispatch: true });
  await scenario("detection warning blocks handoff", { warning: true, throws: /safe verdict/ });
  await scenario("incomplete agent output blocks handoff", { incomplete: true, throws: /terminal/ });
  await scenario("applied routing comment is not analysis", { wrongComment: true, throws: /analysis comment/ });
  await scenario("dispatch API failure surfaces through confirmation", { dispatchError: true });
  console.log(JSON.stringify({ suite: "Relay integration cases passed", count: passed.length, cases: passed }));
})().catch(error => { console.error(error); process.exitCode = 1; });
