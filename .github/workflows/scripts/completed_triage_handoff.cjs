const { positiveInteger } = require("./issue_workflow_support.cjs");

async function selectCompletedTriage({ github, context }) {
  const candidate = context.payload.workflow_run;
  const number = positiveInteger(candidate?.id, "Triage run ID");
  const { data: run } = await github.rest.actions.getWorkflowRun({ ...context.repo, run_id: number });
  const repository = `${context.repo.owner}/${context.repo.repo}`;
  if (run.status !== "completed" || run.conclusion !== "success" ||
      run.head_repository?.full_name?.toLowerCase() !== repository.toLowerCase() ||
      run.head_branch !== context.payload.repository.default_branch ||
      !["issues", "workflow_dispatch"].includes(run.event) || run.run_attempt !== candidate.run_attempt) {
    return { reason: "not a current successful default-branch triage run" };
  }
  const { data: workflow } = await github.rest.actions.getWorkflow({
    ...context.repo, workflow_id: "issue-triage.lock.yml",
  });
  if (run.workflow_id !== workflow.id || workflow.path !== ".github/workflows/issue-triage.lock.yml") {
    throw new Error("The completed workflow is not the registered triage workflow");
  }
  const jobs = await github.paginate(github.rest.actions.listJobsForWorkflowRun, {
    ...context.repo, run_id: number, filter: "latest", per_page: 100,
  });
  for (const name of ["activation", "agent", "detection", "safe_outputs", "conclusion"]) {
    const matching = jobs.filter(job => job.name === name);
    if (matching.length !== 1 || matching[0].conclusion !== "success") {
      return { reason: `triage job ${name} did not complete successfully` };
    }
  }
  const owners = jobs.filter(job => job.name === "mention_owners");
  if (owners.length !== 1 || !["success", "skipped"].includes(owners[0].conclusion)) {
    return { reason: "owner routing did not complete successfully" };
  }
  const artifacts = await github.paginate(github.rest.actions.listWorkflowRunArtifacts, {
    ...context.repo, run_id: number, per_page: 100,
  });
  const usable = artifacts.filter(artifact => !artifact.expired &&
    Date.parse(artifact.created_at) >= Date.parse(run.run_started_at));
  function artifactId(name) {
    const matching = usable.filter(artifact => artifact.name === name)
      .sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at));
    if (matching.length === 0) throw new Error(`Missing current triage artifact: ${name}`);
    return positiveInteger(matching[0].id, "Artifact ID");
  }
  const requestName = usable.some(artifact => artifact.name === "agent-output-fallback")
    ? "agent-output-fallback" : "agent";
  return {
    runId: number, event: run.event, ownerNotification: owners[0].conclusion,
    activationId: artifactId("activation"), receiptId: artifactId("safe-outputs-items"), detectionId: artifactId("detection"),
    requestId: artifactId(requestName),
  };
}

function parseTriageIssue(prompt) {
  // This artifact is published by activation before the agent runs. Read only
  // the trusted workflow introduction, never issue text or agent-produced targets.
  const systemEnd = prompt.indexOf("</system>");
  const introduction = prompt.slice(systemEnd + "</system>".length).trimStart();
  const match = introduction.match(/^# Agentic Triage\s+<!--[^]*?-->\s+You are a triage assistant for GitHub issues in the Azure SDK for Python repository\s+Your task is to analyze issue #([^\r\n]+?) and perform initial triage following the decision flow below/);
  if (!prompt.startsWith("<system>") || systemEnd < 0 || !match) {
    throw new Error("Trusted triage introduction is missing or changed");
  }
  return positiveInteger(match[1], "Triage issue number");
}

function assertSafeDetection(result) {
  if (!result || ["prompt_injection", "secret_leak", "malicious_patch"].some(name => result[name] !== false) ||
      !Array.isArray(result.reasons) || !Array.isArray(result.warnings) || result.warnings.length !== 0) {
    throw new Error("Triage detection did not produce an explicit safe verdict");
  }
}

module.exports = { selectCompletedTriage, parseTriageIssue, assertSafeDetection };
