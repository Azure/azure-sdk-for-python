'use strict';

module.exports = {
    rules: {
        'handle-done-callback': require('./lib/rules/handle-done-callback'),
        'max-top-level-suites': require('./lib/rules/max-top-level-suites'),
        'no-async-describe': require('./lib/rules/no-async-describe'),
        'no-exclusive-tests': require('./lib/rules/no-exclusive-tests'),
        'no-exports': require('./lib/rules/no-exports'),
        'no-global-tests': require('./lib/rules/no-global-tests'),
        'no-hooks': require('./lib/rules/no-hooks'),
        'no-hooks-for-single-case': require('./lib/rules/no-hooks-for-single-case'),
        'no-identical-title': require('./lib/rules/no-identical-title'),
        'no-mocha-arrows': require('./lib/rules/no-mocha-arrows'),
        'no-nested-tests': require('./lib/rules/no-nested-tests'),
        'no-pending-tests': require('./lib/rules/no-pending-tests'),
        'no-return-and-callback': require('./lib/rules/no-return-and-callback'),
        'no-return-from-async': require('./lib/rules/no-return-from-async'),
        'no-setup-in-describe': require('./lib/rules/no-setup-in-describe'),
        'no-sibling-hooks': require('./lib/rules/no-sibling-hooks'),
        'no-skipped-tests': require('./lib/rules/no-skipped-tests'),
        'no-synchronous-tests': require('./lib/rules/no-synchronous-tests'),
        'no-top-level-hooks': require('./lib/rules/no-top-level-hooks'),
        'prefer-arrow-callback': require('./lib/rules/prefer-arrow-callback'),
        'valid-suite-description': require('./lib/rules/valid-suite-description'),
        'valid-test-description': require('./lib/rules/valid-test-description'),
        'no-empty-description': require('./lib/rules/no-empty-description.js')
    },
    configs: {
        all: {
            env: { mocha: true },
            plugins: [ 'mocha' ],
            rules: {
                'mocha/handle-done-callback': 'error',
                'mocha/max-top-level-suites': 'error',
                'mocha/no-async-describe': 'error',
                'mocha/no-exclusive-tests': 'error',
                'mocha/no-exports': 'error',
                'mocha/no-global-tests': 'error',
                'mocha/no-hooks': 'error',
                'mocha/no-hooks-for-single-case': 'error',
                'mocha/no-identical-title': 'error',
                'mocha/no-mocha-arrows': 'error',
                'mocha/no-nested-tests': 'error',
                'mocha/no-pending-tests': 'error',
                'mocha/no-return-and-callback': 'error',
                'mocha/no-return-from-async': 'error',
                'mocha/no-setup-in-describe': 'error',
                'mocha/no-sibling-hooks': 'error',
                'mocha/no-skipped-tests': 'error',
                'mocha/no-synchronous-tests': 'error',
                'mocha/no-top-level-hooks': 'error',
                'mocha/prefer-arrow-callback': 'error',
                'mocha/valid-suite-description': 'error',
                'mocha/valid-test-description': 'error',
                'mocha/no-empty-description': 'error'
            }
        },

        recommended: {
            env: { mocha: true },
            plugins: [ 'mocha' ],
            rules: {
                'mocha/handle-done-callback': 'error',
                'mocha/max-top-level-suites': [ 'error', { limit: 1 } ],
                'mocha/no-async-describe': 'error',
                'mocha/no-exclusive-tests': 'warn',
                'mocha/no-exports': 'error',
                'mocha/no-global-tests': 'error',
                'mocha/no-hooks': 'off',
                'mocha/no-hooks-for-single-case': 'off',
                'mocha/no-identical-title': 'error',
                'mocha/no-mocha-arrows': 'error',
                'mocha/no-nested-tests': 'error',
                'mocha/no-pending-tests': 'warn',
                'mocha/no-return-and-callback': 'error',
                'mocha/no-return-from-async': 'off',
                'mocha/no-setup-in-describe': 'error',
                'mocha/no-sibling-hooks': 'error',
                'mocha/no-skipped-tests': 'warn',
                'mocha/no-synchronous-tests': 'off',
                'mocha/no-top-level-hooks': 'warn',
                'mocha/prefer-arrow-callback': 'off',
                'mocha/valid-suite-description': 'off',
                'mocha/valid-test-description': 'off',
                'mocha/no-empty-description': 'error'
            }
        }
    }
};
