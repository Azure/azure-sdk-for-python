'use strict';
const {matches, methodCallSelector, arrayPrototypeMethodSelector} = require('./selectors/index.js');
const {appendArgument} = require('./fix/index.js');

const MESSAGE_ID = 'require-array-join-separator';
const messages = {
	[MESSAGE_ID]: 'Missing the separator argument.',
};

const selector = matches([
	// `foo.join()`
	methodCallSelector({
		method: 'join',
		argumentsLength: 0,
		includeOptionalMember: true,
	}),
	// `[].join.call(foo)` and `Array.prototype.join.call(foo)`
	[
		methodCallSelector({method: 'call', argumentsLength: 1}),
		arrayPrototypeMethodSelector({path: 'callee.object', method: 'join'}),
	].join(''),
]);

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const sourceCode = context.getSourceCode();
	return {
		[selector](node) {
			const [penultimateToken, lastToken] = sourceCode.getLastTokens(node, 2);
			const isPrototypeMethod = node.arguments.length === 1;
			return {
				loc: {
					start: penultimateToken.loc[isPrototypeMethod ? 'end' : 'start'],
					end: lastToken.loc.end,
				},
				messageId: MESSAGE_ID,
				/** @param {import('eslint').Rule.RuleFixer} fixer */
				fix: fixer => appendArgument(fixer, node, '\',\'', sourceCode),
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
			description: 'Enforce using the separator argument with `Array#join()`.',
		},
		fixable: 'code',
		messages,
	},
};
