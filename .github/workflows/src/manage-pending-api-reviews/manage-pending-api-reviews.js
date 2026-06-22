#!/usr/bin/env node

const { execFileSync } = require("child_process");
const fs = require("fs");

const DEFAULT_METADATA_MARKER = "api-md-review-sync";
const DEFAULT_PENDING_REVIEWS_FIELD = "Custom.PendingAPIReviews";
const METADATA_WARNING = "DO NOT MODIFY THESE CONTENTS!";

function log(message) {
  console.log(message);
}

function warn(message) {
  console.warn(message);
}

// cSpell:ignore FEFF
function runAzsdkCli(args) {
  const cli = process.env.AZSDK_CLI || "azsdk";
  log(`$ ${[cli, ...args].join(" ")}`);
  return execFileSync(cli, args, {
    encoding: "utf-8",
    shell: process.platform === "win32" && /\.(cmd|bat)$/i.test(cli),
    stdio: ["ignore", "pipe", "pipe"],
  });
}

function parseJson(text, description) {
  try {
    return JSON.parse(text.replace(/^\uFEFF/, ""));
  } catch (error) {
    throw new Error(`Failed to parse ${description}: ${error.message}`);
  }
}

function parseEvent() {
  const eventPath = process.env.API_REVIEW_EVENT_PATH || process.env.GITHUB_EVENT_PATH;
  if (!eventPath) {
    throw new Error("GITHUB_EVENT_PATH is required when API_REVIEW_EVENT_PATH is not set.");
  }

  return parseJson(fs.readFileSync(eventPath, "utf-8"), eventPath);
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function parseSyncMetadata(body, marker = DEFAULT_METADATA_MARKER) {
  const pattern = new RegExp(
    `<!--\\s*${escapeRegExp(marker)}\\s*\\n([\\s\\S]*?)\\n-->`,
    "m"
  );
  const match = pattern.exec(body || "");
  if (!match) {
    return null;
  }

  const jsonText = match[1]
    .split(/\r?\n/)
    .filter((line) => line.trim() !== METADATA_WARNING)
    .join("\n")
    .trim();

  const metadata = parseJson(jsonText, `${marker} metadata block`);
  if (!metadata || typeof metadata !== "object" || Array.isArray(metadata)) {
    throw new Error(`${marker} metadata block must contain a JSON object.`);
  }
  return metadata;
}

function normalizeUrlList(value) {
  if (!value) {
    return [];
  }

  const seen = new Set();
  const urls = [];
  for (const line of String(value).split(/\r?\n/)) {
    const url = line.trim();
    if (!url || seen.has(url)) {
      continue;
    }
    seen.add(url);
    urls.push(url);
  }
  return urls;
}

function getPackageWorkItem(metadata) {
  const rawWorkItemId = metadata.packageWorkItemId;
  if (rawWorkItemId === undefined || rawWorkItemId === null || rawWorkItemId === "" || rawWorkItemId === "ERROR") {
    return null;
  }

  const parsedWorkItemId = Number(rawWorkItemId);
  if (!Number.isInteger(parsedWorkItemId)) {
    throw new Error(`Invalid packageWorkItemId in API review metadata: ${rawWorkItemId}`);
  }

  return parseJson(
    runAzsdkCli(["package", "get-work-item", "--work-item-id", String(parsedWorkItemId), "-o", "json"]),
    `package work item ${parsedWorkItemId}`
  );
}

function workItemId(workItem) {
  const id = Number(workItem?.id);
  if (!Number.isInteger(id)) {
    throw new Error("Package work item response did not contain an integer id.");
  }
  return id;
}

function pendingReviewUrls(workItem, fieldName) {
  return normalizeUrlList(workItem?.fields?.[fieldName]);
}

function updatePendingReviews(workItem, fieldName, urls) {
  runAzsdkCli([
    "package",
    "update-work-item",
    "--work-item-id",
    String(workItemId(workItem)),
    "--field",
    `${fieldName}=${urls.join("\n")}`,
    "--multiline-fields-format",
    `${fieldName}=markdown`,
  ]);
}

function updatedUrlsForAction(action, urls, prUrl) {
  if (action === "opened" || action === "reopened") {
    return urls.includes(prUrl) ? urls : [...urls, prUrl];
  }

  if (action === "closed") {
    return urls.filter((url) => url !== prUrl);
  }

  throw new Error(`Unsupported pull request action: ${action}`);
}

function isReviewPullRequest(pullRequest, marker = DEFAULT_METADATA_MARKER) {
  return Boolean(
    parseSyncMetadata(pullRequest.body || "", marker) ||
      pullRequest.title?.startsWith("[API Review]") ||
      pullRequest.head?.ref?.startsWith("apireview/review")
  );
}

function main() {
  const event = parseEvent();
  const action = process.env.API_REVIEW_PR_ACTION || event.action;
  const pullRequest = event.pull_request;
  const fieldName = process.env.PENDING_API_REVIEWS_FIELD || DEFAULT_PENDING_REVIEWS_FIELD;
  const marker = process.env.API_REVIEW_METADATA_MARKER || DEFAULT_METADATA_MARKER;

  if (!pullRequest) {
    warn("Event does not contain a pull_request payload; skipping.");
    return;
  }

  if (action !== "opened" && action !== "closed" && action !== "reopened") {
    warn(`Pull request action ${action} does not affect pending API reviews; skipping.`);
    return;
  }

  if (!isReviewPullRequest(pullRequest, marker)) {
    warn("Pull request does not look like an API review PR; skipping.");
    return;
  }

  const metadata = parseSyncMetadata(pullRequest.body || "", marker);
  if (!metadata) {
    warn(`Pull request does not contain ${marker} metadata; skipping package work item update.`);
    return;
  }

  const prUrl = process.env.API_REVIEW_PR_URL || pullRequest.html_url;
  if (!prUrl) {
    throw new Error("Pull request URL is required.");
  }

  const workItem = getPackageWorkItem(metadata);
  if (!workItem) {
    warn("API review metadata does not contain a packageWorkItemId; skipping package work item update.");
    return;
  }

  const existingUrls = pendingReviewUrls(workItem, fieldName);
  const nextUrls = updatedUrlsForAction(action, existingUrls, prUrl);

  if (nextUrls.join("\n") === existingUrls.join("\n")) {
    log(`Package work item ${workItemId(workItem)} already has desired ${fieldName} value.`);
    return;
  }

  updatePendingReviews(workItem, fieldName, nextUrls);
  log(`Updated package work item ${workItemId(workItem)} ${fieldName} for PR ${prUrl}.`);
}

main();
