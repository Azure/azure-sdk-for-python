'use strict';

const { getStringIfConstant } = require('eslint-utils');

const DEFAULT_TEST_NAMES = [ 'describe', 'context', 'suite', 'it', 'test', 'specify' ];
const ERROR_MESSAGE = 'Unexpected empty test description.';

function objectOptions(options = {}) {
    const {
        testNames = DEFAULT_TEST_NAMES,
        message
    } = options;

    return { testNames, message };
}

function isLiteral(node) {
    return node && node.type === 'Literal';
}

function isStaticallyAnalyzableDescription(node, extractedText) {
    if (extractedText === null) {
        return isLiteral(node);
    }

    return true;
}

function isValidDescriptionArgumentNode(node) {
    if (!node) {
        return false;
    }

    return [
        'Literal', 'TemplateLiteral', 'TaggedTemplateExpression',
        'Identifier', 'MemberExpression', 'CallExpression',
        'LogicalExpression', 'BinaryExpression', 'ConditionalExpression',
        'UnaryExpression', 'SpreadElement', 'AwaitExpression',
        'YieldExpression', 'NewExpression' ].includes(node.type);
}

module.exports = {
    meta: {
        type: 'suggestion',
        docs: {
            description: 'Disallow empty test descriptions',
            url: 'https://github.com/lo1tuma/eslint-plugin-mocha/blob/master/docs/rules/no-empty-description.md'
        },
        messages: {
            error: ERROR_MESSAGE
        },
        schema: [
            {
                type: 'object',
                properties: {
                    testNames: {
                        type: 'array',
                        items: {
                            type: 'string'
                        }
                    },
                    message: {
                        type: 'string'
                    }
                },
                additionalProperties: false
            }
        ]
    },
    create(context) {
        const options = context.options[0];

        const { testNames, message } = objectOptions(options);

        function isTest(node) {
            return node.callee && node.callee.name && testNames.includes(node.callee.name);
        }

        function isNonEmptyDescription(mochaCallExpression) {
            const description = mochaCallExpression.arguments[0];

            if (!isValidDescriptionArgumentNode(description)) {
                return false;
            }

            const text = getStringIfConstant(description, context.getScope());

            if (!isStaticallyAnalyzableDescription(description, text)) {
                return true;
            }

            return text && text.trim().length;
        }

        return {
            CallExpression(node) {
                if (isTest(node)) {
                    if (!isNonEmptyDescription(node)) {
                        context.report({
                            node,
                            message: message || ERROR_MESSAGE
                        });
                    }
                }
            }
        };
    }
};
