'use strict';

/* eslint "complexity": [ "error", 5 ] */

/**
 * @fileoverview Disallow async functions as arguments to describe
 */

const createAstUtils = require('../util/ast');

module.exports = {
    meta: {
        type: 'problem',
        docs: {
            description: 'Disallow async functions passed to describe',
            url: 'https://github.com/lo1tuma/eslint-plugin-mocha/blob/master/docs/rules/no-async-describe.md'
        },
        fixable: 'code',
        schema: []
    },
    create(context) {
        const astUtils = createAstUtils(context.settings);
        const sourceCode = context.getSourceCode();

        function isFunction(node) {
            return (
                node.type === 'FunctionExpression' ||
                node.type === 'FunctionDeclaration' ||
                node.type === 'ArrowFunctionExpression'
            );
        }

        function containsDirectAwait(node) {
            if (node.type === 'AwaitExpression') {
                return true;
            } else if (node.type && !isFunction(node)) {
                return Object.keys(node).some(function (key) {
                    if (Array.isArray(node[key])) {
                        return node[key].some(containsDirectAwait);
                    } else if (key !== 'parent' && node[key] && typeof node[key] === 'object') {
                        return containsDirectAwait(node[key]);
                    }
                    return false;
                });
            }
            return false;
        }

        function fixAsyncFunction(fixer, fn) {
            if (!containsDirectAwait(fn.body)) {
                // Remove the "async" token and all the whitespace before "function":
                const [ asyncToken, functionToken ] = sourceCode.getFirstTokens(fn, 2);
                return fixer.removeRange([ asyncToken.range[0], functionToken.range[0] ]);
            }
            return undefined;
        }

        function isAsyncFunction(node) {
            return node && (node.type === 'FunctionExpression' ||
                node.type === 'ArrowFunctionExpression') && node.async;
        }

        return {
            CallExpression(node) {
                const name = astUtils.getNodeName(node.callee);

                if (astUtils.isDescribe(node)) {
                    const fnArg = node.arguments.slice(-1)[0];
                    if (isAsyncFunction(fnArg)) {
                        context.report({
                            node: fnArg,
                            message: `Unexpected async function in ${name}()`,
                            fix(fixer) {
                                return fixAsyncFunction(fixer, fnArg);
                            }
                        });
                    }
                }
            }
        };
    }
};
