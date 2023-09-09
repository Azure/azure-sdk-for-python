'use strict';
const {
	removeParentheses,
	removeMemberExpressionProperty,
} = require('./fix/index.js');
const {isLiteral} = require('./ast/index.js');

const MESSAGE_ID = 'no-await-expression-member';
const messages = {
	[MESSAGE_ID]: 'Do not access a member directly from an await expression.',
};

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const sourceCode = context.getSourceCode();

	return {
		'MemberExpression[object.type="AwaitExpression"]'(memberExpression) {
			const {property} = memberExpression;
			const problem = {
				node: property,
				messageId: MESSAGE_ID,
			};

			// `const foo = (await bar)[0]`
			if (
				memberExpression.computed
				&& !memberExpression.optional
				&& (isLiteral(property, 0) || isLiteral(property, 1))
				&& memberExpression.parent.type === 'VariableDeclarator'
				&& memberExpression.parent.init === memberExpression
				&& memberExpression.parent.id.type === 'Identifier'
				&& !memberExpression.parent.id.typeAnnotation
			) {
				problem.fix = function * (fixer) {
					const variable = memberExpression.parent.id;
					yield fixer.insertTextBefore(variable, property.value === 0 ? '[' : '[, ');
					yield fixer.insertTextAfter(variable, ']');

					yield removeMemberExpressionProperty(fixer, memberExpression, sourceCode);
					yield * removeParentheses(memberExpression.object, fixer, sourceCode);
				};

				return problem;
			}

			// `const foo = (await bar).foo`
			if (
				!memberExpression.computed
				&& !memberExpression.optional
				&& property.type === 'Identifier'
				&& memberExpression.parent.type === 'VariableDeclarator'
				&& memberExpression.parent.init === memberExpression
				&& memberExpression.parent.id.type === 'Identifier'
				&& memberExpression.parent.id.name === property.name
				&& !memberExpression.parent.id.typeAnnotation
			) {
				problem.fix = function * (fixer) {
					const variable = memberExpression.parent.id;
					yield fixer.insertTextBefore(variable, '{');
					yield fixer.insertTextAfter(variable, '}');

					yield removeMemberExpressionProperty(fixer, memberExpression, sourceCode);
					yield * removeParentheses(memberExpression.object, fixer, sourceCode);
				};

				return problem;
			}

			return problem;
		},
	};
};

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Disallow member access from await expression.',
		},
		fixable: 'code',
		messages,
	},
};
