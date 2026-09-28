// Exercise the pinned gh-aw runtime with mocked GitHub writes, never a real PR.
const fs = require("fs");
const path = require("path");
const root = process.env.GH_AW_RUNTIME;
const request = JSON.parse(fs.readFileSync(0, "utf8"));
global.core = Object.fromEntries(
  ["debug", "info", "warning", "error", "setOutput", "setFailed"].map(name => [name, () => {}])
);

async function main() {
  if (request.mode === "ingest") {
    process.env.GH_AW_VALIDATION_CONFIG = JSON.stringify(request.validation);
    const { validateItem } = require(path.join(root, "safe_output_type_validator.cjs"));
    return validateItem(request.item, request.item.type, 1);
  }
  let comment;
  global.context = {
    eventName: "pull_request_target", runId: 1, serverUrl: "https://github.com",
    repo: { owner: "Azure", repo: "azure-sdk-for-python" },
    payload: { pull_request: { number: 49107 } },
  };
  global.github = {
    rest: { issues: {
      listComments: async () => ({ data: [] }),
      createComment: async params => {
        comment = params;
        return { data: { id: 123, html_url: "https://github.com/Azure/azure-sdk-for-python/pull/49107#issuecomment-123" } };
      },
    } },
  };
  process.env.GH_AW_WORKFLOW_ID = "mgmt-sdk-pr-review";
  process.env.GH_AW_WORKFLOW_NAME = "Management SDK PR Review";
  process.env.GH_AW_PROMPTS_DIR = path.join(root, "..", "md");
  const { main: createHandler } = require(path.join(root, "add_comment.cjs"));
  const handler = await createHandler({ target: "49107", max: 1, hide_older_comments: true, footer: false, discussions: false });
  const result = await handler(request.payload.items[0]);
  return { result, comment };
}

main().then(result => process.stdout.write(JSON.stringify(result))).catch(error => {
  process.stderr.write(String(error.stack));
  process.exitCode = 1;
});
