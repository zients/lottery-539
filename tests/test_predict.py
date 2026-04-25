# tests/test_predict.py
from unittest.mock import patch
import torch

from ml import predict as predict_mod
from ml.model import LotteryTransformer
from ml.predict import checkpoint_path, has_model, predict


def test_checkpoint_path_includes_lottery_type(tmp_path, monkeypatch):
    monkeypatch.setattr(predict_mod, "CHECKPOINT_DIR", tmp_path)
    p = checkpoint_path("539")
    assert p.parent == tmp_path
    assert "539" in p.name
    assert p.suffix == ".pt"


def test_has_model_false_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(predict_mod, "CHECKPOINT_DIR", tmp_path)
    assert has_model("539") is False


def test_has_model_true_when_checkpoint_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(predict_mod, "CHECKPOINT_DIR", tmp_path)
    (tmp_path / "539_best.pt").write_bytes(b"")
    assert has_model("539") is True


def test_predict_returns_n_combos_with_correct_shape(tmp_path, monkeypatch):
    """Train a tiny model, save it, then predict — covers the full inference path."""
    monkeypatch.setattr(predict_mod, "CHECKPOINT_DIR", tmp_path)

    num_range = (1, 39)
    num_count = 39
    model = LotteryTransformer(num_count)
    torch.save(model.state_dict(), tmp_path / "539_best.pt")

    # 30 draws of 5 numbers each (matches default context_len=30)
    draws = [(f"2024-01-{i:02d}", [1, 2, 3, 4, 5]) for i in range(1, 31)]
    combos = predict(draws, "539", num_range=num_range, analyze_count=5, pick=5)

    assert len(combos) == 3
    for combo in combos:
        assert len(combo) == 5
        assert all(num_range[0] <= n <= num_range[1] for n in combo)
        assert combo == sorted(combo)


def test_predict_raises_when_too_few_draws(tmp_path, monkeypatch):
    monkeypatch.setattr(predict_mod, "CHECKPOINT_DIR", tmp_path)
    model = LotteryTransformer(39)
    torch.save(model.state_dict(), tmp_path / "539_best.pt")

    # Only 5 draws but context_len defaults to 30
    draws = [(f"2024-01-{i:02d}", [1, 2, 3, 4, 5]) for i in range(1, 6)]
    try:
        predict(draws, "539", num_range=(1, 39), analyze_count=5, pick=5)
    except ValueError as e:
        assert "30" in str(e)
        return
    raise AssertionError("expected ValueError")
