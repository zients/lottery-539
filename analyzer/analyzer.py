# analyzer/analyzer.py
import random


def frequency(draws: list[tuple]) -> dict[int, int]:
    counts = {n: 0 for n in range(1, 40)}
    for _, numbers in draws:
        for n in numbers:
            counts[n] += 1
    return counts


def hot_numbers(draws: list[tuple], window: int = 30) -> list[int]:
    recent = draws[-window:] if len(draws) >= window else draws
    freq = frequency(recent)
    sorted_nums = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [n for n, _ in sorted_nums[:5]]


def cold_numbers(draws: list[tuple], window: int = 30) -> list[int]:
    recent = draws[-window:] if len(draws) >= window else draws
    freq = frequency(recent)
    hot = set(hot_numbers(draws, window))
    sorted_nums = sorted(
        [(n, c) for n, c in freq.items() if n not in hot],
        key=lambda x: x[1]
    )
    return [n for n, _ in sorted_nums[:5]]


def _valid_combo(numbers: list[int]) -> bool:
    odd_count = sum(1 for n in numbers if n % 2 != 0)
    total = sum(numbers)
    return odd_count in (2, 3) and 80 <= total <= 120


def recommend(draws: list[tuple]) -> list[list[int]]:
    freq = frequency(draws)
    candidates = sorted(range(1, 40), key=lambda n: freq[n], reverse=True)[:20]
    results = []
    attempts = 0
    while len(results) < 3 and attempts < 1000:
        attempts += 1
        combo = sorted(random.sample(candidates, 5))
        if _valid_combo(combo) and combo not in results:
            results.append(combo)
    # fallback if not enough valid combos from top-20
    while len(results) < 3:
        combo = sorted(random.sample(range(1, 40), 5))
        if _valid_combo(combo) and combo not in results:
            results.append(combo)
    return results
