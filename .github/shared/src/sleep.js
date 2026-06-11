/**
 * @param {number} ms Number of milliseconds to sleep
 * @returns {Promise<void>}
 */
export async function sleep(ms) {
  await new Promise((resolve) => setTimeout(resolve, ms));
}
