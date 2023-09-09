'use strict';
const {isEmptyNode} = require('./ast/index.js');

const MESSAGE_ID = 'no-empty-file';
const messages = {
	[MESSAGE_ID]: 'Empty files are not allowed.',
};

const isDirective = node => node.type === 'ExpressionStatement' && 'directive' in node;
const isEmpty = node => isEmptyNode(node, isDirective);

const isTripleSlashDirective = node =>
	node.type === 'Line' && node.value.startsWith('/');

const hasTripeSlashDirectives = comments =>
	comments.some(currentNode => isTripleSlashDirective(currentNode));

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const filename = context.getPhysicalFilename();

	if (!/\.(?:js|mjs|cjs|jsx|ts|mts|cts|tsx)$/i.test(filename)) {
		return;
	}

	return {
		Program(node) {
			if (node.body.some(node => !isEmpty(node))) {
				return;
			}

			const sourceCode = context.getSourceCode();
			const comments = sourceCode.getAllComments();

			if (hasTripeSlashDirectives(comments)) {
				return;
			}

			return {
				node,
				messageId: MESSAGE_ID,
			};
		},
	};
};

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Disallow empty files.',
		},
		messages,
	},
};
