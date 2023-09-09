'use strict';

const { getStringIfConstant } = require('eslint-utils');

/**
 * @fileoverview Match test descriptions to match a pre-configured regular expression
 * @author Alexander Afanasyev
 */

const defaultTestNames = [ 'it', 'test', 'specify' ];

function inlineOptions(options) {
    const [
        stringPattern = '^should',
        testNames = defaultTestNames,
        message
    ] = options;

    const pattern = new RegExp(stringPattern, 'u');

    return { pattern, testNames, message };
}

function objectOptions(options) {
    const {
        pattern: stringPattern = '^should',
        testNames = defaultTestNames,
        message
    } = options;
    const pattern = new RegExp(stringPattern, 'u');

    return { pattern, testNames, message };
}

const patternSchema = {
    type: 'string'
};
const testNamesSchema = {
    type: 'array',
    items: {
        type: 'string'
    }
};
const messageSchema = {
    type: 'string'
};

module.exports = {
    meta: {
        type: 'suggestion',
        docs: {
            description: 'Match test descriptions against a pre-configured regular expression',
            url: 'https://github.com/lo1tuma/eslint-plugin-mocha/blob/master/docs/rules/valid-test-description.md'
        },
        schema: [
            {
                oneOf: [ patternSchema, {
                    type: 'object',
                    properties: {
                        pattern: patternSchema,
                        testNames: testNamesSchema,
                        message: messageSchema
                    },
                    additionalProperties: false
                } ]
            },
            testNamesSchema,
            messageSchema
        ]
    },
    create(context) {
        const options = context.options[0];

        const { pattern, testNames, message } = typeof options === 'object' ?
            objectOptions(options) :
            inlineOptions(context.options);

        function isTest(node) {
            return node.callee && node.callee.name && testNames.includes(node.callee.name);
        }

        function hasValidTestDescription(mochaCallExpression) {
            const args = mochaCallExpression.arguments;
            const testDescriptionArgument = args[0];
            const description = getStringIfConstant(testDescriptionArgument, context.getScope());

            if (description) {
                return pattern.test(description);
            }

            return true;
        }

        function hasValidOrNoTestDescription(mochaCallExpression) {
            const args = mochaCallExpression.arguments;
            const hasNoTestDescription = args.length === 0;

            return hasNoTestDescription || hasValidTestDescription(mochaCallExpression);
        }

        return {
            CallExpression(node) {
                const callee = node.callee;

                if (isTest(node)) {
                    if (!hasValidOrNoTestDescription(node)) {
                        context.report({ node, message: message || `Invalid "${ callee.name }()" description found.` });
                    }
                }
            }
        };
    }
};
