import { resolve } from "path";
import { Bench } from "tinybench";
import { resolveCached } from "../src/path.js";

const bench = new Bench({ name: "github shared", time: 100 });

// ┌─────────┬───────────────────┬──────────────────┬──────────────────┬────────────────────────┬────────────────────────┬─────────┐
// │ (index) │ Task name         │ Latency avg (ns) │ Latency med (ns) │ Throughput avg (ops/s) │ Throughput med (ops/s) │ Samples │
// ├─────────┼───────────────────┼──────────────────┼──────────────────┼────────────────────────┼────────────────────────┼─────────┤
// │ 0       │ 'resolve()'       │ '592.71 ± 1.66%' │ '500.00 ± 0.00'  │ '1836985 ± 0.06%'      │ '2000000 ± 0'          │ 168717  │
// │ 1       │ 'resolveCached()' │ '51.48 ± 0.79%'  │ '0.00 ± 0.00'    │ '14810488 ± 0.04%'     │ '19423802 ± 0'         │ 1942381 │
// └─────────┴───────────────────┴──────────────────┴──────────────────┴────────────────────────┴────────────────────────┴─────────┘

bench.add("resolve()", () => resolve("bar")).add("resolveCached()", () => resolveCached("bar"));

await bench.run();

console.log(bench.name);
console.table(bench.table());
