[![NPM Version](https://img.shields.io/npm/v/eslint-plugin-mocha.svg?style=flat)](https://www.npmjs.org/package/eslint-plugin-mocha)
[![GitHub Actions status](https://github.com/lo1tuma/eslint-plugin-mocha/workflows/CI/badge.svg)](https://github.com/lo1tuma/eslint-plugin-mocha/actions)
[![Coverage Status](https://img.shields.io/coveralls/lo1tuma/eslint-plugin-mocha/master.svg?style=flat)](https://coveralls.io/r/lo1tuma/eslint-plugin-mocha)
[![NPM Downloads](https://img.shields.io/npm/dm/eslint-plugin-mocha.svg?style=flat)](https://www.npmjs.org/package/eslint-plugin-mocha)

# eslint-plugin-mocha

ESLint rules for [mocha](http://mochajs.org/).

## Install and configure

This plugin requires ESLint `4.0.0` or later.

```bash
npm install --save-dev eslint-plugin-mocha
```

Then add a reference to this plugin and selected rules in your eslint config:

```json
{
    "plugins": [
        "mocha"
    ]
}
```

### Plugin Settings

This plugin supports the following settings, which are used by multiple rules:

* `additionalCustomNames`: This allows rules to check additional function names when looking for suites or test cases. This might be used with a custom Mocha extension, such as [`ember-mocha`](https://github.com/switchfly/ember-mocha)
**Example:**

```json
{
    "rules": {
        "mocha/no-skipped-tests": "error",
        "mocha/no-exclusive-tests": "error"
    },
    "settings": {
        "mocha/additionalCustomNames": [
            { "name": "describeModule", "type": "suite", "interfaces": [ "BDD" ] },
            { "name": "testModule", "type": "testCase", "interfaces": [ "TDD" ] }
        ]
    }
}
```

### Recommended config

This plugin exports a recommended config that enforces good practices.

Enable it with the extends option:

```json
{
    "extends": [
        "plugin:mocha/recommended"
    ]
}
```

See [Configuring Eslint](http://eslint.org/docs/user-guide/configuring) on [eslint.org](http://eslint.org) for more info.

## Rules documentation

The documentation of the rules [can be found here](docs/rules).
