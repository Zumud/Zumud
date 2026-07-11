"""Unit tests for the username derivation used by lazy provisioning.

Usernames key filesystem paths (Applications/<username>/...), so they must be
filesystem-safe and unique. Full provisioning against a real database is
covered in the integration lane.
"""

from backend.api.auth import _generate_unique_username


class FakeDB:
    """Mimics db.query(User.id).filter(User.username == candidate).first()."""

    def __init__(self, taken=()):
        self.taken = set(taken)

    def query(self, *args):
        return self

    def filter(self, expression):
        # expression is `User.username == candidate`; the literal sits on the right.
        self.candidate = expression.right.value
        return self

    def first(self):
        return ("row",) if self.candidate in self.taken else None


def test_email_local_part_lowercased():
    assert _generate_unique_username(FakeDB(), "John.Doe@example.com") == "john.doe"


def test_unsafe_characters_stripped():
    assert _generate_unique_username(FakeDB(), "j+o!h#n.doe@example.com") == "john.doe"


def test_missing_email_falls_back_to_user():
    assert _generate_unique_username(FakeDB(), None) == "user"


def test_fully_unsafe_local_part_falls_back_to_user():
    assert _generate_unique_username(FakeDB(), "!!!@example.com") == "user"


def test_collision_appends_numeric_suffix():
    db = FakeDB(taken={"john", "john1"})
    assert _generate_unique_username(db, "john@example.com") == "john2"
