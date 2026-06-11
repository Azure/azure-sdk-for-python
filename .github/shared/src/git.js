/**
 * Returns true if a string is a possible full git SHA (40 hex chars, case insensitive)
 *
 * @param {string} string
 * @returns {boolean}
 */
export function isFullGitSha(string) {
  return /^[0-9a-f]{40}$/i.test(string);
}
