# tests/test_cli.py
import pytest
from unittest.mock import patch
from data.db import init_db, insert_draw, get_all_draws
from cli import cmd_update, cmd_stats, cmd_recommend

@pytest.fixture
def db(tmp_path):
    path = str(tmp_path / "test.db")
    init_db(path)
    return path

@pytest.fixture
def seeded_db(db):
    for i in range(10):
        insert_draw(db, f"2024-01-{i+1:02d}", [i+1, i+2, i+3, i+4, i+5])
    return db

def test_update_inserts_new_draws(db):
    mock_draws = [("2024-01-01", [1, 2, 3, 4, 5])]
    with patch("cli.fetch_draws", return_value=mock_draws), patch("cli.DB_PATH", db):
        cmd_update(start_month="2024-01")
    assert len(get_all_draws(db)) == 1

def test_update_skips_duplicates(db):
    mock_draws = [("2024-01-01", [1, 2, 3, 4, 5])]
    with patch("cli.fetch_draws", return_value=mock_draws), patch("cli.DB_PATH", db):
        cmd_update(start_month="2024-01")
        cmd_update(start_month="2024-01")
    assert len(get_all_draws(db)) == 1

def test_update_auto_detects_start_month(seeded_db):
    mock_draws = [("2024-01-11", [5, 6, 7, 8, 9])]
    with patch("cli.fetch_draws", return_value=mock_draws), patch("cli.DB_PATH", seeded_db):
        cmd_update()  # no start_month - should auto-detect from DB
    assert len(get_all_draws(seeded_db)) == 11

def test_stats_runs_without_error(seeded_db):
    with patch("cli.DB_PATH", seeded_db):
        cmd_stats()

def test_recommend_runs_without_error(seeded_db):
    with patch("cli.DB_PATH", seeded_db):
        cmd_recommend()


def test_update_accepts_lottery_type(db):
    mock_draws = [("2024-01-01", [1, 2, 3, 4, 5])]
    with patch("cli.fetch_draws", return_value=mock_draws), patch("cli.DB_PATH", db):
        cmd_update(start_month="2024-01", lottery_type="649")
    assert len(get_all_draws(db)) == 1


def test_stats_accepts_lottery_type(seeded_db):
    with patch("cli.DB_PATH", seeded_db):
        cmd_stats(lottery_type="649")


def test_recommend_accepts_lottery_type(seeded_db):
    with patch("cli.DB_PATH", seeded_db):
        cmd_recommend(lottery_type="649")
