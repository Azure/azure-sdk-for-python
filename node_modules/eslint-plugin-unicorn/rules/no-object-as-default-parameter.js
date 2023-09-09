'use strict';

const MESSAGE_ID_IDENTIFIER = 'identifier';
const MESSAGE_ID_NON_IDENTIFIER = 'non-identifier';
const messages = {
	[MESSAGE_ID_IDENTIFIER]: 'Do not use an object literal as default for parameter `{{parameter}}`.',
	[MESSAGE_ID_NON_IDENTIFIER]: 'Do not use an object literal as default.',
};

const objectParameterSelector = [
	':function > AssignmentPattern.params',
	'[right.type="ObjectExpression"]',
	'[right.properties.length>0]',
].join('');

/** @param {import('eslint').Rule.RuleContext} context */
const create = () => ({
	[objectParameterSelector](node) {
		const {left, right} = node;

		if (left.type === 'Identifier') {
			return {
				node: left,
				messageId: MESSAGE_ID_IDENTIFIER,
				data: {parameter: left.name},
			};
		}

		return {
			node: right,
			messageId: MESSAGE_ID_NON_IDENTIFIER,
		};
	},
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'problem',
		docs: {
			description: 'Disallow the use of objects as default parameters.',
		},
		messages,
	},
};
