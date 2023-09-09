'use strict';
const simpleArraySearchRule = require('./shared/simple-array-search-rule.js');

const indexOfOverFindIndexRule = simpleArraySearchRule({
	method: 'findIndex',
	replacement: 'indexOf',
});

const lastIndexOfOverFindLastIndexRule = simpleArraySearchRule({
	method: 'findLastIndex',
	replacement: 'lastIndexOf',
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create: context => ({
		...indexOfOverFindIndexRule.createListeners(context),
		...lastIndexOfOverFindLastIndexRule.createListeners(context),
	}),
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Prefer `Array#{indexOf,lastIndexOf}()` over `Array#{findIndex,findLastIndex}()` when looking for the index of an item.',
		},
		fixable: 'code',
		hasSuggestions: true,
		messages: {
			...indexOfOverFindIndexRule.messages,
			...lastIndexOfOverFindLastIndexRule.messages,
		},
	},
};
