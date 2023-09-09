'use strict';
const {methodCallSelector} = require('./selectors/index.js');
const toLocation = require('./utils/to-location.js');
const {isStringLiteral} = require('./ast/index.js');

const MESSAGE_ID = 'no-console-spaces';
const messages = {
	[MESSAGE_ID]: 'Do not use {{position}} space between `console.{{method}}` parameters.',
};

const methods = [
	'log',
	'debug',
	'info',
	'warn',
	'error',
];

const selector = methodCallSelector({
	methods,
	minimumArguments: 1,
	object: 'console',
});

// Find exactly one leading space, allow exactly one space
const hasLeadingSpace = value => value.length > 1 && value.charAt(0) === ' ' && value.charAt(1) !== ' ';

// Find exactly one trailing space, allow exactly one space
const hasTrailingSpace = value => value.length > 1 && value.charAt(value.length - 1) === ' ' && value.charAt(value.length - 2) !== ' ';

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const sourceCode = context.getSourceCode();
	const getProblem = (node, method, position) => {
		const index = position === 'leading'
			? node.range[0] + 1
			: node.range[1] - 2;
		const range = [index, index + 1];

		return {
			loc: toLocation(range, sourceCode),
			messageId: MESSAGE_ID,
			data: {method, position},
			fix: fixer => fixer.removeRange(range),
		};
	};

	return {
		* [selector](node) {
			const method = node.callee.property.name;
			const {arguments: messages} = node;
			const {length} = messages;
			for (const [index, node] of messages.entries()) {
				if (!isStringLiteral(node) && node.type !== 'TemplateLiteral') {
					continue;
				}

				const raw = sourceCode.getText(node).slice(1, -1);

				if (index !== 0 && hasLeadingSpace(raw)) {
					yield getProblem(node, method, 'leading');
				}

				if (index !== length - 1 && hasTrailingSpace(raw)) {
					yield getProblem(node, method, 'trailing');
				}
			}
		},
	};
};

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Do not use leading/trailing space between `console.log` parameters.',
		},
		fixable: 'code',
		messages,
	},
};
