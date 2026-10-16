// cspell:ignore feff
const { positiveInteger } = require("./issue_workflow_support.cjs");

async function selectCompletedTriage({ github, context }) {
  const candidate = context.payload.workflow_run;
  const runId = positiveInteger(candidate?.id, "Triage run ID");
  const attempt = positiveInteger(candidate?.run_attempt, "Triage run attempt");
  const { data: run } = await github.rest.actions.getWorkflowRun({ ...context.repo, run_id: runId });
  const repository = `${context.repo.owner}/${context.repo.repo}`;
  if (run.id !== runId || run.status !== "completed" || run.conclusion !== "success" ||
      run.head_repository?.full_name?.toLowerCase() !== repository.toLowerCase() ||
      run.head_branch !== context.payload.repository.default_branch ||
      !["issues", "workflow_dispatch"].includes(run.event) || run.run_attempt !== attempt) {
    return { reason: "not a current successful default-branch triage run" };
  }
  const { data: workflow } = await github.rest.actions.getWorkflow({
    ...context.repo, workflow_id: "issue-triage.lock.yml",
  });
  if (run.workflow_id !== workflow.id || workflow.path !== ".github/workflows/issue-triage.lock.yml") {
    throw new Error("The completed workflow is not the registered triage workflow");
  }
  const jobs = await github.paginate(github.rest.actions.listJobsForWorkflowRunAttempt, {
    ...context.repo, run_id: runId, attempt_number: attempt, per_page: 100,
  });
  for (const name of ["activation", "agent", "detection", "safe_outputs", "conclusion"]) {
    const matching = jobs.filter(job => job.name === name);
    if (matching.length !== 1 || matching[0].conclusion !== "success" || matching[0].run_attempt !== attempt) {
      return { reason: `triage job ${name} did not complete successfully in this attempt` };
    }
  }
  const owners = jobs.filter(job => job.name === "mention_owners");
  if (owners.length !== 1 || owners[0].run_attempt !== attempt ||
      !["success", "skipped"].includes(owners[0].conclusion)) {
    return { reason: "owner routing did not complete successfully" };
  }
  const artifacts = await github.paginate(github.rest.actions.listWorkflowRunArtifacts, {
    ...context.repo, run_id: runId, per_page: 100,
  });
  const startedAt = Date.parse(run.run_started_at);
  if (!Number.isFinite(startedAt)) throw new Error("Invalid triage run start time");
  const usable = artifacts.filter(artifact => artifact.expired === false &&
    Date.parse(artifact.created_at) >= startedAt);
  function artifactId(name) {
    const matching = usable.filter(artifact => artifact.name === name);
    if (matching.length !== 1) throw new Error(`Expected one current triage artifact: ${name}`);
    return positiveInteger(matching[0].id, "Artifact ID");
  }
  const activation = jobs.find(job => job.name === "activation");
  // Completed runs can discard activation artifacts. The activation job's
  // logged context is produced before the agent, unlike agent-owned artifacts.
  const { data: activationLog } = await github.request(
    "GET /repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
    { ...context.repo, job_id: positiveInteger(activation.id, "Activation job ID") }
  );
  const issueNumber = parseTriageIssue(activationLog, run.event);
  const requestName = usable.some(artifact => artifact.name === "agent-output-fallback")
    ? "agent-output-fallback" : "agent";
  return {
    runId, attempt, issueNumber, event: run.event, ownerNotification: owners[0].conclusion,
    receiptId: artifactId("safe-outputs-items"), detectionId: artifactId("detection"),
    requestId: artifactId(requestName),
  };
}

function parseTriageIssue(log, event) {
  if (typeof log !== "string" || log.length > 8 * 1024 * 1024) {
    throw new Error("Activation log is missing or exceeds the supported size");
  }
  const field = event === "issues" ? "GH_AW_GITHUB_EVENT_ISSUE_NUMBER"
    : event === "workflow_dispatch" ? "GH_AW_GITHUB_EVENT_INPUTS_ISSUE_NUMBER" : null;
  if (!field) throw new Error("Unsupported triage trigger");
  const expression = new RegExp(`^\\uFEFF?\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d+Z {3}${field}: ([^\\r\\n]*)\\r?$`, "gm");
  const numbers = [...log.matchAll(expression)].map(match => positiveInteger(match[1], "Triage issue number"));
  const introduction = /^\uFEFF?\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z Your task is to analyze issue #([^\r\n]+?) and perform initial triage following the decision flow below\r?$/gm;
  const promptNumbers = [...log.matchAll(introduction)].map(match => positiveInteger(match[1], "Prompt issue number"));
  if (numbers.length === 0 || promptNumbers.length === 0 || new Set([...numbers, ...promptNumbers]).size !== 1) {
    throw new Error("Activation issue context is missing or inconsistent");
  }
  return numbers[0];
}

function assertSafeDetection(result) {
  if (!result || ["prompt_injection", "secret_leak", "malicious_patch"].some(name => result[name] !== false) ||
      !Array.isArray(result.reasons) || !Array.isArray(result.warnings) || result.warnings.length !== 0) {
    throw new Error("Triage detection did not produce an explicit safe verdict");
  }
}

module.exports = { selectCompletedTriage, parseTriageIssue, assertSafeDetection };
