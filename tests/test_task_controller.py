"""Unit tests for the async TaskController helper in Main."""
import asyncio

import pytest

from Main import TaskController


class TestKey:
    def test_key_format(self):
        tc = TaskController()
        assert tc._k(123, "blaze") == "123::blaze"


class TestRunningState:
    def test_not_running_initially(self):
        tc = TaskController()
        assert tc.running(1, "blaze") is False


@pytest.mark.asyncio
class TestStartStop:
    async def test_start_marks_running_then_stop_clears(self):
        tc = TaskController()

        async def factory(stop_event):
            await stop_event.wait()

        await tc.start(1, "loop", factory)
        assert tc.running(1, "loop") is True

        stopped = await tc.stop(1, "loop")
        assert stopped is True
        assert tc.running(1, "loop") is False

    async def test_stop_returns_false_when_nothing_running(self):
        tc = TaskController()
        assert await tc.stop(1, "loop") is False

    async def test_start_replaces_existing_task(self):
        tc = TaskController()

        async def factory(stop_event):
            await stop_event.wait()

        await tc.start(1, "loop", factory)
        first = tc.tasks[tc._k(1, "loop")]
        await tc.start(1, "loop", factory)
        second = tc.tasks[tc._k(1, "loop")]
        assert first is not second
        await tc.stop(1, "loop")

    async def test_stop_all_stops_every_type(self):
        tc = TaskController()

        async def factory(stop_event):
            await stop_event.wait()

        await tc.start(2, "a", factory)
        await tc.start(2, "b", factory)
        count = await tc.stop_all(2)
        assert count == 2
        assert tc.running(2, "a") is False
        assert tc.running(2, "b") is False

    async def test_finished_task_auto_deregisters(self):
        tc = TaskController()

        async def factory(stop_event):
            return

        await tc.start(3, "quick", factory)
        await asyncio.sleep(0.05)
        assert tc.running(3, "quick") is False
