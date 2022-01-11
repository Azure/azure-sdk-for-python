class CannotOverwriteExistingCassetteException(Exception):
    def __init__(self, *args, **kwargs):
        self.cassette = kwargs["cassette"]
        self.failed_request = kwargs["failed_request"]
        message = self._get_message(kwargs["cassette"], kwargs["failed_request"])
        super(CannotOverwriteExistingCassetteException, self).__init__(message)

    @staticmethod
    def _get_message(cassette, failed_request):
        """Get the final message related to the exception"""
        # Get the similar requests in the cassette that
        # have match the most with the request.
        best_matches = cassette.find_requests_with_most_matches(failed_request)
        if best_matches:
            # Build a comprehensible message to put in the exception.
            best_matches_msg = "Found {} similar requests with {} different matcher(s) :\n".format(
                len(best_matches), len(best_matches[0][2])
            )

            for idx, best_match in enumerate(best_matches, start=1):
                request, succeeded_matchers, failed_matchers_assertion_msgs = best_match
                best_matches_msg += (
                    "\n%s - (%r).\n"
                    "Matchers succeeded : %s\n"
                    "Matchers failed :\n" % (idx, request, succeeded_matchers)
                )
                for failed_matcher, assertion_msg in failed_matchers_assertion_msgs:
                    best_matches_msg += "%s - assertion failure :\n" "%s\n" % (failed_matcher, assertion_msg)
        else:
            best_matches_msg = "No similar requests, that have not been played, found."
        return (
            "Can't overwrite existing cassette (%r) in "
            "your current record mode (%r).\n"
            "No match for the request (%r) was found.\n"
            "%s" % (cassette._path, cassette.record_mode, failed_request, best_matches_msg)
        )


class UnhandledHTTPRequestError(KeyError):
    """Raised when a cassette does not contain the request we want."""

    pass
