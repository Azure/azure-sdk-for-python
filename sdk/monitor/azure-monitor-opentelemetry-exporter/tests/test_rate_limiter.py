# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import threading
import time
import unittest

from azure.monitor.opentelemetry.exporter.export._rate_limiter import (
    _TokenBucketRateLimiter,
    _DEFAULT_MAX_ENVELOPES_PER_SECOND,
    _MIN_MAX_ENVELOPES_PER_SECOND,
)


class TestTokenBucketRateLimiter(unittest.TestCase):
    """Unit tests for _TokenBucketRateLimiter."""

    def test_constructor_valid(self):
        limiter = _TokenBucketRateLimiter(100)
        self.assertIsNotNone(limiter)

    def test_constructor_rejects_zero(self):
        with self.assertRaises(ValueError):
            _TokenBucketRateLimiter(0)

    def test_constructor_rejects_negative(self):
        with self.assertRaises(ValueError):
            _TokenBucketRateLimiter(-1)

    def test_constructor_minimum(self):
        limiter = _TokenBucketRateLimiter(_MIN_MAX_ENVELOPES_PER_SECOND)
        self.assertIsNotNone(limiter)

    def test_consume_zero_returns_zero(self):
        limiter = _TokenBucketRateLimiter(100)
        self.assertEqual(limiter.try_consume(0), 0)

    def test_consume_negative_returns_zero(self):
        limiter = _TokenBucketRateLimiter(100)
        self.assertEqual(limiter.try_consume(-5), 0)

    def test_full_bucket_grants_all(self):
        limiter = _TokenBucketRateLimiter(100)
        # Bucket starts full at 100 tokens
        granted = limiter.try_consume(50)
        self.assertEqual(granted, 50)

    def test_full_bucket_grants_up_to_capacity(self):
        limiter = _TokenBucketRateLimiter(100)
        # Request more than capacity
        granted = limiter.try_consume(200)
        self.assertEqual(granted, 100)

    def test_bucket_depletes(self):
        limiter = _TokenBucketRateLimiter(100)
        # Drain the bucket
        granted1 = limiter.try_consume(100)
        self.assertEqual(granted1, 100)
        # Immediately request more - bucket should be empty (or nearly so)
        granted2 = limiter.try_consume(100)
        # Should get very few or zero tokens
        self.assertLessEqual(granted2, 5)

    def test_bucket_refills_over_time(self):
        limiter = _TokenBucketRateLimiter(1000)
        # Drain the bucket
        limiter.try_consume(1000)
        # Wait for partial refill
        time.sleep(0.1)
        granted = limiter.try_consume(1000)
        # Should have refilled ~100 tokens (1000/sec * 0.1sec)
        self.assertGreater(granted, 50)
        self.assertLessEqual(granted, 200)

    def test_bucket_caps_at_capacity(self):
        limiter = _TokenBucketRateLimiter(100)
        # Wait a while - bucket should not exceed capacity
        time.sleep(0.2)
        granted = limiter.try_consume(200)
        self.assertEqual(granted, 100)

    def test_thread_safety(self):
        limiter = _TokenBucketRateLimiter(1000)
        results = []
        errors = []

        def consume():
            try:
                for _ in range(100):
                    limiter.try_consume(1)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=consume) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len(errors), 0)

    def test_default_constant_value(self):
        self.assertEqual(_DEFAULT_MAX_ENVELOPES_PER_SECOND, 10000)


