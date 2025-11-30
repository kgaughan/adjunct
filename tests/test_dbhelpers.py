import sqlite3

import pytest

from adjunct import dbhelpers


@pytest.fixture
def tmp_db(tmp_path):
    conn = sqlite3.connect(tmp_path / "fixture.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE people (
            id   INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        """)
    cur.executemany(
        "INSERT INTO people (name) VALUES (?)",
        [("tom",), ("dick",), ("harry",)],
    )
    conn.commit()
    cur.close()
    yield conn
    conn.close()


def test_query(tmp_db):
    ids_names = list(dbhelpers.query(tmp_db, "SELECT id, name FROM people ORDER BY id"))
    assert ids_names == [(1, "tom"), (2, "dick"), (3, "harry")]


def test_query_row(tmp_db):
    assert dbhelpers.query_row(tmp_db, "SELECT id FROM people WHERE name = ?", ("harry",)) == (3,)


def test_query_row_no_match(tmp_db):
    assert dbhelpers.query_row(tmp_db, "SELECT id FROM people WHERE name = ?", ("alice",)) is None


def test_query_value(tmp_db):
    assert dbhelpers.query_value(tmp_db, "SELECT id FROM people WHERE name = ?", ("harry",)) == 3


def test_query_value_no_match(tmp_db):
    assert dbhelpers.query_value(tmp_db, "SELECT id FROM people WHERE name = ?", ("alice",)) is None


def test_execute(tmp_db):
    new_id = dbhelpers.execute(tmp_db, "INSERT INTO people (name) VALUES (?)", ("alice",))
    assert isinstance(new_id, int)
    assert dbhelpers.query_value(tmp_db, "SELECT id FROM people WHERE name = ?", ("alice",)) == new_id
