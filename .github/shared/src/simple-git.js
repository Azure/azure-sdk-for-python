import { resolve } from "path";
import { simpleGit } from "simple-git";

/**
 *
 * @param {string} inputPath
 * @returns {Promise<string>}
 */
export async function getRootFolder(inputPath) {
  // expecting users to handle the case where inputPath is not a git repo
  const gitRoot = await simpleGit(inputPath).revparse("--show-toplevel");
  return resolve(gitRoot.trim());
}
