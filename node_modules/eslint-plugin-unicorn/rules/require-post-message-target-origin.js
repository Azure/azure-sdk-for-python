'use strict';
const {methodCallSelector} = require('./selectors/index.js');
const {appendArgument} = require('./fix/index.js');

const ERROR = 'error';
const SUGGESTION = 'suggestion';
const messages = {
	[ERROR]: 'Missing the `targetOrigin` argument.',
	[SUGGESTION]: 'Use `{{code}}`.',
};

/** @param {import('eslint').Rule.RuleContext} context */
function create(context) {
	const sourceCode = context.getSourceCode();
	return {
		[methodCallSelector({method: 'postMessage', argumentsLength: 1})](node) {
			const [penultimateToken, lastToken] = sourceCode.getLastTokens(node, 2);
			const replacements = [];
			const target = node.callee.object;
			if (target.type === 'Identifier') {
				const {name} = target;

				replacements.push(`${name}.location.origin`);

				if (name !== 'self' && name !== 'window' && name !== 'globalThis') {
					replacements.push('self.location.origin');
				}
			} else {
				replacements.push('self.location.origin');
			}

			replacements.push('\'*\'');

			return {
				loc: {
					start: penultimateToken.loc.end,
					end: lastToken.loc.end,
				},
				messageId: ERROR,
				suggest: replacements.map(code => ({
					messageId: SUGGESTION,
					data: {code},
					/** @param {import('eslint').Rule.RuleFixer} fixer */
					fix: fixer => appendArgument(fixer, node, code, sourceCode),
				})),
			};
		},
	};
}

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'problem',
		docs: {
			description: 'Enforce using the `targetOrigin` argument with `window.postMessage()`.',
		},
		hasSuggestions: true,
		messages,
	},
};
