import { readdir } from "fs/promises";
import { basename, join, normalize, sep } from "path";
import { pathToFileURL } from "url";
import { inspect } from "util";

/**
 * @param {import('@actions/github-script').AsyncFunctionArguments} AsyncFunctionArguments
 */
export default async function importAllModules({ core }) {
  const workspace = process.env.GITHUB_WORKSPACE;
  if (!workspace) {
    throw new Error("Env var GITHUB_WORKSPACE must be set");
  }

  const githubDir = join(workspace, ".github");

  // find all files matching "**/src/**/*.js", sorted for readability
  const scriptFiles = (await readdir(githubDir, { recursive: true }))
    .filter((f) => normalize(f).split(sep).includes("src") && basename(f).endsWith(".js"))
    .sort();

  core.info("Script Files:");
  scriptFiles.map(core.info);
  core.info("");

  for (const file of scriptFiles) {
    core.info(`Importing ${file}`);

    const fullPath = join(githubDir, file);
    const fileUrl = pathToFileURL(fullPath).href;

    // if import fails, throws error which causes step to fail
    const module = /** @type {unknown} */ (await import(fileUrl));

    core.info(inspect(module));
    core.info("");
  }

  core.info("All script files are importable");
}
