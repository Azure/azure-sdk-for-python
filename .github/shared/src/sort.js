/**
 * Returns a comparator that compares values by a date string in ascending order.
 * Throws if the value returned by getDate() is null, undefined, or cannot be
 * parsed as a date.
 *
 * @template T
 * @param {(item: T) => string} getDate
 * @returns {(a: T, b: T) => number}
 */
export function byDate(getDate) {
  return (a, b) => {
    // Sort ascending to match JS default
    return parseDate(getDate(a)) - parseDate(getDate(b));
  };
}

/**
 * Parses a string to a date, throwing if null, undefined, or cannot be parsed.
 *
 * @param {string} s
 * @returns {number}
 */
function parseDate(s) {
  // Date.parse() returns NaN for null, undefined, or strings that cannot be parsed.
  const parsed = Date.parse(s);

  if (Number.isNaN(parsed)) {
    throw new Error(`Unable to parse '${s}' to a valid date`);
  }

  return parsed;
}

/**
 * Inverts a comparator function.
 *
 * @template T
 * @param {(a: T, b: T) => number} comparator
 * @returns {(a: T, b: T) => number}
 */
export function invert(comparator) {
  return (a, b) => -comparator(a, b);
}
