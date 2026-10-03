"""Exercise installed-command behavior with recorded offline model requests."""
import json

import pytest

from structsynth.cli import main
from structsynth.llm import OpenAICompatibleClient


def test_demo_resume_replay_and_report_never_call_a_provider(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(OpenAICompatibleClient, "_http", lambda *_: pytest.fail("Unexpected network request"))
    output = tmp_path / "demo"
    assert main(["demo", "--output-dir", str(output), "--max-workers", "2"]) == 0
    source = next((output / "offline_demo").glob("20_shot/seed_42/*"))
    captured = {name: (source / name).read_bytes() for name in
                ("discovery_requests.jsonl", "generation_requests.jsonl", "synthetic.json", "metrics.json")}
    assert main(["demo", "--output-dir", str(output), "--max-workers", "2", "--resume"]) == 0
    for name, content in captured.items():
        assert (source / name).read_bytes() == content
    assert list((output / "summaries").glob("*/summary.csv"))
    assert main(["run", "--config", str(output / "demo_config.json"), "--replay-dir", str(source)]) == 0
    other = [path for path in source.parent.iterdir() if path != source]
    assert len(other) == 1
    replay = other[0]
    manifest = json.loads((replay / "manifest.json").read_text())
    assert manifest["identity"]["backend"]["kind"] == "replay"
    assert (replay / "synthetic.json").read_bytes() == captured["synthetic.json"]
    assert (replay / "metrics.json").read_bytes() == captured["metrics.json"]
    usage = json.loads((replay / "usage.json").read_text())
    for stage in ("discovery", "generation"):
        assert usage[stage]["api_requests"] == usage[stage]["total_tokens"] == 0
        assert usage[stage]["replayed_requests"] > 0
    for name, content in captured.items():
        assert (source / name).read_bytes() == content
    review = tmp_path / "review"
    assert main(["report", "--run-dirs", str(source), str(replay), "--output-dir", str(review)]) == 0
    summary = json.loads((review / "summary.json").read_text())
    assert len(summary["groups"]) == 4  # Two sizes, with independent backend provenance.
    assert all(group["metrics"]["downstream.auc_roc"]["valid_count"] == 1 for group in summary["groups"])
    assert "OFFLINE DEMO" in capsys.readouterr().out
