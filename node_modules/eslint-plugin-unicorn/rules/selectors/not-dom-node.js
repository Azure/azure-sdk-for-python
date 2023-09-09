'use strict';

const {isUndefined} = require('../ast/index.js');

// AST Types:
// https://github.com/eslint/espree/blob/master/lib/ast-node-types.js#L18
// Only types possible to be `callee` or `argument` are listed
const impossibleNodeTypes = [
	'ArrayExpression',
	'ArrowFunctionExpression',
	'ClassExpression',
	'FunctionExpression',
	'Literal',
	'ObjectExpression',
	'TemplateLiteral',
];

// We might need this later
/* c8 ignore start */
const isNotDomNode = node =>
	impossibleNodeTypes.includes(node.type)
	|| isUndefined(node);
/* c8 ignore end */

const notDomNodeSelector = node => [
	...impossibleNodeTypes.map(type => `[${node}.type!="${type}"]`),
	`:not([${node}.type="Identifier"][${node}.name="undefined"])`,
].join('');

module.exports = {
	isNotDomNode,
	notDomNodeSelector,
};
