/**
 * Convert a float [0,1] to a percentage string.
 *
 * @param {number} value - A number between 0 and 1.
 * @param {number} [decimals=0] - How many decimal places to include. Default: 0
 * @returns {string}
 */
export function toPercent(value, decimals = 0) {
  return `${(value * 100).toFixed(decimals)}%`;
}
