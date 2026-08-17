"""Unit tests for the JSON persistence helpers in Main."""
import json

import Main


class TestLoadJson:
    def test_returns_default_when_missing(self, tmp_path):
        path = tmp_path / "nope.json"
        default = {"a": 1}
        assert Main._load_json(str(path), default) is default

    def test_reads_existing_json(self, tmp_path):
        path = tmp_path / "data.json"
        path.write_text(json.dumps({"x": [1, 2, 3]}))
        assert Main._load_json(str(path), {}) == {"x": [1, 2, 3]}

    def test_returns_default_on_invalid_json(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text("{not valid json")
        assert Main._load_json(str(path), []) == []


class TestSaveJson:
    def test_round_trip(self, tmp_path):
        path = tmp_path / "out.json"
        data = {"groups": [1, 2], "flag": True}
        Main._save_json(str(path), data)
        assert json.loads(path.read_text()) == data

    def test_save_then_load(self, tmp_path):
        path = tmp_path / "rt.json"
        data = [10, 20, 30]
        Main._save_json(str(path), data)
        assert Main._load_json(str(path), None) == data

    def test_save_failure_is_swallowed(self):
        # A non-existent directory makes open() fail; _save_json must not raise.
        Main._save_json("/no/such/dir/x.json", {"a": 1})
