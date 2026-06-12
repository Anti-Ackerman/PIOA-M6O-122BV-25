# tests/test_tui.py

import unittest
from unittest.mock import patch
from io import StringIO
from src.db.tui import CarDatabaseUI
from src.db.backend.memory import Database


class TestCarDatabaseUI(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.ui = CarDatabaseUI()
        self.ui.db = self.db
        self.db.create_table("cars")
        self.db.create_record("cars", {"brand": "Toyota", "price": 20000, "color": "red"})

    # ----- Вспомогательные методы -----
    def test_get_non_empty(self):
        with patch('builtins.input', return_value="  BMW  "):
            self.assertEqual(self.ui._get_non_empty("x"), "BMW")

    def test_get_int(self):
        with patch('builtins.input', return_value="15000"):
            self.assertEqual(self.ui._get_int("x"), 15000)

    def test_get_filters(self):
        cases = [
            (["", "", ""], {}),
            (["Toyota", "", ""], {"brand": "Toyota"}),
            (["", "20000", ""], {"price": 20000}),
        ]
        for inp, exp in cases:
            with patch('builtins.input', side_effect=inp):
                self.assertEqual(self.ui._get_filters(), exp)

    def test_get_data(self):
        with patch('builtins.input', side_effect=["Honda", "18000", "blue"]):
            self.assertEqual(self.ui._get_data(), {"brand": "Honda", "price": 18000, "color": "blue"})

    def test_print_records(self):
        self.ui._print_records([])
        self.ui._print_records([{"id": 1, "brand": "A", "price": 100, "color": "r"}])

    # ----- Управление таблицами -----
    def test_table_management_create(self):
        with patch('builtins.input', side_effect=["1", "new_table", "0"]):
            self.ui._table_management()
        self.assertIn("new_table", self.db.get_table_names())

    def test_table_management_delete(self):
        self.db.create_table("temp")
        with patch('builtins.input', side_effect=["2", "temp", "0"]):
            self.ui._table_management()
        self.assertNotIn("temp", self.db.get_table_names())

    def test_choose_existing_table(self):
        with patch('builtins.input', return_value="cars"):
            with patch.object(self.ui, '_work_with_table') as mock:
                self.ui._choose_and_work_with_table()
                mock.assert_called_once_with("cars")

    def test_choose_nonexistent_table(self):
        with patch('builtins.input', return_value="wrong"):
            with patch('sys.stdout', new_callable=StringIO) as out:
                self.ui._choose_and_work_with_table()
                self.assertIn("не найдена", out.getvalue().lower())

    # ----- Сортировка -----
    def test_sort_table_empty(self):
        self.db.create_table("empty")
        with patch('builtins.input', side_effect=["empty", "price", "n"]):
            with patch('sys.stdout', new_callable=StringIO) as out:
                self.ui._sort_table()
                self.assertIn("пуста", out.getvalue().lower())

    def test_sort_table_valid(self):
        self.db.create_record("cars", {"brand": "Audi", "price": 30000, "color": "white"})
        self.db.create_record("cars", {"brand": "BMW", "price": 35000, "color": "black"})
        with patch('builtins.input', side_effect=["cars", "price", "n"]):
            with patch('sys.stdout', new_callable=StringIO) as out:
                self.ui._sort_table()
                output = out.getvalue()
                self.assertIn("20000", output)
                self.assertIn("30000", output)
                self.assertIn("35000", output)

    def test_sort_table_invalid_field(self):
        with patch('builtins.input', side_effect=["cars", "invalid", "n"]):
            with patch('sys.stdout', new_callable=StringIO) as out:
                self.ui._sort_table()
                self.assertIn("Недопустимое поле", out.getvalue())

    # ----- CRUD операции -----
    def test_work_with_table_add(self):
        with patch('builtins.input', side_effect=["1", "Honda", "18000", "blue", "0"]):
            self.ui._work_with_table("cars")
        self.assertTrue(self.db.read_records("cars", {"brand": "Honda"}))

    def test_work_with_table_find(self):
        with patch('builtins.input', side_effect=["2", "Toyota", "", "", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as out:
                self.ui._work_with_table("cars")
                self.assertIn("Toyota", out.getvalue())

    def test_work_with_table_update(self):
        # Основная последовательность + запасные нули на случай дополнительных запросов
        with patch('builtins.input', side_effect=[
            "3", "Toyota", "", "", "Lexus", "", "", "0", "0", "0", "0"
        ]):
            self.ui._work_with_table("cars")
        self.assertEqual(len(self.db.read_records("cars", {"brand": "Toyota"})), 0)
        self.assertEqual(len(self.db.read_records("cars", {"brand": "Lexus"})), 1)

    def test_work_with_table_delete(self):
        self.db.create_record("cars", {"brand": "ToDel", "price": 100, "color": "w"})
        with patch('builtins.input', side_effect=["4", "ToDel", "", "", "y", "0"]):
            self.ui._work_with_table("cars")
        self.assertEqual(len(self.db.read_records("cars", {"brand": "ToDel"})), 0)

    def test_work_with_table_show_all(self):
        with patch('builtins.input', side_effect=["5", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as out:
                self.ui._work_with_table("cars")
                self.assertIn("Toyota", out.getvalue())

    def test_update_no_match(self):
        with patch('builtins.input', side_effect=["3", "NoSuch", "", "", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as out:
                self.ui._work_with_table("cars")
                self.assertIn("Нет записей", out.getvalue())

    # ----- Главное меню (run) -----
    def test_run_management_choice(self):
        with patch('builtins.input', side_effect=["1", "0", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as out:
                self.ui.run()
                self.assertIn("Управление таблицами", out.getvalue())

    def test_run_work_choice(self):
        with patch('builtins.input', side_effect=["2", "cars", "0", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as out:
                self.ui.run()
                self.assertIn("Работа с таблицей", out.getvalue())

    def test_run_sort_choice(self):
        self.db.create_record("cars", {"brand": "Audi", "price": 30000, "color": "white"})
        self.db.create_record("cars", {"brand": "BMW", "price": 35000, "color": "black"})
        with patch('builtins.input', side_effect=["3", "cars", "price", "n", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as out:
                self.ui.run()
                output = out.getvalue()
                self.assertIn("20000", output)
                self.assertIn("30000", output)
                self.assertIn("35000", output)


if __name__ == "__main__":
    unittest.main()