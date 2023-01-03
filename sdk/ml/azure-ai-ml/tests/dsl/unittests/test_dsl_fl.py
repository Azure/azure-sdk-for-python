
@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
class TestDSLPipeline:
    def test_dsl_fl_encoding(self) -> None:
        pass
        '''If the 4, big test files for testing the dsl pipeline are any clue, there's a lot to test
        when decorators are concerned. 
        
        We still need to figure out everything that can be tested, starting at least with a full 
        review of what's testing by the 2000+ line file 'test_dsl_pipeline' and checking out what's
        applicable.

        Separate from that, FL-specific testing will also be needed, mostly to check that the tools we
        offer to represent the scatter-gather loop and silos encode everything correctly for azure to 
        process.
        '''