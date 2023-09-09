'use strict';

function getBuiltinRule(id) {
	return require('eslint/use-at-your-own-risk').builtinRules.get(id);
}

module.exports = getBuiltinRule;
