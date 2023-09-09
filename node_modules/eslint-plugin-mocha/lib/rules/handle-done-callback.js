'use strict';

const { find } = require('rambda');
const createAstUtils = require('../util/ast');

module.exports = {
    meta: {
        type: 'problem',
        docs: {
            description: 'Enforces handling of callbacks for async tests',
            url: 'https://github.com/lo1tuma/eslint-plugin-mocha/blob/master/docs/rules/handle-done-callback.md'
        },
        schema: [
            {
                type: 'object',
                properties: {
                    ignoreSkipped: {
                        type: 'boolean',
                        default: false
                    }
                },
                additionalProperties: false
            }
        ]
    },
    create(context) {
        const astUtils = createAstUtils(context.settings);
        const [ { ignoreSkipped = false } = {} ] = context.options;
        const modifiersToCheck = ignoreSkipped ? [ 'only' ] : [ 'only', 'skip' ];

        function isAsyncFunction(functionExpression) {
            return functionExpression.params.length === 1;
        }

        function findParamInScope(paramName, scope) {
            return find(function (variable) {
                return variable.name === paramName && variable.defs[0].type === 'Parameter';
            }, scope.variables);
        }

        function isReferenceHandled(reference) {
            const parent = context.getSourceCode().getNodeByRangeIndex(reference.identifier.range[0]).parent;

            return parent.type === 'CallExpression';
        }

        function hasHandledReferences(references) {
            return references.some(isReferenceHandled);
        }

        function checkAsyncMochaFunction(functionExpression) {
            const scope = context.getScope();
            const callback = functionExpression.params[0];
            const callbackName = callback.name;
            const callbackVariable = findParamInScope(callbackName, scope);

            if (callbackVariable && !hasHandledReferences(callbackVariable.references)) {
                context.report({
                    node: callback,
                    message: 'Expected "{{name}}" callback to be handled.', data: { name: callbackName }
                });
            }
        }

        function check(node) {
            if (astUtils.hasParentMochaFunctionCall(node, { modifiers: modifiersToCheck }) && isAsyncFunction(node)) {
                checkAsyncMochaFunction(node);
            }
        }

        return {
            FunctionExpression: check,
            ArrowFunctionExpression: check
        };
    }
};
