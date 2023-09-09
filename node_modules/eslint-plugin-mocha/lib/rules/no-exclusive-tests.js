'use strict';

const createAstUtils = require('../util/ast');

module.exports = {
    meta: {
        type: 'problem',
        docs: {
            description: 'Disallow exclusive tests',
            url: 'https://github.com/lo1tuma/eslint-plugin-mocha/blob/master/docs/rules/no-exclusive-tests.md'
        },
        schema: []
    },
    create(context) {
        const astUtils = createAstUtils(context.settings);

        const options = { modifiers: [ 'only' ], modifiersOnly: true };
        const isDescribe = astUtils.buildIsDescribeAnswerer(options);
        const isTestCase = astUtils.buildIsTestCaseAnswerer(options);

        return {
            CallExpression(node) {
                if (isDescribe(node) || isTestCase(node)) {
                    const callee = node.callee;

                    context.report({
                        node: callee.property,
                        message: 'Unexpected exclusive mocha test.'
                    });
                }
            }
        };
    }
};
