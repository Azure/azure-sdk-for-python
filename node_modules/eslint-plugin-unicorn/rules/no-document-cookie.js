'use strict';
const {GlobalReferenceTracker} = require('./utils/global-reference-tracker.js');

const MESSAGE_ID = 'no-document-cookie';
const messages = {
	[MESSAGE_ID]: 'Do not use `document.cookie` directly.',
};

const tracker = new GlobalReferenceTracker({
	object: 'document.cookie',
	filter: ({node}) => node.parent.type === 'AssignmentExpression' && node.parent.left === node,
	handle: ({node}) => ({node, messageId: MESSAGE_ID}),
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create: context => tracker.createListeners(context),
	meta: {
		type: 'problem',
		docs: {
			description: 'Do not use `document.cookie` directly.',
		},
		messages,
	},
};
