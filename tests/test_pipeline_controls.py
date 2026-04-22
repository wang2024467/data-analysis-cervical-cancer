from pathlib import Path

from src.pipeline.run_sql import evaluate_quality_gate, pick_raw_csv


class _FakeQuery:
    def __init__(self, value):
        self._value = value

    def fetchone(self):
        return (self._value,)


class _FakeConn:
    def __init__(self, max_null, range_sum, consistency_sum):
        self.max_null = max_null
        self.range_sum = range_sum
        self.consistency_sum = consistency_sum

    def sql(self, query: str):
        q = query.lower()
        if "max(null_rate)" in q:
            return _FakeQuery(self.max_null)
        if "check_range_violations" in q:
            return _FakeQuery(self.range_sum)
        if "check_consistency_violations" in q:
            return _FakeQuery(self.consistency_sum)
        raise AssertionError(f"Unexpected query: {query}")


class _FakeLogger:
    def info(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None


def test_quality_gate_passes_within_thresholds() -> None:
    conn = _FakeConn(max_null=0.10, range_sum=0, consistency_sum=0)
    config = {
        "quality_gate": {
            "max_null_rate": 0.25,
            "allow_range_violations": 0,
            "allow_consistency_violations": 0,
        }
    }
    evaluate_quality_gate(conn, config, _FakeLogger())


def test_quality_gate_fails_on_null_threshold() -> None:
    conn = _FakeConn(max_null=0.90, range_sum=0, consistency_sum=0)
    config = {"quality_gate": {"max_null_rate": 0.25, "allow_range_violations": 0, "allow_consistency_violations": 0}}

    try:
        evaluate_quality_gate(conn, config, _FakeLogger())
        assert False, "Expected ValueError when quality gate fails"
    except ValueError as e:
        assert "max_null_rate_exceeded" in str(e)


def test_pick_raw_csv_returns_latest_file(tmp_path: Path) -> None:
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("x\n1\n", encoding="utf-8")
    b.write_text("x\n2\n", encoding="utf-8")

    latest = pick_raw_csv(tmp_path)
    assert latest is not None
    assert latest.name in {"a.csv", "b.csv"}


def test_pick_raw_csv_none_when_empty(tmp_path: Path) -> None:
    assert pick_raw_csv(tmp_path) is None


def test_pick_raw_csv_ignores_gitkeep(tmp_path: Path) -> None:
    (tmp_path / ".gitkeep").write_text("", encoding="utf-8")
    assert pick_raw_csv(tmp_path) is None


def test_pick_raw_csv_prefers_csv_even_with_gitkeep(tmp_path: Path) -> None:
    (tmp_path / ".gitkeep").write_text("", encoding="utf-8")
    csv = tmp_path / "real_input.csv"
    csv.write_text("x\n1\n", encoding="utf-8")
    selected = pick_raw_csv(tmp_path)
    assert selected == csv
