'use strict';
const {isEmptyNode} = require('./ast/index.js');
const getSwitchCaseHeadLocation = require('./utils/get-switch-case-head-location.js');

const MESSAGE_ID_ERROR = 'no-useless-switch-case/error';
const MESSAGE_ID_SUGGESTION = 'no-useless-switch-case/suggestion';
const messages = {
	[MESSAGE_ID_ERROR]: 'Useless case in switch statement.',
	[MESSAGE_ID_SUGGESTION]: 'Remove this case.',
};

const isEmptySwitchCase = node => node.consequent.every(node => isEmptyNode(node));

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => ({
	* 'SwitchStatement[cases.length>1]'(switchStatement) {
		const {cases} = switchStatement;

		// TypeScript allows multiple `default` cases
		const defaultCases = cases.filter(switchCase => switchCase.test === null);
		if (defaultCases.length !== 1) {
			return;
		}

		const [defaultCase] = defaultCases;

		// We only check cases where the last case is the `default` case
		if (defaultCase !== cases[cases.length - 1]) {
			return;
		}

		const uselessCases = [];

		for (let index = cases.length - 2; index >= 0; index--) {
			const node = cases[index];
			if (isEmptySwitchCase(node)) {
				uselessCases.unshift(node);
			} else {
				break;
			}
		}

		for (const node of uselessCases) {
			yield {
				node,
				loc: getSwitchCaseHeadLocation(node, context.getSourceCode()),
				messageId: MESSAGE_ID_ERROR,
				suggest: [
					{
						messageId: MESSAGE_ID_SUGGESTION,
						/** @param {import('eslint').Rule.RuleFixer} fixer */
						fix: fixer => fixer.remove(node),
					},
				],
			};
		}
	},
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Disallow useless case in switch statements.',
		},
		hasSuggestions: true,
		messages,
	},
};
