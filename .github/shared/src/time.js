/**
 * @typedef {Object} DurationType
 * @property {number} Millisecond - 1 millisecond
 * @property {number} Second -      1 second in milliseconds
 * @property {number} Minute -      1 minute in milliseconds
 * @property {number} Hour   -      1 hour in milliseconds
 * @property {number} Day    -      1 day in milliseconds
 * @property {number} Week   -      1 week in milliseconds
 */

/**
 * Common time duration constants in milliseconds.
 *
 * @readonly
 * @type {DurationType}
 */
export const Duration = Object.freeze({
  Millisecond: 1,
  Second: 1000,
  Minute: 60 * 1000,
  Hour: 60 * 60 * 1000,
  Day: 24 * 60 * 60 * 1000,
  Week: 7 * 24 * 60 * 60 * 1000,
});

/**
 * Add milliseconds to a date.
 * @param {Date} date
 * @param {number} ms
 * @returns {Date}
 */
export function add(date, ms) {
  return new Date(date.getTime() + ms);
}

/**
 * Formats a duration of milliseconds as hh:mm:ss (always zero-padded).
 *
 * @param {number} ms
 * @returns {string}
 */
export function formatDuration(ms) {
  let totalSeconds = Math.floor(ms / Duration.Second);

  const hours = Math.floor(totalSeconds / 3600);
  totalSeconds %= 3600;

  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;

  const pad = (/** @type {number} */ n) => String(n).padStart(2, "0");

  return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
}

/**
 * Returns the number of milliseconds between two dates (always non-negative)
 *
 * @param {Date} from
 * @param {Date} to
 * @returns {number}
 */
export function getDuration(from, to) {
  return Math.abs(from.getTime() - to.getTime());
}

/**
 * Subtract milliseconds from a date.
 * @param {Date} date
 * @param {number} ms
 * @returns {Date}
 */
export function subtract(date, ms) {
  return new Date(date.getTime() - ms);
}
