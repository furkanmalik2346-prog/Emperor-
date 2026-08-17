"""Unit tests for the FloodTracker rate-limiting helper in Main."""
import Main
from Main import FloodTracker


class TestFloodState:
    def test_new_tracker_not_flooded(self):
        ft = FloodTracker()
        assert ft.flooded(1) is False
        assert ft.remaining(1) == 0.0

    def test_mark_sets_flooded(self):
        ft = FloodTracker()
        ft.mark(1, 2.0)
        assert ft.flooded(1) is True
        assert 0.0 < ft.remaining(1) <= 2.0

    def test_mark_is_capped_at_flood_cap(self):
        ft = FloodTracker()
        ft.mark(1, 999.0)
        assert ft.remaining(1) <= FloodTracker.FLOOD_CAP + 0.01

    def test_clear_removes_flood(self):
        ft = FloodTracker()
        ft.mark(1, 2.0)
        ft.clear(1)
        assert ft.flooded(1) is False

    def test_expired_flood_reads_false(self, monkeypatch):
        ft = FloodTracker()
        t = [1000.0]
        monkeypatch.setattr(Main.time, "monotonic", lambda: t[0])
        ft.mark(1, 2.0)
        assert ft.flooded(1) is True
        t[0] += 5.0  # advance past the (capped) window
        assert ft.flooded(1) is False


class TestFloodRate:
    def test_rate_counts_records(self):
        ft = FloodTracker()
        for _ in range(5):
            ft.record(7)
        assert ft.rate(7) == 5

    def test_near_limit_triggers_at_soft_limit(self):
        ft = FloodTracker()
        for _ in range(FloodTracker.SOFT_LIMIT):
            ft.record(3)
        assert ft.near_limit(3) is True

    def test_not_near_limit_below_threshold(self):
        ft = FloodTracker()
        for _ in range(FloodTracker.SOFT_LIMIT - 1):
            ft.record(3)
        assert ft.near_limit(3) is False

    def test_old_records_drop_out_of_window(self, monkeypatch):
        ft = FloodTracker()
        t = [1000.0]
        monkeypatch.setattr(Main.time, "monotonic", lambda: t[0])
        ft.record(9)
        t[0] += FloodTracker.RATE_WIN + 10  # move beyond the rate window
        ft.record(9)
        assert ft.rate(9) == 1
