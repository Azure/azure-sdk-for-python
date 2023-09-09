'use strict';

const createAstUtils = require('../util/ast');

function reportIfShortArrowFunction(context, node) {
    if (node.body.type !== 'BlockStatement') {
        context.report({
            node: node.body,
            message: 'Confusing implicit return in a test with callback'
        });
        return true;
    }
    return false;
}

function isFunctionCallWithName(node, name) {
    return node.type === 'CallExpression' &&
        node.callee.type === 'Identifier' &&
        node.callee.name === name;
}

module.exports = {
    meta: {
        type: 'problem',
        docs: {
            description: 'Disallow returning in a test or hook function that uses a callback',
            url: 'https://github.com/lo1tuma/eslint-plugin-mocha/blob/master/docs/rules/no-return-and-callback.md'
        },
        schema: []
    },
    create(context) {
        const astUtils = createAstUtils(context.settings);

        function isAllowedReturnStatement(node, doneName) {
            const argument = node.argument;

            if (astUtils.isReturnOfUndefined(node) || argument.type === 'Literal') {
                return true;
            }

            return isFunctionCallWithName(argument, doneName);
        }

        function reportIfFunctionWithBlock(node, doneName) {
            const returnStatement = astUtils.findReturnStatement(node.body.body);
            if (returnStatement && !isAllowedReturnStatement(returnStatement, doneName)) {
                context.report({
                    node: returnStatement,
                    message: 'Unexpected use of `return` in a test with callback'
                });
            }
        }

        function check(node) {
            if (node.params.length === 0 || !astUtils.hasParentMochaFunctionCall(node)) {
                return;
            }

            if (!reportIfShortArrowFunction(context, node)) {
                reportIfFunctionWithBlock(node, node.params[0].name);
            }
        }

        return {
            FunctionExpression: check,
            ArrowFunctionExpression: check
        };
    }
};
