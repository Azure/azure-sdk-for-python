'use strict';
const {isParenthesized} = require('@eslint-community/eslint-utils');
const avoidCapture = require('./utils/avoid-capture.js');
const needsSemicolon = require('./utils/needs-semicolon.js');
const isSameReference = require('./utils/is-same-reference.js');
const getIndentString = require('./utils/get-indent-string.js');
const {getParenthesizedText} = require('./utils/parentheses.js');
const shouldAddParenthesesToConditionalExpressionChild = require('./utils/should-add-parentheses-to-conditional-expression-child.js');
const {extendFixRange} = require('./fix/index.js');
const getScopes = require('./utils/get-scopes.js');

const messageId = 'prefer-ternary';

const selector = [
	'IfStatement',
	':not(IfStatement > .alternate)',
	'[test.type!="ConditionalExpression"]',
	'[consequent]',
	'[alternate]',
].join('');

const isTernary = node => node?.type === 'ConditionalExpression';

function getNodeBody(node) {
	/* c8 ignore next 3 */
	if (!node) {
		return;
	}

	if (node.type === 'ExpressionStatement') {
		return getNodeBody(node.expression);
	}

	if (node.type === 'BlockStatement') {
		const body = node.body.filter(({type}) => type !== 'EmptyStatement');
		if (body.length === 1) {
			return getNodeBody(body[0]);
		}
	}

	return node;
}

const isSingleLineNode = node => node.loc.start.line === node.loc.end.line;

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const onlySingleLine = context.options[0] === 'only-single-line';
	const sourceCode = context.getSourceCode();
	const scopeToNamesGeneratedByFixer = new WeakMap();
	const isSafeName = (name, scopes) => scopes.every(scope => {
		const generatedNames = scopeToNamesGeneratedByFixer.get(scope);
		return !generatedNames || !generatedNames.has(name);
	});

	const getText = node => {
		let text = getParenthesizedText(node, sourceCode);
		if (
			!isParenthesized(node, sourceCode)
			&& shouldAddParenthesesToConditionalExpressionChild(node)
		) {
			text = `(${text})`;
		}

		return text;
	};

	function merge(options, mergeOptions) {
		const {
			before = '',
			after = ';',
			consequent,
			alternate,
			node,
		} = options;

		const {
			checkThrowStatement,
			returnFalseIfNotMergeable,
		} = {
			checkThrowStatement: false,
			returnFalseIfNotMergeable: false,
			...mergeOptions,
		};

		if (!consequent || !alternate || consequent.type !== alternate.type) {
			return returnFalseIfNotMergeable ? false : options;
		}

		const {type, argument, delegate, left, right, operator} = consequent;

		if (
			type === 'ReturnStatement'
			&& !isTernary(argument)
			&& !isTernary(alternate.argument)
		) {
			return merge({
				before: `${before}return `,
				after,
				consequent: argument === null ? 'undefined' : argument,
				alternate: alternate.argument === null ? 'undefined' : alternate.argument,
				node,
			});
		}

		if (
			type === 'YieldExpression'
			&& delegate === alternate.delegate
			&& !isTernary(argument)
			&& !isTernary(alternate.argument)
		) {
			return merge({
				before: `${before}yield${delegate ? '*' : ''} (`,
				after: `)${after}`,
				consequent: argument === null ? 'undefined' : argument,
				alternate: alternate.argument === null ? 'undefined' : alternate.argument,
				node,
			});
		}

		if (
			type === 'AwaitExpression'
			&& !isTernary(argument)
			&& !isTernary(alternate.argument)
		) {
			return merge({
				before: `${before}await (`,
				after: `)${after}`,
				consequent: argument,
				alternate: alternate.argument,
				node,
			});
		}

		if (
			checkThrowStatement
			&& type === 'ThrowStatement'
			&& !isTernary(argument)
			&& !isTernary(alternate.argument)
		) {
			// `ThrowStatement` don't check nested

			// If `IfStatement` is not a `BlockStatement`, need add `{}`
			const {parent} = node;
			const needBraces = parent && parent.type !== 'BlockStatement';
			return {
				type,
				before: `${before}${needBraces ? '{\n{{INDENT_STRING}}' : ''}const {{ERROR_NAME}} = `,
				after: `;\n{{INDENT_STRING}}throw {{ERROR_NAME}};${needBraces ? '\n}' : ''}`,
				consequent: argument,
				alternate: alternate.argument,
			};
		}

		if (
			type === 'AssignmentExpression'
			&& operator === alternate.operator
			&& !isTernary(left)
			&& !isTernary(alternate.left)
			&& !isTernary(right)
			&& !isTernary(alternate.right)
			&& isSameReference(left, alternate.left)
		) {
			return merge({
				before: `${before}${sourceCode.getText(left)} ${operator} `,
				after,
				consequent: right,
				alternate: alternate.right,
				node,
			});
		}

		return returnFalseIfNotMergeable ? false : options;
	}

	return {
		[selector](node) {
			const consequent = getNodeBody(node.consequent);
			const alternate = getNodeBody(node.alternate);

			if (
				onlySingleLine
				&& [consequent, alternate, node.test].some(node => !isSingleLineNode(node))
			) {
				return;
			}

			const result = merge({node, consequent, alternate}, {
				checkThrowStatement: true,
				returnFalseIfNotMergeable: true,
			});

			if (!result) {
				return;
			}

			const problem = {node, messageId};

			// Don't fix if there are comments
			if (sourceCode.getCommentsInside(node).length > 0) {
				return problem;
			}

			const scope = sourceCode.getScope(node);
			problem.fix = function * (fixer) {
				const testText = getText(node.test);
				const consequentText = typeof result.consequent === 'string'
					? result.consequent
					: getText(result.consequent);
				const alternateText = typeof result.alternate === 'string'
					? result.alternate
					: getText(result.alternate);

				let {type, before, after} = result;

				let generateNewVariables = false;
				if (type === 'ThrowStatement') {
					const scopes = getScopes(scope);
					const errorName = avoidCapture('error', scopes, isSafeName);

					for (const scope of scopes) {
						if (!scopeToNamesGeneratedByFixer.has(scope)) {
							scopeToNamesGeneratedByFixer.set(scope, new Set());
						}

						const generatedNames = scopeToNamesGeneratedByFixer.get(scope);
						generatedNames.add(errorName);
					}

					const indentString = getIndentString(node, sourceCode);

					after = after
						.replace('{{INDENT_STRING}}', indentString)
						.replace('{{ERROR_NAME}}', errorName);
					before = before
						.replace('{{INDENT_STRING}}', indentString)
						.replace('{{ERROR_NAME}}', errorName);
					generateNewVariables = true;
				}

				let fixed = `${before}${testText} ? ${consequentText} : ${alternateText}${after}`;
				const tokenBefore = sourceCode.getTokenBefore(node);
				const shouldAddSemicolonBefore = needsSemicolon(tokenBefore, sourceCode, fixed);
				if (shouldAddSemicolonBefore) {
					fixed = `;${fixed}`;
				}

				yield fixer.replaceText(node, fixed);

				if (generateNewVariables) {
					yield * extendFixRange(fixer, sourceCode.ast.range);
				}
			};

			return problem;
		},
	};
};

const schema = [
	{
		enum: ['always', 'only-single-line'],
		default: 'always',
	},
];

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Prefer ternary expressions over simple `if-else` statements.',
		},
		fixable: 'code',
		schema,
		messages: {
			[messageId]: 'This `if` statement can be replaced by a ternary expression.',
		},
	},
};
