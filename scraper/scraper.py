# scraper/scraper.py
import requests
from datetime import date, datetime

API_URL = "https://api.taiwanlottery.com/TLCAPIWeB/Lottery/Daily539Result"
HEADERS = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
START_YEAR, START_MONTH = 2007, 1


def parse_draws(data: dict) -> list[tuple[str, list[int]]]:
    """Parse draw records from official Taiwan Lottery API response.

    Expected item format:
        {"lotteryDate": "2026-04-07T00:00:00", "drawNumberSize": [4, 8, 21, 27, 29], ...}
    """
    draws = []
    for item in data.get("daily539Res") or []:
        try:
            draw_date = item["lotteryDate"][:10]  # "2026-04-07T00:00:00" → "2026-04-07"
            numbers = item["drawNumberSize"]       # already sorted
            if len(numbers) == 5 and all(1 <= n <= 39 for n in numbers):
                draws.append((draw_date, numbers))
        except (KeyError, TypeError):
            continue
    return draws


def fetch_draws(start_month: str | None = None) -> list[tuple[str, list[int]]]:
    """Fetch all 539 draws from official API, month by month.

    Args:
        start_month: "YYYY-MM" to start from. Defaults to "2007-01".

    Returns:
        List of (date, numbers) tuples, oldest first.
    """
    if start_month:
        year, month = int(start_month[:4]), int(start_month[5:7])
    else:
        year, month = START_YEAR, START_MONTH

    today = date.today()
    all_draws = []

    while (year, month) <= (today.year, today.month):
        month_str = f"{year}-{month:02d}"
        response = requests.get(
            API_URL,
            params={
                "period": "",
                "month": month_str,
                "endMonth": month_str,
                "pageNum": 1,
                "pageSize": 31,
            },
            headers=HEADERS,
            timeout=10,
        )
        data = response.json().get("content", {})
        batch = parse_draws(data)
        all_draws.extend(sorted(batch))  # sort within month (API returns newest first)

        month += 1
        if month > 12:
            month = 1
            year += 1

    return all_draws
