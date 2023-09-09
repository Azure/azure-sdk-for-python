'use strict';

const nodeTypesDoNotNeedParentheses = new Set([
	'CallExpression',
	'Identifier',
	'Literal',
	'MemberExpression',
	'NewExpression',
	'TemplateLiteral',
	'ThisExpression',
]);

/**
Check if parentheses should be added to a `node` when it's used as `argument` of `SpreadElement`.

@param {Node} node - The AST node to check.
@returns {boolean}
*/
const shouldAddParenthesesToSpreadElementArgument = node =>
	!nodeTypesDoNotNeedParentheses.has(node.type);

module.exports = shouldAddParenthesesToSpreadElementArgument;
