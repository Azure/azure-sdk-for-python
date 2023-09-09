'use strict';
const {replaceTemplateElement} = require('./fix/index.js');

const MESSAGE_ID = 'no-hex-escape';
const messages = {
	[MESSAGE_ID]: 'Use Unicode escapes instead of hexadecimal escapes.',
};

function checkEscape(context, node, value) {
	const fixedValue = value.replace(/(?<=(?:^|[^\\])(?:\\\\)*\\)x/g, 'u00');

	if (value !== fixedValue) {
		return {
			node,
			messageId: MESSAGE_ID,
			fix: fixer =>
				node.type === 'TemplateElement'
					? replaceTemplateElement(fixer, node, fixedValue)
					: fixer.replaceText(node, fixedValue),
		};
	}
}

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => ({
	Literal(node) {
		if (node.regex || typeof node.value === 'string') {
			return checkEscape(context, node, node.raw);
		}
	},
	TemplateElement: node => checkEscape(context, node, node.value.raw),
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Enforce the use of Unicode escapes instead of hexadecimal escapes.',
		},
		fixable: 'code',
		messages,
	},
};
