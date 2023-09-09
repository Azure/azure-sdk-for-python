'use strict';
const {isParenthesized} = require('@eslint-community/eslint-utils');
const needsSemicolon = require('./utils/needs-semicolon.js');
const {isDecimalInteger} = require('./utils/numeric.js');
const toLocation = require('./utils/to-location.js');
const {fixSpaceAroundKeyword} = require('./fix/index.js');
const {isNumberLiteral} = require('./ast/index.js');

const MESSAGE_ZERO_FRACTION = 'zero-fraction';
const MESSAGE_DANGLING_DOT = 'dangling-dot';
const messages = {
	[MESSAGE_ZERO_FRACTION]: 'Don\'t use a zero fraction in the number.',
	[MESSAGE_DANGLING_DOT]: 'Don\'t use a dangling dot in the number.',
};

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => ({
	Literal(node) {
		if (!isNumberLiteral(node)) {
			return;
		}

		// Legacy octal number `0777` and prefixed number `0o1234` cannot have a dot.
		const {raw} = node;
		const match = raw.match(/^(?<before>[\d_]*)(?<dotAndFractions>\.[\d_]*)(?<after>.*)$/);
		if (!match) {
			return;
		}

		const {before, dotAndFractions, after} = match.groups;
		const fixedDotAndFractions = dotAndFractions.replace(/[.0_]+$/g, '');
		const formatted = ((before + fixedDotAndFractions) || '0') + after;

		if (formatted === raw) {
			return;
		}

		const isDanglingDot = dotAndFractions === '.';
		// End of fractions
		const end = node.range[0] + before.length + dotAndFractions.length;
		const start = end - (raw.length - formatted.length);
		const sourceCode = context.getSourceCode();
		return {
			loc: toLocation([start, end], sourceCode),
			messageId: isDanglingDot ? MESSAGE_DANGLING_DOT : MESSAGE_ZERO_FRACTION,
			* fix(fixer) {
				let fixed = formatted;
				if (
					node.parent.type === 'MemberExpression'
					&& node.parent.object === node
					&& isDecimalInteger(formatted)
					&& !isParenthesized(node, sourceCode)
				) {
					fixed = `(${fixed})`;

					if (needsSemicolon(sourceCode.getTokenBefore(node), sourceCode, fixed)) {
						fixed = `;${fixed}`;
					}
				}

				yield fixer.replaceText(node, fixed);
				yield * fixSpaceAroundKeyword(fixer, node, sourceCode);
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
			description: 'Disallow number literals with zero fractions or dangling dots.',
		},
		fixable: 'code',
		messages,
	},
};
