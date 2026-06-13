import unittest
from src.db.backend.indexed_memory import IndexedMemoryDatabase

class TestIndexedMemoryDatabase(unittest.TestCase):
    def setUp(self):
        self.db = IndexedMemoryDatabase()
        self.db.create_table("cars")
        self.db.create_record("cars", {"brand": "Toyota", "price": 20000, "color": "red"})
        self.db.create_record("cars", {"brand": "BMW", "price": 35000, "color": "black"})
        self.db.create_record("cars", {"brand": "Toyota", "price": 22000, "color": "blue"})

    def test_create_index(self):
        self.db.create_index("cars", "brand")
        self.assertIn("brand", self.db._indices["cars"])

    def test_select_uses_index(self):
        self.db.create_index("cars", "brand")
        results = self.db.read_records("cars", {"brand": "Toyota"})
        self.assertEqual(len(results), 2)

    def test_select_without_index_fallback(self):
        results = self.db.read_records("cars", {"price": 20000})
        self.assertEqual(len(results), 1)

    def test_index_updates_on_insert(self):
        self.db.create_index("cars", "brand")
        self.db.create_record("cars", {"brand": "Toyota", "price": 25000, "color": "green"})
        idx = self.db._indices["cars"]["brand"]
        self.assertEqual(len(idx.get("Toyota", [])), 3)

    def test_index_updates_on_update(self):
        self.db.create_index("cars", "brand")
        self.db.update_records("cars", {"brand": "Toyota"}, {"brand": "Lexus"})
        idx = self.db._indices["cars"]["brand"]
        self.assertEqual(len(idx.get("Toyota", [])), 0)
        self.assertEqual(len(idx.get("Lexus", [])), 2)

    def test_index_updates_on_delete(self):
        self.db.create_index("cars", "brand")
        self.db.delete_records("cars", {"brand": "BMW"})
        idx = self.db._indices["cars"]["brand"]
        self.assertNotIn("BMW", idx)

    def test_drop_index(self):
        self.db.create_index("cars", "brand")
        self.db.drop_index("cars", "brand")
        self.assertNotIn("brand", self.db._indices.get("cars", {}))

if __name__ == "__main__":
    unittest.main()