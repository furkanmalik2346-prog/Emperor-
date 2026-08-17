"""Unit tests for small argument/update helpers in Main."""
import types

import Main


def _ctx(args):
    return types.SimpleNamespace(args=args)


class TestArgHelpers:
    def test_get_args_returns_list(self):
        assert Main._get_args(_ctx(["a", "b"])) == ["a", "b"]

    def test_get_args_none_becomes_empty(self):
        assert Main._get_args(_ctx(None)) == []

    def test_txt_arg_joins_and_strips(self):
        assert Main._txt_arg(_ctx(["hello", "world"])) == "hello world"

    def test_txt_arg_empty(self):
        assert Main._txt_arg(_ctx([])) == ""


class TestDedupKey:
    def test_returns_chat_and_message_id(self):
        upd = types.SimpleNamespace(
            message=types.SimpleNamespace(chat_id=10, message_id=99),
            edited_message=None,
        )
        assert Main._dedup_key(upd) == (10, 99)

    def test_uses_edited_message_when_no_message(self):
        upd = types.SimpleNamespace(
            message=None,
            edited_message=types.SimpleNamespace(chat_id=5, message_id=7),
        )
        assert Main._dedup_key(upd) == (5, 7)

    def test_returns_none_without_any_message(self):
        upd = types.SimpleNamespace(message=None, edited_message=None)
        assert Main._dedup_key(upd) is None


class TestMisc:
    def test_last_is_fresh_single_none_list(self):
        a = Main._last()
        assert a == [None]
        a[0] = "x"
        assert Main._last() == [None]  # independent list each call

    def test_build_rcod_lines_covers_all_friends_plus_random(self):
        lines = Main._build_rcod_lines()
        assert len(lines) == len(Main.FRIENDS) + 1
        assert "𝑷𝑼𝑹𝑬" in lines[-1]

    def test_bots_filters_none(self, monkeypatch):
        monkeypatch.setattr(Main, "all_bot_instances", [object(), None, object()])
        assert len(Main._bots()) == 2
