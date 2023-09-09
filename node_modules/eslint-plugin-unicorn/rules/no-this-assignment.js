'use strict';
const {matches} = require('./selectors/index.js');

const MESSAGE_ID = 'no-this-assignment';
const messages = {
	[MESSAGE_ID]: 'Do not assign `this` to `{{name}}`.',
};

const variableDeclaratorSelector = [
	'VariableDeclarator',
	'[init.type="ThisExpression"]',
	'[id.type="Identifier"]',
].join('');

const assignmentExpressionSelector = [
	'AssignmentExpression',
	'[right.type="ThisExpression"]',
	'[left.type="Identifier"]',
].join('');

const selector = matches([variableDeclaratorSelector, assignmentExpressionSelector]);

/** @param {import('eslint').Rule.RuleContext} context */
const create = () => ({
	[selector](node) {
		const variable = node.type === 'AssignmentExpression' ? node.left : node.id;
		return {
			node,
			data: {name: variable.name},
			messageId: MESSAGE_ID,
		};
	},
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Disallow assigning `this` to a variable.',
		},
		messages,
	},
};
