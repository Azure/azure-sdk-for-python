/**
 * @param {Set<any>} set1
 * @param {Set<any>} set2
 * @returns {boolean} True if sets are the same size and have the same elements
 */
export function equals(set1, set2) {
  if (!(set1 instanceof Set) || !(set2 instanceof Set)) {
    return false;
  }

  if (set1.size !== set2.size) {
    return false;
  }

  // Should be O(N), since set lookup should be O(1)
  // Sets are same size, so iterating over either set has the same perf
  for (const item of set1) {
    if (!set2.has(item)) {
      return false;
    }
  }

  return true;
}

/**
 * @template T
 * @param {Set<T>} a
 * @param {Set<T>} b
 * @returns {Set<T>}
 */
export function intersect(a, b) {
  // Since set lookup is O(1), iterate over the smaller set for better perf: O(small) vs O(large)
  const [small, large] = a.size < b.size ? [a, b] : [b, a];
  return new Set([...small].filter((value) => large.has(value)));
}
