'use strict';

const {isStringLiteral} = require('./literal.js');

const isStaticRequire = node => Boolean(
	node?.type === 'CallExpression'
	&& node.callee.type === 'Identifier'
	&& node.callee.name === 'require'
	&& !node.optional
	&& node.arguments.length === 1
	&& isStringLiteral(node.arguments[0]),
);

module.exports = isStaticRequire;