class TestBaseExporterRateLimiting(unittest.TestCase):
    """Integration tests for rate limiting in BaseExporter."""

    @classmethod
    def setUpClass(cls):
        import os

        os.environ["APPINSIGHTS_INSTRUMENTATIONKEY"] = (
            "1234abcd-5678-4efa-8abc-1234567890ab"
        )
        os.environ["APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL"] = "true"
        os.environ["APPLICATIONINSIGHTS_SDKSTATS_DISABLED"] = "true"

    def test_rate_limiter_initialized_by_default(self):
        from azure.monitor.opentelemetry.exporter.export._base import BaseExporter

        base = BaseExporter(disable_offline_storage=True)
        self.assertIsNotNone(base._rate_limiter)

    def test_rate_limiter_disabled_with_zero(self):
        from azure.monitor.opentelemetry.exporter.export._base import BaseExporter

        base = BaseExporter(disable_offline_storage=True, max_envelopes_per_second=0)
        self.assertIsNone(base._rate_limiter)

    def test_rate_limiter_rejects_negative(self):
        from azure.monitor.opentelemetry.exporter.export._base import BaseExporter

        with self.assertRaises(ValueError):
            BaseExporter(disable_offline_storage=True, max_envelopes_per_second=-1)

    def test_rate_limiter_custom_value(self):
        from azure.monitor.opentelemetry.exporter.export._base import BaseExporter

        base = BaseExporter(disable_offline_storage=True, max_envelopes_per_second=500)
        self.assertIsNotNone(base._rate_limiter)
        self.assertEqual(base._rate_limiter._max_per_second, 500.0)

    def test_transmit_rate_limited_batch_returns_retryable(self):
        """When the entire batch is rejected by the rate limiter, _transmit returns FAILED_RETRYABLE."""
        from unittest import mock
        from datetime import datetime
        from azure.monitor.opentelemetry.exporter.export._base import (
            BaseExporter,
            ExportResult,
        )
        from azure.monitor.opentelemetry.exporter._generated.exporter.models import (
            TelemetryItem,
        )

        base = BaseExporter(disable_offline_storage=True, max_envelopes_per_second=10)
        # Drain the bucket
        base._rate_limiter.try_consume(10)

        envelopes = [TelemetryItem(name="Test", time=datetime.now()) for _ in range(5)]
        result = base._transmit(envelopes)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmit_partial_rate_limit_sends_admitted(self):
        """When the rate limiter admits only part of the batch, the admitted portion is sent."""
        from unittest import mock
        from datetime import datetime
        from azure.monitor.opentelemetry.exporter.export._base import (
            BaseExporter,
            ExportResult,
        )
        from azure.monitor.opentelemetry.exporter._generated.exporter.models import (
            TelemetryItem,
            TrackResponse,
        )

        base = BaseExporter(disable_offline_storage=True, max_envelopes_per_second=5)
        # Drain bucket, then let a few tokens refill
        base._rate_limiter.try_consume(5)

        # Manually set tokens to 3 for deterministic test
        base._rate_limiter._tokens = 3

        envelopes = [TelemetryItem(name="Test", time=datetime.now()) for _ in range(10)]

        with mock.patch.object(base.client, "track") as mock_track:
            mock_track.return_value = TrackResponse(items_received=3, items_accepted=3)
            result = base._transmit(envelopes)
            # Should have sent only 3 envelopes
            self.assertEqual(len(mock_track.call_args[0][0]), 3)
            self.assertEqual(result, ExportResult.SUCCESS)
            # envelopes list should be mutated in-place to only contain the admitted portion
            self.assertEqual(len(envelopes), 3)

    def test_transmit_partial_rate_limit_no_storage_drops_overflow(self):
        """When storage is disabled and overflow occurs, overflow is dropped and logged."""
        from unittest import mock
        from datetime import datetime
        from azure.monitor.opentelemetry.exporter.export._base import (
            BaseExporter,
            ExportResult,
        )
        from azure.monitor.opentelemetry.exporter._generated.exporter.models import (
            TelemetryItem,
            TrackResponse,
        )

        base = BaseExporter(disable_offline_storage=True, max_envelopes_per_second=5)
        base._rate_limiter._tokens = 3

        envelopes = [TelemetryItem(name="Test", time=datetime.now()) for _ in range(10)]

        with mock.patch.object(base.client, "track") as mock_track:
            mock_track.return_value = TrackResponse(items_received=3, items_accepted=3)
            # Should not raise even with no storage
            result = base._transmit(envelopes)
            self.assertEqual(result, ExportResult.SUCCESS)
            # Only admitted envelopes remain
            self.assertEqual(len(envelopes), 3)

    def test_stats_exporter_bypasses_rate_limiter(self):
        """Stats exporters should not be rate limited."""
        from unittest import mock
        from datetime import datetime
        from azure.monitor.opentelemetry.exporter.export._base import (
            BaseExporter,
            ExportResult,
        )
        from azure.monitor.opentelemetry.exporter._generated.exporter.models import (
            TelemetryItem,
            TrackResponse,
        )

        base = BaseExporter(disable_offline_storage=True, max_envelopes_per_second=1)
        base._is_sdkstats = True  # Mark as stats exporter
        # Drain the rate limiter
        base._rate_limiter.try_consume(1)

        envelopes = [TelemetryItem(name="Test", time=datetime.now()) for _ in range(5)]

        with mock.patch.object(base.client, "track") as mock_track:
            mock_track.return_value = TrackResponse(items_received=5, items_accepted=5)
            result = base._transmit(envelopes)
            # All 5 should be sent despite rate limiter being empty
            self.assertEqual(len(mock_track.call_args[0][0]), 5)
            self.assertEqual(result, ExportResult.SUCCESS)

    def test_redirect_does_not_double_consume_rate_limiter(self):
        """When _transmit recurses on a 307/308 redirect, rate limiting should be skipped."""
        from unittest import mock
        from datetime import datetime
        from azure.core.exceptions import HttpResponseError
        from azure.monitor.opentelemetry.exporter.export._base import (
            BaseExporter,
            ExportResult,
        )
        from azure.monitor.opentelemetry.exporter._generated.exporter.models import (
            TelemetryItem,
            TrackResponse,
        )

        base = BaseExporter(disable_offline_storage=True, max_envelopes_per_second=5)

        envelopes = [TelemetryItem(name="Test", time=datetime.now()) for _ in range(5)]

        # First call raises a 307 redirect, second call succeeds
        mock_response = mock.Mock()
        mock_response.headers = {"location": "https://redirected.example.com/v2/track"}
        redirect_error = HttpResponseError(
            message="Temporary Redirect",
            response=mock_response,
        )
        redirect_error.status_code = 307

        with mock.patch.object(base.client, "track") as mock_track:
            mock_track.side_effect = [
                redirect_error,
                TrackResponse(items_received=5, items_accepted=5),
            ]
            result = base._transmit(envelopes)
            # Should succeed after redirect
            self.assertEqual(result, ExportResult.SUCCESS)
            # track should have been called twice (original + redirect)
            self.assertEqual(mock_track.call_count, 2)


if __name__ == "__main__":
    unittest.main()
