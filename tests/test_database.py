import sqlite3
import unittest

from src.database import DatabaseRepository


class DatabaseRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseRepository(":memory:")

    def tearDown(self):
        self.db.close()

    def test_add_and_read_inserted_record(self):
        self.assertTrue(self.db.add(1, "alice", "<p>Hello</p>"))
        self.assertEqual(self.db.get_by_id(1), {"id": 1, "name": "alice", "message": "<p>Hello</p>"})

    def test_add_duplicate_id_raises_integrity_error(self):
        self.db.add(1, "alice", "first")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.add(1, "bob", "second")

    def test_add_rejects_invalid_length_and_types(self):
        with self.assertRaises(ValueError):
            self.db.add(1, "a" * 257, "message")
        with self.assertRaises(TypeError):
            self.db.add("1", "alice", "message")

    def test_get_by_id_returns_none_when_missing(self):
        self.assertIsNone(self.db.get_by_id(44))

    def test_get_by_id_rejects_non_integer(self):
        with self.assertRaises(TypeError):
            self.db.get_by_id(True)

    def test_get_by_name_returns_all_matching_rows(self):
        self.db.add(2, "alice", "second")
        self.db.add(1, "alice", "first")
        self.db.add(3, "bob", "other")
        self.assertEqual([row["id"] for row in self.db.get_by_name("alice")], [1, 2])

    def test_get_by_name_returns_empty_list_when_missing(self):
        self.assertEqual(self.db.get_by_name("nobody"), [])

    def test_update_changes_existing_message(self):
        self.db.add(1, "alice", "old")
        self.assertTrue(self.db.update(1, "new"))
        self.assertEqual(self.db.get_by_id(1)["message"], "new")

    def test_update_missing_id_returns_false(self):
        self.assertFalse(self.db.update(9, "message"))

    def test_update_validates_message_length(self):
        with self.assertRaises(ValueError):
            self.db.update(1, "x" * 8097)

    def test_delete_removes_existing_record(self):
        self.db.add(1, "alice", "message")
        self.assertTrue(self.db.delete(1))
        self.assertIsNone(self.db.get_by_id(1))

    def test_delete_missing_id_returns_false(self):
        self.assertFalse(self.db.delete(2))


if __name__ == "__main__":
    unittest.main()
