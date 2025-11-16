import os

from adjunct import passkit


def test_jsonpasswdfile(tmp_path):
    ht = passkit.JSONPasswdFile(tmp_path / "passwd.json")

    assert list(ht.users.keys()) == []

    ht.set_password("fred", "wilma")
    assert set(ht.users.keys()) == {"fred"}
    assert ht.check_password("fred", "wilma")

    ht.set_password("barney", "betty")
    assert set(ht.users.keys()) == {"fred", "barney"}
    assert ht.check_password("barney", "betty")

    assert not ht.check_password("fred", "betty")
    assert not ht.check_password("barney", "wilma")

    ht.delete("fred")
    assert set(ht.users.keys()) == {"barney"}
    assert not ht.check_password("fred", "wilma")
    assert ht.check_password("barney", "betty")

    ht.delete("fred")
    assert set(ht.users.keys()) == {"barney"}


def test_jsonpasswdfile_existing():
    path = os.path.join(os.path.dirname(__file__), "passwd.json")
    ht = passkit.JSONPasswdFile(path)
    assert ht.check_password("fred", "wilma")
    assert ht.check_password("barney", "betty")
    assert set(ht.users.keys()) == {"fred", "barney"}
