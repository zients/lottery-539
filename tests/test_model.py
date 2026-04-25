# tests/test_model.py
import torch
from ml.model import LotteryTransformer


def test_forward_output_shape_matches_num_count():
    model = LotteryTransformer(num_count=39)
    x = torch.zeros(4, 30, 39)  # (batch, context_len, num_count)
    out = model(x)
    assert out.shape == (4, 39)


def test_forward_works_for_smaller_lottery():
    # 638 special-ball range is (1, 8) → num_count=8; covers smallest case
    model = LotteryTransformer(num_count=8)
    x = torch.zeros(2, 30, 8)
    out = model(x)
    assert out.shape == (2, 8)


def test_logits_are_unconstrained_real_values():
    # Output is logits (no sigmoid yet); should not be bounded to [0, 1]
    model = LotteryTransformer(num_count=39)
    x = torch.randn(4, 30, 39).abs()  # any input
    out = model(x)
    assert out.dtype == torch.float32
    # sanity: at least some logit is outside [0, 1] for random init + random input
    # (this is statistically near-certain; deterministic seeds optional)
    assert (out < 0).any() or (out > 1).any()


def test_gradients_flow_through_model():
    model = LotteryTransformer(num_count=39)
    x = torch.zeros(2, 30, 39, requires_grad=False)
    out = model(x)
    loss = out.sum()
    loss.backward()
    # At least one parameter must have a non-None gradient
    grads = [p.grad for p in model.parameters() if p.grad is not None]
    assert len(grads) > 0
    assert any(g.abs().sum().item() > 0 for g in grads)


def test_handles_short_context():
    # context_len smaller than max_context default — must still work
    model = LotteryTransformer(num_count=39, max_context=512)
    x = torch.zeros(1, 5, 39)
    out = model(x)
    assert out.shape == (1, 39)
