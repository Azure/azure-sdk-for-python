import { defineBaseConfig } from "./eslint.base.config.js";

export default defineBaseConfig({
  // ensures the tsconfig path resolves relative to this file (so cannot be defined in base file)
  // default is process.cwd() when running eslint, which may be incorrect
  tsconfigRootDir: import.meta.dirname,
});
