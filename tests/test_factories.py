"""Unit tests for the message-generating factory helpers in Main.

Each factory returns a zero-argument callable that produces a decorated line.
The lines embed the caller's text, are capped at 255 characters, and avoid
emitting the exact same string twice in a row.
"""
import random

import Main


def setup_function(_):
    random.seed(1234)


def _emit(factory_callable, n=5):
    return [factory_callable() for _ in range(n)]


class TestSimpleFactories:
    def test_wrap_factory_embeds_text(self):
        f = Main._wrap_factory("hello")
        for line in _emit(f):
            assert "hello" in line
            assert len(line) <= 255

    def test_randomcod_factory_embeds_text(self):
        f = Main._randomcod_factory("boom")
        for line in _emit(f):
            assert "boom" in line
            assert len(line) <= 255

    def test_pure_nc_factory_embeds_text(self):
        f = Main._pure_nc_factory("zeno")
        for line in _emit(f):
            assert "zeno" in line
            assert len(line) <= 255

    def test_db_factory_embeds_text(self):
        f = Main._db_factory("ki", 0)
        for line in _emit(f):
            assert "ki" in line
            assert len(line) <= 255

    def test_wave_factory_embeds_text(self):
        f = Main._wave_factory("surf")
        for line in _emit(f):
            assert "surf" in line
            assert len(line) <= 255

    def test_hakai_factory_starts_with_text(self):
        f = Main._hakai_nc_factory("PREFIX")
        for line in _emit(f):
            assert line.startswith("PREFIX")
            assert len(line) <= 255


class TestLeanFactory:
    def test_lean_factory_first_line_is_bare_text(self):
        f = Main._lean_nc_factory("clean")
        assert f() == "clean"

    def test_lean_factory_avoids_consecutive_duplicates(self):
        f = Main._lean_nc_factory("clean")
        a, b = f(), f()
        assert a != b


class TestFontFactory:
    def test_bold_style_translates_text(self):
        f = Main._font_factory("abc", "bold")
        bold = "abc".translate(Main._BOLD_MAP)
        assert any(bold in line for line in _emit(f))

    def test_unknown_style_keeps_plain_text(self):
        f = Main._font_factory("plain", "nope")
        assert all("plain" in line for line in _emit(f))


class TestFriendFactory:
    def test_friend_factory_embeds_text_and_name(self):
        f = Main._friend_nc_factory("GOKU", "attack")
        uni = Main.FRIENDS_UNI["GOKU"]
        for line in _emit(f):
            assert "attack" in line
            assert uni in line
            assert len(line) <= 255


class TestGokuVegetaFactories:
    def test_goku_factory(self):
        f = Main._goku_factory("power")
        for line in _emit(f):
            assert "power" in line
            assert "𝑮𝑶𝑲𝑼" in line

    def test_vegeta_factory(self):
        f = Main._vegeta_factory("prince")
        for line in _emit(f):
            assert "prince" in line
            assert "𝑽𝑬𝑮𝑬𝑻𝑨" in line


class TestMgcFactories:
    def test_mgc_fire_embeds_text(self):
        f = Main._mgc_fire_factory("blaze")
        for line in _emit(f):
            assert "blaze" in line
            assert len(line) <= 255

    def test_mgc_war_embeds_text(self):
        f = Main._mgc_war_factory("clash")
        for line in _emit(f):
            assert "clash" in line
            assert len(line) <= 255

    def test_mgc_surge_bolds_text(self):
        f = Main._mgc_surge_factory("volt")
        bold = "volt".translate(Main._BOLD_MAP)
        for line in _emit(f):
            assert bold in line
            assert len(line) <= 255


class TestCustomTemplateFactory:
    def test_placeholders_are_replaced(self):
        f = Main._custom_template_factory("[{t}] #{n} {w}", "hey")
        line = f()
        assert "hey" in line
        assert "#1" in line
        assert any(w in line for w in Main._HAKAI_WORDS)

    def test_counter_increments(self):
        f = Main._custom_template_factory("{n}", "x")
        assert f() == "1"
        assert f() == "2"
