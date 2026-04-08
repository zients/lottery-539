# tests/test_scraper.py
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from scraper.scraper import parse_draws, fetch_draws

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_response.json"


def load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_parse_draws_returns_list():
    draws = parse_draws(load_fixture(), "539")
    assert isinstance(draws, list)
    assert len(draws) == 3


def test_parse_draws_structure():
    draws = parse_draws(load_fixture(), "539")
    # API returns newest-first; fixture has 3 items
    date, numbers = draws[0]
    assert date == "2007-01-03"
    assert numbers == [22, 23, 27, 29, 30]


def test_parse_draws_all_numbers_in_range():
    draws = parse_draws(load_fixture(), "539")
    for _, numbers in draws:
        assert len(numbers) == 5
        assert all(1 <= n <= 39 for n in numbers)


def test_fetch_draws_calls_api():
    mock_response = MagicMock()
    mock_response.json.return_value = {"content": load_fixture()}
    with patch("scraper.scraper.requests.get", return_value=mock_response) as mock_get:
        result = fetch_draws(start_month="2007-01", lottery_type="539")
    mock_get.assert_called()
    assert len(result) >= 3


def test_fetch_draws_stops_on_empty():
    mock_response = MagicMock()
    mock_response.json.return_value = {"content": {"totalSize": 0, "daily539Res": []}}
    with patch("scraper.scraper.requests.get", return_value=mock_response):
        result = fetch_draws(start_month="2007-01", lottery_type="539")
    assert result == []


def test_fetch_draws_sorted_oldest_first():
    # fixture has items newest-first; fetch_draws should return oldest-first
    from datetime import date
    current = f"{date.today().year}-{date.today().month:02d}"
    mock_response = MagicMock()
    mock_response.json.return_value = {"content": load_fixture()}
    with patch("scraper.scraper.requests.get", return_value=mock_response):
        result = fetch_draws(start_month=current, lottery_type="539")
    dates = [r[0] for r in result]
    assert dates == sorted(dates)


def test_fetch_draws_uses_correct_endpoint_for_649():
    mock_response = MagicMock()
    mock_response.json.return_value = {"content": {"lotto649Res": []}}
    with patch("scraper.scraper.requests.get", return_value=mock_response) as mock_get:
        fetch_draws(start_month="2007-01", lottery_type="649")
    url = mock_get.call_args[0][0]
    assert "Lotto649Result" in url
