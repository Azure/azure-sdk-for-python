'use strict';
const {isIdentifierName} = require('@babel/helper-validator-identifier');
const escapeString = require('./utils/escape-string.js');
const {methodCallSelector, matches} = require('./selectors/index.js');

const MESSAGE_ID = 'prefer-dom-node-dataset';
const messages = {
	[MESSAGE_ID]: 'Prefer `.dataset` over `{{method}}(…)`.',
};

const selector = [
	matches([
		methodCallSelector({method: 'setAttribute', argumentsLength: 2}),
		methodCallSelector({methods: ['getAttribute', 'removeAttribute', 'hasAttribute'], argumentsLength: 1}),
	]),
	'[arguments.0.type="Literal"]',
].join('');

const dashToCamelCase = string => string.replace(/-[a-z]/g, s => s[1].toUpperCase());

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => ({
	[selector](node) {
		const [nameNode] = node.arguments;
		let attributeName = nameNode.value;

		if (typeof attributeName !== 'string') {
			return;
		}

		attributeName = attributeName.toLowerCase();

		if (!attributeName.startsWith('data-')) {
			return;
		}

		const method = node.callee.property.name;
		const name = dashToCamelCase(attributeName.slice(5));

		const sourceCode = context.getSourceCode();
		let text = '';
		const datasetText = `${sourceCode.getText(node.callee.object)}.dataset`;
		switch (method) {
			case 'setAttribute':
			case 'getAttribute':
			case 'removeAttribute': {
				text = isIdentifierName(name) ? `.${name}` : `[${escapeString(name, nameNode.raw.charAt(0))}]`;
				text = `${datasetText}${text}`;
				if (method === 'setAttribute') {
					text += ` = ${sourceCode.getText(node.arguments[1])}`;
				} else if (method === 'removeAttribute') {
					text = `delete ${text}`;
				}

				/*
				For non-exists attribute, `element.getAttribute('data-foo')` returns `null`,
				but `element.dataset.foo` returns `undefined`, switch to suggestions if necessary
				*/
				break;
			}

			case 'hasAttribute': {
				text = `Object.hasOwn(${datasetText}, ${escapeString(name, nameNode.raw.charAt(0))})`;
				break;
			}
			// No default
		}

		return {
			node,
			messageId: MESSAGE_ID,
			data: {method},
			fix: fixer => fixer.replaceText(node, text),
		};
	},
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Prefer using `.dataset` on DOM elements over calling attribute methods.',
		},
		fixable: 'code',
		messages,
	},
};
