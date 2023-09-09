'use strict';

const createAstUtils = require('../util/ast');

module.exports = {
    meta: {
        type: 'suggestion',
        docs: {
            description: 'Disallow pending tests',
            url: 'https://github.com/lo1tuma/eslint-plugin-mocha/blob/master/docs/rules/no-pending-tests.md'
        },
        schema: []
    },
    create(context) {
        const astUtils = createAstUtils(context.settings);
        const isTestCase = astUtils.buildIsTestCaseAnswerer();

        function isPendingMochaTest(node) {
            return isTestCase(node) &&
                node.arguments.length === 1 &&
                node.arguments[0].type === 'Literal';
        }

        return {
            CallExpression(node) {
                if (node.callee && isPendingMochaTest(node)) {
                    context.report({
                        node,
                        message: 'Unexpected pending mocha test.'
                    });
                }
            }
        };
    }
};
