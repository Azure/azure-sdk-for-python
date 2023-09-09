'use strict';
const not = require('./negation.js');

// AST Types:
// https://github.com/eslint/espree/blob/master/lib/ast-node-types.js#L18
// Only types possible to be `argument` are listed
const impossibleNodeTypes = [
	'ArrayExpression',
	'BinaryExpression',
	'ClassExpression',
	'Literal',
	'ObjectExpression',
	'TemplateLiteral',
	'UnaryExpression',
	'UpdateExpression',
];

// Technically these nodes could be a function, but most likely not
const mostLikelyNotNodeTypes = [
	'AssignmentExpression',
	'AwaitExpression',
	'LogicalExpression',
	'NewExpression',
	'TaggedTemplateExpression',
	'ThisExpression',
];

const notFunctionSelector = node => not([
	[...impossibleNodeTypes, ...mostLikelyNotNodeTypes].map(type => `[${node}.type="${type}"]`),
	`[${node}.type="Identifier"][${node}.name="undefined"]`,
	[
		`[${node}.type="CallExpression"]`,
		not([
			`[${node}.callee.type="MemberExpression"]`,
			`[${node}.callee.optional!=true]`,
			`[${node}.callee.computed!=true]`,
			`[${node}.callee.property.type="Identifier"]`,
			`[${node}.callee.property.name="bind"]`,
		].join('')),
	].join(''),
]);

module.exports = {
	notFunctionSelector,
};
