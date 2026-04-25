# tests/test_train.py
import torch
from ml.train import coverage


def _make_logits(probs: list[list[float]]) -> torch.Tensor:
    """Build logits whose sigmoid yields the given probabilities."""
    p = torch.tensor(probs)
    # sigmoid^-1(p) = log(p / (1 - p)); avoid 0/1 with clamp
    p = p.clamp(1e-6, 1 - 1e-6)
    return torch.log(p / (1 - p))


def test_coverage_perfect_prediction_returns_one():
    # 2 samples, 5 classes; pick top 2; both targets fully inside top-2
    logits = _make_logits([
        [0.9, 0.9, 0.1, 0.1, 0.1],  # top-2 = {0, 1}
        [0.1, 0.1, 0.9, 0.9, 0.1],  # top-2 = {2, 3}
    ])
    targets = torch.tensor([
        [1, 1, 0, 0, 0],
        [0, 0, 1, 1, 0],
    ], dtype=torch.float)
    assert coverage(logits, targets, pick=2) == 1.0


def test_coverage_zero_when_no_overlap():
    logits = _make_logits([
        [0.9, 0.9, 0.1, 0.1, 0.1],  # top-2 = {0, 1}
    ])
    targets = torch.tensor([[0, 0, 1, 1, 0]], dtype=torch.float)
    assert coverage(logits, targets, pick=2) == 0.0


def test_coverage_partial_overlap():
    # top-2 picks {0, 1}; target is {0, 2} → 1 of 2 correct = 0.5
    logits = _make_logits([
        [0.9, 0.9, 0.1, 0.1, 0.1],
    ])
    targets = torch.tensor([[1, 0, 1, 0, 0]], dtype=torch.float)
    assert coverage(logits, targets, pick=2) == 0.5


def test_coverage_averages_over_batch():
    logits = _make_logits([
        [0.9, 0.9, 0.1, 0.1, 0.1],  # match {0, 1} fully → 1.0
        [0.9, 0.9, 0.1, 0.1, 0.1],  # match {2, 3} not at all → 0.0
    ])
    targets = torch.tensor([
        [1, 1, 0, 0, 0],
        [0, 0, 1, 1, 0],
    ], dtype=torch.float)
    assert coverage(logits, targets, pick=2) == 0.5
