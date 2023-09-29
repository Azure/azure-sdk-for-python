# Integration Scenario

This package exercises an _invalid install scenario_. `azure-core` requires `msrest` as one of its dependencies. By adding `msrest` to the `uninstall` configuration for an `optional` environment, we are exercising the

> you shouldn't do this

scenario for `optional`. Before an invocation of `pytest`, a `depends` check is run to confirm consistency of the environment.