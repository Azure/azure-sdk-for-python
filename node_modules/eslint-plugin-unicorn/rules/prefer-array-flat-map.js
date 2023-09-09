'use strict';
const {isNodeMatches} = require('./utils/is-node-matches.js');
const {methodCallSelector, matches} = require('./selectors/index.js');
const {removeMethodCall} = require('./fix/index.js');

const MESSAGE_ID = 'prefer-array-flat-map';
const messages = {
	[MESSAGE_ID]: 'Prefer `.flatMap(…)` over `.map(…).flat()`.',
};

const selector = [
	methodCallSelector('flat'),
	matches([
		'[arguments.length=0]',
		'[arguments.length=1][arguments.0.type="Literal"][arguments.0.raw="1"]',
	]),
	methodCallSelector({path: 'callee.object', method: 'map'}),
].join('');

const ignored = ['React.Children', 'Children'];

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => ({
	[selector](flatCallExpression) {
		const mapCallExpression = flatCallExpression.callee.object;
		if (isNodeMatches(mapCallExpression.callee.object, ignored)) {
			return;
		}

		const sourceCode = context.getSourceCode();
		const mapProperty = mapCallExpression.callee.property;

		return {
			node: flatCallExpression,
			loc: {start: mapProperty.loc.start, end: flatCallExpression.loc.end},
			messageId: MESSAGE_ID,
			* fix(fixer) {
				// Removes:
				//   map(…).flat();
				//         ^^^^^^^
				//   (map(…)).flat();
				//           ^^^^^^^
				yield * removeMethodCall(fixer, flatCallExpression, sourceCode);

				// Renames:
				//   map(…).flat();
				//   ^^^
				//   (map(…)).flat();
				//    ^^^
				yield fixer.replaceText(mapProperty, 'flatMap');
			},
		};
	},
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Prefer `.flatMap(…)` over `.map(…).flat()`.',
		},
		fixable: 'code',
		messages,
	},
};
