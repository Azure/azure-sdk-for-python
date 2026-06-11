# .github/src

## Overview

Helper functions intended for use by any JavaScript, TypeScript, or other code (using a wrapper
that shells to nodejs) in this repo.

## Calling from TypeScript

You may need to enable `allowJs` in `tsconfig.json`:

```
{
  "compilerOptions": {
    "allowJs": true
  }
}
```

https://www.typescriptlang.org/tsconfig/#allowJs

Another issue may be missing type definitions, but all shared code should be annotated with JSDoc
comments, which TypeScript should use to infer types.
