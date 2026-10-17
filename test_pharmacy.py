"""
================================================================================
Automated Test Suite for Pharmacy Inventory System (PS No. 72)
================================================================================
This test script verifies all required test cases and boundary conditions
using Python's built-in unittest framework.
Temporary files are used for all tests to protect the real medicines.csv.
================================================================================
"""

import csv
import os
import tempfile
import unittest

from pharmacy import (
    add_medicine_logic,
    sell_medicine_logic,
    delete_medicine_logic,
    get_low_stock_medicines,
    calculate_inventory_value,
    generate_id,
    find_medicine,
    load_medicines,
    save_medicines,
    FIELDNAMES,
    LOW_STOCK_LIMIT,
)


class TestPharmacyInventorySystem(unittest.TestCase):
    """
    Test suite verifying the 4 mandatory test cases and edge cases.
    """

    def setUp(self):
        """
        Create a temporary directory and temporary CSV file for each test.
        """
        self.test_dir = tempfile.TemporaryDirectory()
        self.temp_csv = os.path.join(self.test_dir.name, "test_medicines.csv")

    def tearDown(self):
        """
        Clean up the temporary directory after each test.
        """
        self.test_dir.cleanup()

    def _create_temp_csv(self, rows):
        """
        Helper method to populate the temporary CSV with given rows.
        """
        with open(self.temp_csv, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)

    # --------------------------------------------------------------------------
    # TEST CASE 1: Normal Input (Add Medicine)
    # --------------------------------------------------------------------------
    def test_case_1_normal_input(self):
        """
        Test Case 1 - Normal input:
        Start with empty medicines.csv.
        Add Name: Paracetamol, Quantity: 50, Price: 2.50
        Expected: Medicine added. ID: M1 | Paracetamol | Qty: 50 | Price: 2.50
        """
        # 1. Start with an empty CSV file (header only)
        self._create_temp_csv([])
        medicines = load_medicines(self.temp_csv)
        self.assertEqual(len(medicines), 0)

        # 2. Add Paracetamol, qty: 50, price: 2.50
        success, msg, record = add_medicine_logic(
            medicines=medicines,
            name="Paracetamol",
            quantity=50,
            price=2.50,
            filename=self.temp_csv
        )

        expected_msg = "Medicine added. ID: M1 | Paracetamol | Qty: 50 | Price: 2.50"
        self.assertTrue(success)
        self.assertEqual(msg, expected_msg)
        self.assertIsNotNone(record)
        self.assertEqual(record["ID"], "M1")
        self.assertEqual(record["Name"], "Paracetamol")
        self.assertEqual(record["Quantity"], 50)
        self.assertEqual(record["Price"], 2.50)

        # 3. Verify file persistence
        reloaded = load_medicines(self.temp_csv)
        self.assertEqual(len(reloaded), 1)
        self.assertEqual(reloaded[0]["ID"], "M1")
        self.assertEqual(reloaded[0]["Name"], "Paracetamol")
        self.assertEqual(reloaded[0]["Quantity"], 50)
        self.assertEqual(reloaded[0]["Price"], 2.50)

    # --------------------------------------------------------------------------
    # TEST CASE 2: Boundary / Minimum Input (Sell Entire Stock)
    # --------------------------------------------------------------------------
    def test_case_2_boundary_minimum_input(self):
        """
        Test Case 2 - Boundary / minimum input:
        Data: M1, Paracetamol, 50, 2.50.
        Sell ID: M1, Quantity: 50 (entire stock)
        Expected:
        Sold 50 units. Bill: 125.00
        Stock left: 0 | Out of stock!
        """
        initial_data = [
            {"ID": "M1", "Name": "Paracetamol", "Quantity": "50", "Price": "2.50"}
        ]
        self._create_temp_csv(initial_data)
        medicines = load_medicines(self.temp_csv)

        # Sell entire stock of 50 units
        success, msg, bill, remaining = sell_medicine_logic(
            medicines=medicines,
            med_id="M1",
            quantity=50,
            filename=self.temp_csv
        )

        expected_msg = "Sold 50 units. Bill: 125.00\nStock left: 0 | Out of stock!"
        self.assertTrue(success)
        self.assertEqual(msg, expected_msg)
        self.assertEqual(bill, 125.00)
        self.assertEqual(remaining, 0)

        # Verify medicine still exists in CSV with quantity 0
        reloaded = load_medicines(self.temp_csv)
        self.assertEqual(len(reloaded), 1)
        self.assertEqual(reloaded[0]["ID"], "M1")
        self.assertEqual(reloaded[0]["Quantity"], 0)

    # --------------------------------------------------------------------------
    # TEST CASE 3: Invalid Input (Insufficient Stock)
    # --------------------------------------------------------------------------
    def test_case_3_invalid_input(self):
        """
        Test Case 3 - Invalid input:
        Data: M1, Paracetamol, 5, 2.50.
        Sell ID: M1, Quantity: 8
        Expected: Insufficient stock. Available: 5
        """
        initial_data = [
            {"ID": "M1", "Name": "Paracetamol", "Quantity": "5", "Price": "2.50"}
        ]
        self._create_temp_csv(initial_data)
        medicines = load_medicines(self.temp_csv)

        # Attempt to sell 8 units when only 5 exist
        success, msg, bill, remaining = sell_medicine_logic(
            medicines=medicines,
            med_id="M1",
            quantity=8,
            filename=self.temp_csv
        )

        expected_msg = "Insufficient stock. Available: 5"
        self.assertFalse(success)
        self.assertEqual(msg, expected_msg)
        self.assertEqual(remaining, 5)

        # Verify stock was NOT altered in CSV
        reloaded = load_medicines(self.temp_csv)
        self.assertEqual(reloaded[0]["Quantity"], 5)

    # --------------------------------------------------------------------------
    # TEST CASE 4: Different Valid Scenario
    # --------------------------------------------------------------------------
    def test_case_4_scenario(self):
        """
        Test Case 4 - Different valid scenario:
        medicines.csv contains:
        M1,Paracetamol,50,2.50
        M2,Cetirizine,8,5.00
        M3,Amoxicillin,30,12.00
        (a) Menu 5 -> Expected: M2 | Cetirizine | Qty: 8 (Low stock)
        (b) Menu 4 -> ID: M3 -> Expected: Medicine M3 deleted.
        (c) Menu 6 -> Expected: Total inventory value: 165.00
        """
        sample_rows = [
            {"ID": "M1", "Name": "Paracetamol", "Quantity": "50", "Price": "2.50"},
            {"ID": "M2", "Name": "Cetirizine", "Quantity": "8", "Price": "5.00"},
            {"ID": "M3", "Name": "Amoxicillin", "Quantity": "30", "Price": "12.00"},
        ]
        self._create_temp_csv(sample_rows)
        medicines = load_medicines(self.temp_csv)

        # (a) Low stock report (Quantity strictly < 10)
        low_stock = get_low_stock_medicines(medicines, limit=LOW_STOCK_LIMIT)
        self.assertEqual(len(low_stock), 1)
        self.assertEqual(low_stock[0]["ID"], "M2")
        self.assertEqual(low_stock[0]["Name"], "Cetirizine")
        formatted_low_stock = f"{low_stock[0]['ID']} | {low_stock[0]['Name']} | Qty: {low_stock[0]['Quantity']} (Low stock)"
        self.assertEqual(formatted_low_stock, "M2 | Cetirizine | Qty: 8 (Low stock)")

        # (b) Delete Medicine M3
        del_success, del_msg = delete_medicine_logic(
            medicines=medicines,
            med_id="M3",
            filename=self.temp_csv
        )
        self.assertTrue(del_success)
        self.assertEqual(del_msg, "Medicine M3 deleted.")

        # Confirm M3 is removed from memory and CSV
        self.assertIsNone(find_medicine(medicines, "M3"))
        reloaded = load_medicines(self.temp_csv)
        self.assertEqual(len(reloaded), 2)
        self.assertIsNone(find_medicine(reloaded, "M3"))

        # (c) Inventory Value after deletion
        # Remaining: M1 (50 * 2.50 = 125.00) + M2 (8 * 5.00 = 40.00) = 165.00
        total_value = calculate_inventory_value(medicines)
        self.assertEqual(total_value, 165.00)
        formatted_value_msg = f"Total inventory value: {total_value:.2f}"
        self.assertEqual(formatted_value_msg, "Total inventory value: 165.00")

    # --------------------------------------------------------------------------
    # ADDITIONAL TESTS: ID Generation, Case Insensitivity, Input Rejections
    # --------------------------------------------------------------------------
    def test_id_generation_never_duplicates_after_deletion(self):
        """
        Verify new ID generation takes max existing numeric part + 1.
        If M1, M2, M3 exist and M2 or M3 is deleted, IDs do not collide.
        """
        meds = [
            {"ID": "M1", "Name": "MedA", "Quantity": 10, "Price": 5.0},
            {"ID": "M3", "Name": "MedC", "Quantity": 20, "Price": 10.0},
        ]
        # Max ID is 3, so next should be M4 even though list length is 2
        next_id = generate_id(meds)
        self.assertEqual(next_id, "M4")

    def test_case_insensitive_lookup(self):
        """
        Verify searching for medicine ID handles 'm1', 'M1', and leading/trailing spaces.
        """
        meds = [{"ID": "M1", "Name": "Paracetamol", "Quantity": 10, "Price": 2.5}]
        self.assertIsNotNone(find_medicine(meds, "m1"))
        self.assertIsNotNone(find_medicine(meds, "M1"))
        self.assertIsNotNone(find_medicine(meds, "  m1  "))
        self.assertIsNone(find_medicine(meds, "M99"))

    def test_validation_rejects_negative_and_empty(self):
        """
        Verify validation rules reject empty names, negative quantities, and negative prices.
        """
        meds = []
        # Empty name
        ok, msg, _ = add_medicine_logic(meds, "", 10, 5.0, self.temp_csv)
        self.assertFalse(ok)
        self.assertIn("cannot be empty", msg)

        # Negative quantity
        ok, msg, _ = add_medicine_logic(meds, "Aspirin", -5, 5.0, self.temp_csv)
        self.assertFalse(ok)
        self.assertIn("cannot be negative", msg)

        # Negative price
        ok, msg, _ = add_medicine_logic(meds, "Aspirin", 10, -2.5, self.temp_csv)
        self.assertFalse(ok)
        self.assertIn("cannot be negative", msg)


if __name__ == "__main__":
    unittest.main(verbosity=2)
