'use strict';
const safeRegex = require('safe-regex');
const {newExpressionSelector} = require('./selectors/index.js');
const {isNewExpression} = require('./ast/index.js');

const MESSAGE_ID = 'no-unsafe-regex';
const messages = {
	[MESSAGE_ID]: 'Unsafe regular expression.',
};

const newRegExpSelector = [
	newExpressionSelector('RegExp'),
	'[arguments.0.type="Literal"]',
].join('');

/** @param {import('eslint').Rule.RuleContext} context */
const create = () => ({
	'Literal[regex]'(node) {
		// Handle regex literal inside RegExp constructor in the other handler
		if (isNewExpression(node.parent, {name: 'RegExp'})) {
			return;
		}

		if (!safeRegex(node.value)) {
			return {
				node,
				messageId: MESSAGE_ID,
			};
		}
	},
	[newRegExpSelector](node) {
		const arguments_ = node.arguments;
		const hasRegExp = arguments_[0].regex;

		let pattern;
		let flags;
		if (hasRegExp) {
			({pattern} = arguments_[0].regex);
			flags = arguments_[1]?.type === 'Literal'
				? arguments_[1].value
				: arguments_[0].regex.flags;
		} else {
			pattern = arguments_[0].value;
			flags = arguments_[1]?.type === 'Literal'
				? arguments_[1].value
				: '';
		}

		if (!safeRegex(`/${pattern}/${flags}`)) {
			return {
				node,
				messageId: MESSAGE_ID,
			};
		}
	},
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'problem',
		docs: {
			description: 'Disallow unsafe regular expressions.',
		},
		messages,
	},
};
