'use strict';

const { getStringIfConstant } = require('eslint-utils');

/**
 * @fileoverview Match suite descriptions to match a pre-configured regular expression
 * @author Alexander Afanasyev
 */

const defaultSuiteNames = [ 'describe', 'context', 'suite' ];

function inlineOptions(options) {
    const [
        stringPattern,
        suiteNames = defaultSuiteNames,
        message
    ] = options;

    const pattern = new RegExp(stringPattern, 'u');

    return { pattern, suiteNames, message };
}

function objectOptions(options) {
    const {
        pattern: stringPattern,
        suiteNames = defaultSuiteNames,
        message
    } = options;

    const pattern = new RegExp(stringPattern, 'u');

    return { pattern, suiteNames, message };
}

const patternSchema = {
    type: 'string'
};
const suiteNamesSchema = {
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
            description: 'Match suite descriptions against a pre-configured regular expression',
            url: 'https://github.com/lo1tuma/eslint-plugin-mocha/blob/master/docs/rules/valid-suite-description.md'
        },
        schema: [
            {
                oneOf: [ patternSchema, {
                    type: 'object',
                    properties: {
                        pattern: patternSchema,
                        suiteNames: suiteNamesSchema,
                        message: messageSchema
                    },
                    additionalProperties: false
                } ]
            },
            suiteNamesSchema,
            messageSchema
        ]
    },
    create(context) {
        const options = context.options[0];

        const { pattern, suiteNames, message } = typeof options === 'object' ?
            objectOptions(options) :
            inlineOptions(context.options);

        function isSuite(node) {
            return node.callee && node.callee.name && suiteNames.includes(node.callee.name);
        }

        function hasValidSuiteDescription(mochaCallExpression) {
            const args = mochaCallExpression.arguments;
            const descriptionArgument = args[0];
            const description = getStringIfConstant(descriptionArgument, context.getScope());

            if (description) {
                return pattern.test(description);
            }

            return true;
        }

        function hasValidOrNoSuiteDescription(mochaCallExpression) {
            const args = mochaCallExpression.arguments;
            const hasNoSuiteDescription = args.length === 0;

            return hasNoSuiteDescription || hasValidSuiteDescription(mochaCallExpression);
        }

        return {
            CallExpression(node) {
                const callee = node.callee;

                if (isSuite(node)) {
                    if (!hasValidOrNoSuiteDescription(node)) {
                        context.report({ node, message: message || `Invalid "${ callee.name }()" description found.` });
                    }
                }
            }
        };
    }
};
