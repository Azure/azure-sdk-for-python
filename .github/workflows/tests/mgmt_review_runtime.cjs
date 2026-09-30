// Exercise the pinned gh-aw runtime with mocked GitHub writes, never a real PR.
const fs = require("fs");
const path = require("path");
const root = process.env.GH_AW_RUNTIME;
const request = JSON.parse(fs.readFileSync(0, "utf8"));
global.core = Object.fromEntries(
  ["debug", "info", "warning", "error", "setOutput", "setFailed"].map(name => [name, () => {}])
);

async function main() {
  if (request.mode === "preflight-tool") {
    const { parseToolArgs } = require(path.join(root, "mcp_cli_bridge.cjs"));
    const { createPythonHandler } = require(path.join(root, "mcp_handler_python.cjs"));
    const server = { debug() {}, debugError() {} };
    const { args } = parseToolArgs(["."], { request: { type: "string" } }, JSON.stringify(request.arguments));
    return createPythonHandler(server, "review", request.script, 30)(args);
  }
  if (request.mode === "ingest") {
    process.env.GH_AW_VALIDATION_CONFIG = JSON.stringify(request.validation);
    const { validateItem } = require(path.join(root, "safe_output_type_validator.cjs"));
    return validateItem(request.item, request.item.type, 1);
  }
  if (request.mode === "submit") {
    const { parseToolArgs } = require(path.join(root, "mcp_cli_bridge.cjs"));
    const appended = [];
    const server = { debug() {}, debugError() {} };
    const { createHandlers } = require(path.join(root, "safe_outputs_handlers.cjs"));
    const handler = createHandlers(server, item => appended.push(item), {
      add_comment: { max: 1, target: "49107", data_enabled: true, data_schema: request.schema },
    }).addCommentHandler;
    const responses = [];
    for (const submission of request.submissions) {
      try {
        responses.push(await handler(parseToolArgs(["."], {}, JSON.stringify(submission)).args));
      } catch (error) {
        responses.push({ error });
      }
    }
    process.env.GH_AW_VALIDATION_CONFIG = JSON.stringify(request.validation);
    const { validateItem } = require(path.join(root, "safe_output_type_validator.cjs"));
    const ingestion = appended.map((item, index) => validateItem(item, "add_comment", index + 1));
    return { appended, responses, ingestion };
  }
  let comment, writes = 0, hides = 0;
  global.context = {
    eventName: request.eventName || "pull_request_target", runId: 1, serverUrl: "https://github.com",
    repo: { owner: "Azure", repo: "azure-sdk-for-python" },
    payload: request.eventName === "workflow_dispatch" ? { inputs: { pr_number: "49107" } } : { pull_request: { number: 49107 } },
  };
  global.github = {
    graphql: async () => {
      hides++;
      return { minimizeComment: { minimizedComment: { isMinimized: true } } };
    },
    rest: { issues: {
      listComments: async () => ({ data: request.existing ? [
        { id: 122, node_id: "old-comment", body: "<!-- gh-aw-workflow-id: mgmt-sdk-pr-review -->\nExisting useful review" },
      ] : [] }),
      createComment: async params => {
        writes++;
        comment = params;
        return { data: { id: 123, html_url: "https://github.com/Azure/azure-sdk-for-python/pull/49107#issuecomment-123" } };
      },
    } },
  };
  process.env.GH_AW_WORKFLOW_ID = "mgmt-sdk-pr-review";
  process.env.GH_AW_WORKFLOW_NAME = "Management SDK PR Review";
  process.env.GH_AW_PROMPTS_DIR = path.join(root, "..", "md");
  const handlerFile = request.payload.items[0]?.type === "noop" ? "noop_handler.cjs" : "add_comment.cjs";
  const { main: createHandler } = require(path.join(root, handlerFile));
  const handler = await createHandler(request.handlerConfig || { target: "49107", max: 1, hide_older_comments: true, footer: false, discussions: false });
  const result = request.payload.items.length ? await handler(request.payload.items[0]) : null;
  return { result, comment, writes, hides };
}

main().then(result => process.stdout.write(JSON.stringify(result))).catch(error => {
  process.stderr.write(String(error.stack));
  process.exitCode = 1;
});
