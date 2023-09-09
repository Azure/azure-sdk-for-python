'use strict';

function isArrowFunctionBody(node) {
	return node.parent.type === 'ArrowFunctionExpression' && node.parent.body === node;
}

module.exports = isArrowFunctionBody;
