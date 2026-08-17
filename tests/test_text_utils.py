"""Unit tests for the pure text-transformation helpers in Main."""
import Main


class TestToBoldItalic:
    def test_uppercase_maps_to_math_bold_italic(self):
        assert Main._to_bold_italic("A") == chr(0x1D468)
        assert Main._to_bold_italic("Z") == chr(0x1D468 + 25)

    def test_lowercase_maps_to_math_bold_italic(self):
        assert Main._to_bold_italic("a") == chr(0x1D482)
        assert Main._to_bold_italic("z") == chr(0x1D482 + 25)

    def test_non_letters_pass_through_unchanged(self):
        assert Main._to_bold_italic("1 !-") == "1 !-"

    def test_empty_string(self):
        assert Main._to_bold_italic("") == ""

    def test_mixed_string_length_preserved(self):
        src = "Goku 99!"
        assert len(Main._to_bold_italic(src)) == len(src)


class TestRandomDecorations:
    def test_rnd_emoji_is_from_pool(self):
        for _ in range(50):
            assert Main.rnd_emoji() in Main.RANDOM_EMOJIS

    def test_rnd_suffix_wraps_a_suffix_emoji(self):
        for _ in range(50):
            s = Main.rnd_suffix()
            assert s.startswith(" 𓂃")
            assert s.endswith("་༘")
            assert any(e in s for e in Main.SUFFIX_EMOJIS)


class TestNormalizeCmd:
    def test_plain_ascii_unchanged(self):
        assert Main._normalize_cmd("nc") == "nc"

    def test_bold_unicode_normalized_to_ascii(self):
        assert Main._normalize_cmd("𝐧𝐜") == "nc"

    def test_bold_digits_normalized(self):
        assert Main._normalize_cmd("𝟏𝟐𝟑") == "123"

    def test_mixed_case_and_uppercase_bold(self):
        assert Main._normalize_cmd("𝐒𝐭𝐨𝐩") == "Stop"


class TestSplitText:
    def test_short_text_single_chunk(self):
        assert Main._split_text("hello world") == ["hello world"]

    def test_empty_text_returns_single_empty_chunk(self):
        assert Main._split_text("") == [""]

    def test_long_text_split_into_multiple_chunks(self):
        text = "\n".join(["x" * 10 for _ in range(20)])
        chunks = Main._split_text(text, limit=30)
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 30

    def test_chunks_recombine_to_original_lines(self):
        text = "line1\nline2\nline3"
        chunks = Main._split_text(text, limit=12)
        recombined = "\n".join(chunks)
        assert recombined == text

    def test_line_longer_than_limit_still_returned(self):
        text = "a" * 100
        chunks = Main._split_text(text, limit=20)
        assert "".join(chunks) == text
