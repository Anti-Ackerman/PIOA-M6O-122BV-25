import unittest
import tempfile
from src.db.backend.file import FileDatabase
from src.db.backend.errors import TableNotFoundError, TableAlreadyExistsError

class TestFileDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = FileDatabase(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_table(self):
        self.db.create_table("test")
        self.assertIn("test", self.db.get_table_names())

    def test_create_table_already_exists(self):
        self.db.create_table("test")
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("test")

    def test_drop_table(self):
        self.db.create_table("test")
        self.db.drop_table("test")
        self.assertNotIn("test", self.db.get_table_names())

    def test_drop_nonexistent(self):
        with self.assertRaises(TableNotFoundError):
            self.db.drop_table("nonexistent")

    def test_read_nonexistent(self):
        with self.assertRaises(TableNotFoundError):
            self.db.read_records("nonexistent")

    def test_create_record(self):
        self.db.create_table("test")
        rec = self.db.create_record("test", {"name": "Alice"})
        self.assertEqual(rec["id"], 1)
        self.assertEqual(rec["name"], "Alice")

    def test_read_records_no_filters(self):
        self.db.create_table("test")
        self.db.create_record("test", {"name": "A"})
        self.db.create_record("test", {"name": "B"})
        self.assertEqual(len(self.db.read_records("test")), 2)

    def test_read_records_with_filters(self):
        self.db.create_table("test")
        self.db.create_record("test", {"name": "Alice"})
        self.db.create_record("test", {"name": "Bob"})
        result = self.db.read_records("test", {"name": "Alice"})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Alice")

    def test_update_records(self):
        self.db.create_table("test")
        self.db.create_record("test", {"name": "Old"})
        updated = self.db.update_records("test", {"name": "Old"}, {"name": "New"})
        self.assertEqual(updated, 1)
        self.assertEqual(self.db.read_records("test")[0]["name"], "New")

    def test_update_with_empty_filters(self):
        self.db.create_table("test")
        self.db.create_record("test", {"name": "A"})
        self.db.create_record("test", {"name": "B"})
        updated = self.db.update_records("test", None, {"status": "updated"})
        self.assertEqual(updated, 2)
        for rec in self.db.read_records("test"):
            self.assertEqual(rec["status"], "updated")

    def test_delete_records(self):
        self.db.create_table("test")
        self.db.create_record("test", {"name": "ToDelete"})
        deleted = self.db.delete_records("test", {"name": "ToDelete"})
        self.assertEqual(deleted, 1)
        self.assertEqual(len(self.db.read_records("test")), 0)

    def test_delete_all(self):
        self.db.create_table("test")
        self.db.create_record("test", {"name": "A"})
        self.db.create_record("test", {"name": "B"})
        deleted = self.db.delete_records("test", None)
        self.assertEqual(deleted, 2)
        self.assertEqual(len(self.db.read_records("test")), 0)

    def test_sort_records(self):
        self.db.create_table("test")
        self.db.create_record("test", {"price": 300})
        self.db.create_record("test", {"price": 100})
        sorted_rec = self.db.sort_records("test", "price")
        self.assertEqual([r["price"] for r in sorted_rec], [100, 300])

    def test_get_table_names(self):
        self.db.create_table("table1")
        self.db.create_table("table2")
        names = self.db.get_table_names()
        self.assertIn("table1", names)
        self.assertIn("table2", names)

if __name__ == "__main__":
    unittest.main()