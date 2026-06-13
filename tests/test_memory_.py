import unittest
from src.db.backend.memory import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.db.create_table("cars")
        self.db.create_record("cars", {"brand": "Toyota", "price": 20000, "color": "red"})
        self.db.create_record("cars", {"brand": "BMW", "price": 35000, "color": "black"})
        self.db.create_record("cars", {"brand": "Audi", "price": 30000, "color": "white"})

    def test_create_table_success(self):
        self.db.create_table("new")
        self.assertIn("new", self.db.get_table_names())

    def test_create_table_duplicate(self):
        with self.assertRaises(ValueError):
            self.db.create_table("cars")

    def test_drop_table_success(self):
        self.db.drop_table("cars")
        self.assertNotIn("cars", self.db.get_table_names())

    def test_drop_table_nonexistent(self):
        with self.assertRaises(ValueError):
            self.db.drop_table("nonexistent")

    def test_create_record(self):
        rec = self.db.create_record("cars", {"brand": "Honda", "price": 18000, "color": "blue"})
        self.assertIn("id", rec)
        self.assertEqual(rec["brand"], "Honda")

    def test_create_record_missing_field(self):
        with self.assertRaises(ValueError):
            self.db.create_record("cars", {"brand": "Honda"}) 

    def test_create_record_invalid_price(self):
        with self.assertRaises(ValueError):
            self.db.create_record("cars", {"brand": "Honda", "price": "not_int", "color": "blue"})

    def test_read_records_no_filters(self):
        cars = self.db.read_records("cars")
        self.assertEqual(len(cars), 3)

    def test_read_records_with_filters(self):
        toyota = self.db.read_records("cars", {"brand": "Toyota"})
        self.assertEqual(len(toyota), 1)
        self.assertEqual(toyota[0]["price"], 20000)

    def test_read_records_filters_case_insensitive(self):
        toyota = self.db.read_records("cars", {"brand": "toyota"})
        self.assertEqual(len(toyota), 1)

    def test_update_records(self):
        updated = self.db.update_records("cars", {"brand": "Toyota"}, {"price": 22000})
        self.assertEqual(updated, 1)
        toyota = self.db.read_records("cars", {"brand": "Toyota"})[0]
        self.assertEqual(toyota["price"], 22000)

    def test_update_records_all(self):
        updated = self.db.update_records("cars", None, {"color": "green"})
        self.assertEqual(updated, 3)
        for car in self.db.read_records("cars"):
            self.assertEqual(car["color"], "green")

    def test_update_records_no_match(self):
        updated = self.db.update_records("cars", {"brand": "Lada"}, {"price": 100})
        self.assertEqual(updated, 0)

    def test_delete_records(self):
        deleted = self.db.delete_records("cars", {"brand": "BMW"})
        self.assertEqual(deleted, 1)
        self.assertEqual(len(self.db.read_records("cars")), 2)

    def test_delete_records_all(self):
        deleted = self.db.delete_records("cars", None)
        self.assertEqual(deleted, 3)
        self.assertEqual(len(self.db.read_records("cars")), 0)

    def test_delete_records_no_match(self):
        deleted = self.db.delete_records("cars", {"brand": "Lada"})
        self.assertEqual(deleted, 0)

    def test_sort_records_price_asc(self):
        sorted_cars = self.db.sort_records("cars", "price")
        prices = [c["price"] for c in sorted_cars]
        self.assertEqual(prices, [20000, 30000, 35000])

    def test_sort_records_price_desc(self):
        sorted_cars = self.db.sort_records("cars", "price", reverse=True)
        prices = [c["price"] for c in sorted_cars]
        self.assertEqual(prices, [35000, 30000, 20000])

    def test_sort_records_empty_table(self):
        self.db.create_table("empty")
        result = self.db.sort_records("empty", "price")
        self.assertEqual(result, [])

    def test_sort_records_missing_key(self):
        self.db.create_table("noyear")
        self.db.create_record("noyear", {"brand": "A", "price": 100})
        self.db.create_record("noyear", {"brand": "B", "price": 200})
        sorted_cars = self.db.sort_records("noyear", "year") 
        self.assertEqual(len(sorted_cars), 2)  

    def test_get_table_names(self):
        names = self.db.get_table_names()
        self.assertIn("cars", names)
        self.db.create_table("another")
        self.assertEqual(len(self.db.get_table_names()), 2)

if __name__ == "__main__":
    unittest.main()