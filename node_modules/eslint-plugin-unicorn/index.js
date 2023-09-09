'use strict';
const createDeprecatedRules = require('./rules/utils/create-deprecated-rules.js');
const {loadRules} = require('./rules/utils/rule.js');
const recommendedConfig = require('./configs/recommended.js');
const allRulesEnabledConfig = require('./configs/all.js');

const deprecatedRules = createDeprecatedRules({
	// {ruleId: ReplacementRuleId | ReplacementRuleId[]}, if no replacement, use `{ruleId: []}`
	'import-index': [],
	'no-array-instanceof': 'unicorn/no-instanceof-array',
	'no-fn-reference-in-iterator': 'unicorn/no-array-callback-reference',
	'no-reduce': 'unicorn/no-array-reduce',
	'prefer-dataset': 'unicorn/prefer-dom-node-dataset',
	'prefer-event-key': 'unicorn/prefer-keyboard-event-key',
	'prefer-exponentiation-operator': 'prefer-exponentiation-operator',
	'prefer-flat-map': 'unicorn/prefer-array-flat-map',
	'prefer-node-append': 'unicorn/prefer-dom-node-append',
	'prefer-node-remove': 'unicorn/prefer-dom-node-remove',
	'prefer-object-has-own': 'prefer-object-has-own',
	'prefer-replace-all': 'unicorn/prefer-string-replace-all',
	'prefer-starts-ends-with': 'unicorn/prefer-string-starts-ends-with',
	'prefer-text-content': 'unicorn/prefer-dom-node-text-content',
	'prefer-trim-start-end': 'unicorn/prefer-string-trim-start-end',
	'regex-shorthand': 'unicorn/better-regex',
});

module.exports = {
	rules: {
		...loadRules(),
		...deprecatedRules,
	},
	configs: {
		recommended: recommendedConfig,
		all: allRulesEnabledConfig,
	},
};
