'use strict';

const { isNil, find } = require('rambda');
const createAstUtils = require('../util/ast');

const asyncMethods = [ 'async', 'callback', 'promise' ];

function hasAsyncCallback(functionExpression) {
    return functionExpression.params.length === 1;
}

function isAsyncFunction(functionExpression) {
    return functionExpression.async === true;
}

function findPromiseReturnStatement(nodes) {
    return find(function (node) {
        return (
            node.type === 'ReturnStatement' &&
            node.argument &&
            node.argument.type !== 'Literal'
        );
    }, nodes);
}

function doesReturnPromise(functionExpression) {
    const bodyStatement = functionExpression.body;
    let returnStatement = null;

    if (bodyStatement.type === 'BlockStatement') {
        returnStatement = findPromiseReturnStatement(
            functionExpression.body.body
        );
    } else if (bodyStatement.type !== 'Literal') {
        //  allow arrow statements calling a promise with implicit return.
        returnStatement = bodyStatement;
    }

    return returnStatement !== null && typeof returnStatement !== 'undefined';
}

module.exports = {
    meta: {
        type: 'suggestion',
        docs: {
            description: 'Disallow synchronous tests',
            url: 'https://github.com/lo1tuma/eslint-plugin-mocha/blob/master/docs/rules/no-synchronous-tests.md'
        },
        schema: [
            {
                type: 'object',
                properties: {
                    allowed: {
                        type: 'array',
                        items: {
                            type: 'string',
                            enum: asyncMethods
                        },
                        minItems: 1,
                        uniqueItems: true
                    }
                }
            }
        ]
    },
    create(context) {
        const astUtils = createAstUtils(context.settings);
        const options = context.options[0] || {};
        const allowedAsyncMethods = isNil(options.allowed) ?
            asyncMethods :
            options.allowed;

        function check(node) {
            if (astUtils.hasParentMochaFunctionCall(node)) {
                // For each allowed async test method, check if it is used in the test
                const testAsyncMethods = allowedAsyncMethods.map(function (
                    method
                ) {
                    switch (method) {
                    case 'async':
                        return isAsyncFunction(node);

                    case 'callback':
                        return hasAsyncCallback(node);

                    default:
                        return doesReturnPromise(node);
                    }
                });

                // Check that at least one allowed async test method is used in the test
                const isAsyncTest = testAsyncMethods.includes(true);

                if (!isAsyncTest) {
                    context.report({ node, message: 'Unexpected synchronous test.' });
                }
            }
        }

        return {
            FunctionExpression: check,
            ArrowFunctionExpression: check
        };
    }
};
