'use strict';
const {GlobalReferenceTracker} = require('./utils/global-reference-tracker.js');
const builtins = require('./utils/builtins.js');
const {
	switchCallExpressionToNewExpression,
	switchNewExpressionToCallExpression,
} = require('./fix/index.js');

const messages = {
	enforce: 'Use `new {{name}}()` instead of `{{name}}()`.',
	disallow: 'Use `{{name}}()` instead of `new {{name}}()`.',
};

function enforceNewExpression({node, path: [name]}, sourceCode) {
	if (name === 'Object') {
		const {parent} = node;
		if (
			parent.type === 'BinaryExpression'
			&& (parent.operator === '===' || parent.operator === '!==')
			&& (parent.left === node || parent.right === node)
		) {
			return;
		}
	}

	return {
		node,
		messageId: 'enforce',
		data: {name},
		fix: fixer => switchCallExpressionToNewExpression(node, sourceCode, fixer),
	};
}

function enforceCallExpression({node, path: [name]}, sourceCode) {
	const problem = {
		node,
		messageId: 'disallow',
		data: {name},
	};

	if (name !== 'String' && name !== 'Boolean' && name !== 'Number') {
		problem.fix = function * (fixer) {
			yield * switchNewExpressionToCallExpression(node, sourceCode, fixer);
		};
	}

	return problem;
}

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const sourceCode = context.getSourceCode();
	const newExpressionTracker = new GlobalReferenceTracker({
		objects: builtins.disallowNew,
		type: GlobalReferenceTracker.CONSTRUCT,
		handle: reference => enforceCallExpression(reference, sourceCode),
	});
	const callExpressionTracker = new GlobalReferenceTracker({
		objects: builtins.enforceNew,
		type: GlobalReferenceTracker.CALL,
		handle: reference => enforceNewExpression(reference, sourceCode),
	});

	return {
		* 'Program:exit'(program) {
			const scope = sourceCode.getScope(program);

			yield * newExpressionTracker.track(scope);
			yield * callExpressionTracker.track(scope);
		},
	};
};

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Enforce the use of `new` for all builtins, except `String`, `Number`, `Boolean`, `Symbol` and `BigInt`.',
		},
		fixable: 'code',
		messages,
	},
};
