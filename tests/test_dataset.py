# tests/test_dataset.py
import pytest
import torch
from ml.dataset import LotteryDataset, is_oos_split

DRAWS = [(f"2024-01-{i:02d}", [1, 2, 3, 4, 5]) for i in range(1, 11)]  # 10 draws


def test_default_ratio_splits_80_20():
    is_draws, oos_draws = is_oos_split(DRAWS)
    assert len(is_draws) == 8
    assert len(oos_draws) == 2


def test_oos_takes_latest_draws():
    is_draws, oos_draws = is_oos_split(DRAWS, oos_ratio=0.3)
    assert oos_draws == DRAWS[-3:]
    assert is_draws == DRAWS[:-3]


def test_zero_ratio_returns_all_in_sample():
    is_draws, oos_draws = is_oos_split(DRAWS, oos_ratio=0.0)
    assert is_draws == DRAWS
    assert oos_draws == []


def test_small_dataset_rounds_down():
    # 3 draws * 0.2 = 0.6 → int() truncates to 0 OOS
    small = DRAWS[:3]
    is_draws, oos_draws = is_oos_split(small, oos_ratio=0.2)
    assert len(is_draws) == 3
    assert len(oos_draws) == 0


def test_empty_input():
    assert is_oos_split([]) == ([], [])


def test_invalid_ratio_raises():
    with pytest.raises(ValueError):
        is_oos_split(DRAWS, oos_ratio=1.0)
    with pytest.raises(ValueError):
        is_oos_split(DRAWS, oos_ratio=-0.1)


# --- LotteryDataset --------------------------------------------------------

DRAWS_539 = [(f"2024-01-{i:02d}", [(i % 39) + 1,
                                   ((i + 1) % 39) + 1,
                                   ((i + 2) % 39) + 1,
                                   ((i + 3) % 39) + 1,
                                   ((i + 4) % 39) + 1])
             for i in range(1, 51)]  # 50 draws of 5 numbers in [1, 39]


def test_dataset_length_accounts_for_context_window():
    ds = LotteryDataset(DRAWS_539, context_len=10, num_range=(1, 39))
    # 50 draws, context=10 → samples = 50 - 10 = 40
    assert len(ds) == 40


def test_dataset_length_zero_when_too_few_draws():
    ds = LotteryDataset(DRAWS_539[:5], context_len=10, num_range=(1, 39))
    assert len(ds) == 0


def test_dataset_item_shapes_are_correct():
    ds = LotteryDataset(DRAWS_539, context_len=10, num_range=(1, 39))
    ctx, target = ds[0]
    assert ctx.shape == (10, 39)  # (context_len, num_count)
    assert target.shape == (39,)


def test_dataset_item_is_multihot_with_correct_count():
    ds = LotteryDataset(DRAWS_539, context_len=10, num_range=(1, 39))
    ctx, target = ds[0]
    # Each context row has exactly 5 ones (5 balls per draw); target also 5 ones
    assert (ctx.sum(dim=1) == 5).all()
    assert target.sum().item() == 5
    # All entries are 0 or 1
    assert torch.all((ctx == 0) | (ctx == 1))


def test_dataset_truncates_to_analyze_count_for_special_ball_games():
    # 638-shaped: 6 regular + 1 special, but model should only see regulars
    draws_638 = [(f"2024-01-{i:02d}", [1, 2, 3, 4, 5, 6, 7]) for i in range(1, 21)]
    ds = LotteryDataset(draws_638, context_len=5, num_range=(1, 38),
                        analyze_count=6)
    ctx, target = ds[0]
    # 6 regulars set; the special (7) outside the 1..38 range still gets set
    # because 7 is within (1, 38). What matters: only 6 numbers per row.
    assert (ctx.sum(dim=1) == 6).all()
    assert target.sum().item() == 6
