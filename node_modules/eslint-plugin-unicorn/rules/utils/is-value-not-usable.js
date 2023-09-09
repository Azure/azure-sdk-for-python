'use strict';

module.exports = node =>
	node.parent.type === 'ExpressionStatement'
	|| (
		node.parent.type === 'ChainExpression'
		&& node.parent.parent.type === 'ExpressionStatement'
	);
