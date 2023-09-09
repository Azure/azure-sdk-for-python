'use strict';

const createAstUtils = require('../util/ast');

module.exports = {
    meta: {
        docs: {
            description: 'Disallow skipped tests',
            url: 'https://github.com/lo1tuma/eslint-plugin-mocha/blob/master/docs/rules/no-skipped-tests.md'
        },
        type: 'problem',
        schema: []
    },
    create(context) {
        const astUtils = createAstUtils(context.settings);
        const options = { modifiers: [ 'skip' ], modifiersOnly: true };
        const isTestCase = astUtils.buildIsTestCaseAnswerer(options);
        const isDescribe = astUtils.buildIsDescribeAnswerer(options);

        return {
            CallExpression(node) {
                if (isDescribe(node) || isTestCase(node)) {
                    const callee = node.callee;
                    const nodeToReport =
                        callee.type === 'MemberExpression' ?
                            callee.property :
                            callee;

                    context.report({
                        node: nodeToReport,
                        message: 'Unexpected skipped mocha test.'
                    });
                }
            }
        };
    }
};
