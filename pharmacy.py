"""
================================================================================
Pharmacy Inventory System (PS No. 72)
================================================================================
A console-based Python application to manage a pharmacy's medicine stock.
Uses standard library modules (csv, os) and stores inventory in medicines.csv.

Core Concepts Demonstrated:
- Dictionaries & Lists
- CSV File Handling (csv.DictReader, csv.DictWriter)
- CRUD Operations (Create, Read, Update, Delete)
- Functions with Clean Separation of Concerns
- Robust Input Validation & Error Handling
================================================================================
"""

import csv
import os

# ==============================================================================
# GLOBAL CONSTANTS
# ==============================================================================
FILE_NAME = "medicines.csv"
LOW_STOCK_LIMIT = 10
FIELDNAMES = ["ID", "Name", "Quantity", "Price"]


# ==============================================================================
# DATA PERSISTENCE FUNCTIONS
# ==============================================================================
def load_medicines(filename=FILE_NAME):
    """
    Load medicines from the CSV file into a list of dictionaries.

    If the file does not exist, it is created automatically with the header:
    ID,Name,Quantity,Price
    
    Data conversions performed:
    - Quantity is converted to integer (int)
    - Price is converted to float (float)
    """
    medicines = []

    # If file doesn't exist, create it with header only
    if not os.path.exists(filename):
        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()
        except OSError as e:
            print(f"Error creating file {filename}: {e}")
        return medicines

    # Read records from CSV file
    try:
        with open(filename, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip empty or malformed rows
                if not row or not row.get("ID"):
                    continue
                try:
                    qty = int(row.get("Quantity", 0))
                    price = float(row.get("Price", 0.0))
                    medicines.append({
                        "ID": row["ID"].strip(),
                        "Name": row["Name"].strip(),
                        "Quantity": qty,
                        "Price": price
                    })
                except (ValueError, TypeError):
                    # Skip corrupted rows without crashing
                    continue
    except OSError as e:
        print(f"Error reading file {filename}: {e}")

    return medicines


def save_medicines(medicines, filename=FILE_NAME):
    """
    Save the complete list of medicine dictionaries back to medicines.csv
    using csv.DictWriter. Price is saved formatted to 2 decimal places.
    """
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for med in medicines:
                writer.writerow({
                    "ID": str(med["ID"]).strip(),
                    "Name": str(med["Name"]).strip(),
                    "Quantity": int(med["Quantity"]),
                    "Price": f"{float(med['Price']):.2f}"
                })
        return True
    except OSError as e:
        print(f"Error saving file {filename}: {e}")
        return False


# ==============================================================================
# HELPER & VALIDATION FUNCTIONS
# ==============================================================================
def generate_id(medicines):
    """
    Generate a new unique medicine ID.
    Finds the highest existing numeric ID part and adds 1 (e.g. M1, M2 -> M3).
    This ensures IDs never duplicate even after records are deleted.
    If the list is empty, starts from M1.
    """
    if not medicines:
        return "M1"

    max_num = 0
    for med in medicines:
        raw_id = str(med.get("ID", "")).strip().upper()
        if raw_id.startswith("M"):
            num_part = raw_id[1:]
            if num_part.isdigit():
                num = int(num_part)
                if num > max_num:
                    max_num = num
        elif raw_id.isdigit():
            num = int(raw_id)
            if num > max_num:
                max_num = num

    return f"M{max_num + 1}"


def find_medicine(medicines, med_id):
    """
    Find and return a medicine dictionary from the list by ID (case-insensitive).
    Returns None if the medicine is not found.
    """
    if not med_id:
        return None
    target_id = str(med_id).strip().upper()
    for med in medicines:
        if str(med.get("ID", "")).strip().upper() == target_id:
            return med
    return None


def get_positive_int(prompt="Enter quantity: "):
    """
    Prompt the user for a strictly positive integer (> 0).
    Rejects non-numeric, negative, and zero values with a clear error.
    Returns the integer if valid, or None if invalid.
    """
    user_input = input(prompt).strip()
    try:
        val = int(user_input)
        if val <= 0:
            print("Error: Quantity must be greater than zero.")
            return None
        return val
    except ValueError:
        print("Error: Invalid input. Quantity must be a valid whole number.")
        return None


def get_non_negative_int(prompt="Enter quantity: "):
    """
    Prompt the user for a non-negative integer (>= 0).
    Rejects non-numeric or negative values with a clear error.
    Returns the integer if valid, or None if invalid.
    """
    user_input = input(prompt).strip()
    try:
        val = int(user_input)
        if val < 0:
            print("Error: Quantity cannot be negative.")
            return None
        return val
    except ValueError:
        print("Error: Invalid input. Quantity must be a valid whole number.")
        return None


def get_non_negative_float(prompt="Enter price: "):
    """
    Prompt the user for a non-negative float (>= 0.0).
    Rejects non-numeric or negative values with a clear error.
    Returns the float if valid, or None if invalid.
    """
    user_input = input(prompt).strip()
    try:
        val = float(user_input)
        if val < 0.0:
            print("Error: Price cannot be negative.")
            return None
        return val
    except ValueError:
        print("Error: Invalid input. Price must be a valid numeric value.")
        return None


# ==============================================================================
# PURE LOGIC FUNCTIONS (TESTABLE WITHOUT CONSOLE INPUT)
# ==============================================================================
def add_medicine_logic(medicines, name, quantity, price, filename=FILE_NAME):
    """
    Pure logic function to validate, add a new medicine, and persist to CSV.
    Returns (success: bool, message: str, new_record: dict or None).
    """
    # Validate name
    if name is None or not str(name).strip():
        return False, "Error: Medicine name cannot be empty.", None

    clean_name = str(name).strip()

    # Validate quantity
    try:
        clean_qty = int(quantity)
    except (ValueError, TypeError):
        return False, "Error: Quantity must be a valid whole number.", None

    if clean_qty < 0:
        return False, "Error: Quantity cannot be negative.", None

    # Validate price
    try:
        clean_price = float(price)
    except (ValueError, TypeError):
        return False, "Error: Price must be a valid numeric value.", None

    if clean_price < 0.0:
        return False, "Error: Price cannot be negative.", None

    # Generate new ID and append record
    new_id = generate_id(medicines)
    new_record = {
        "ID": new_id,
        "Name": clean_name,
        "Quantity": clean_qty,
        "Price": clean_price
    }
    medicines.append(new_record)
    save_medicines(medicines, filename)

    msg = f"Medicine added. ID: {new_id} | {clean_name} | Qty: {clean_qty} | Price: {clean_price:.2f}"
    return True, msg, new_record


def sell_medicine_logic(medicines, med_id, quantity, filename=FILE_NAME):
    """
    Pure logic function to validate and execute medicine sale.
    Returns (success: bool, message: str, bill: float, remaining_stock: int).
    """
    med = find_medicine(medicines, med_id)
    if med is None:
        return False, "Medicine not found.", 0.0, -1

    # Validate sale quantity
    try:
        qty = int(quantity)
    except (ValueError, TypeError):
        return False, "Error: Quantity must be a valid whole number.", 0.0, med["Quantity"]

    if qty <= 0:
        return False, "Error: Quantity must be greater than zero.", 0.0, med["Quantity"]

    if qty > med["Quantity"]:
        msg = f"Insufficient stock. Available: {med['Quantity']}"
        return False, msg, 0.0, med["Quantity"]

    # Deduct stock and compute bill
    med["Quantity"] -= qty
    bill = qty * med["Price"]
    save_medicines(medicines, filename)

    remaining = med["Quantity"]
    if remaining == 0:
        stock_msg = "Stock left: 0 | Out of stock!"
    elif remaining < LOW_STOCK_LIMIT:
        stock_msg = f"Stock left: {remaining} | Low stock!"
    else:
        stock_msg = f"Stock left: {remaining}"

    msg = f"Sold {qty} units. Bill: {bill:.2f}\n{stock_msg}"
    return True, msg, bill, remaining


def delete_medicine_logic(medicines, med_id, filename=FILE_NAME):
    """
    Pure logic function to delete a medicine by ID and update the CSV.
    Returns (success: bool, message: str).
    """
    med = find_medicine(medicines, med_id)
    if med is None:
        return False, "Medicine not found."

    actual_id = med["ID"]
    medicines.remove(med)
    save_medicines(medicines, filename)
    return True, f"Medicine {actual_id} deleted."


def get_low_stock_medicines(medicines, limit=LOW_STOCK_LIMIT):
    """
    Return a list of medicine dictionaries whose quantity is strictly below limit.
    """
    return [med for med in medicines if med["Quantity"] < limit]


def calculate_inventory_value(medicines):
    """
    Calculate and return the total monetary inventory value:
    sum of (Quantity * Price) for all medicines.
    """
    return sum(med["Quantity"] * med["Price"] for med in medicines)


# ==============================================================================
# MENU FEATURE FUNCTIONS (INTERACTIVE CLI WRAPPERS)
# ==============================================================================
def add_medicine(medicines, filename=FILE_NAME, name=None, quantity=None, price=None):
    """
    Feature 1: Add a new medicine.
    Prompts for Name, Quantity, and Price.
    Validates inputs and saves to CSV.
    """
    print("\n--- Add Medicine ---")
    if name is None:
        name_input = input("Enter medicine name: ").strip()
        if not name_input:
            print("Error: Medicine name cannot be empty.")
            return None
    else:
        name_input = name

    if quantity is None:
        qty_input = get_non_negative_int("Enter quantity: ")
        if qty_input is None:
            return None
    else:
        qty_input = quantity

    if price is None:
        price_input = get_non_negative_float("Enter price: ")
        if price_input is None:
            return None
    else:
        price_input = price

    success, msg, record = add_medicine_logic(medicines, name_input, qty_input, price_input, filename)
    print(msg)
    return record if success else None


def view_stock(medicines):
    """
    Feature 2: View current medicine stock in a clean aligned table.
    If no medicines are present, prints 'No medicines in stock.'
    """
    print("\n--- Current Medicine Stock ---")
    if not medicines:
        print("No medicines in stock.")
        return

    # Table Header
    print("-" * 55)
    print(f"{'ID':<6}{'Name':<25}{'Quantity':<12}{'Price':<12}")
    print("-" * 55)

    # Table Rows
    for med in medicines:
        print(f"{med['ID']:<6}{med['Name']:<25}{med['Quantity']:<12}{med['Price']:.2f}")

    print("-" * 55)


def sell_medicine(medicines, filename=FILE_NAME, med_id=None, quantity=None):
    """
    Feature 3: Sell medicine.
    Prompts for ID (case-insensitive) and Quantity.
    Verifies availability, deducts stock, calculates bill, and saves changes.
    """
    print("\n--- Sell Medicine ---")
    if med_id is None:
        med_id_input = input("Enter Medicine ID: ").strip()
        if not med_id_input:
            print("Medicine not found.")
            return None
    else:
        med_id_input = med_id

    med = find_medicine(medicines, med_id_input)
    if med is None:
        print("Medicine not found.")
        return None

    if quantity is None:
        qty_input = get_positive_int("Enter Quantity to sell: ")
        if qty_input is None:
            return None
    else:
        qty_input = quantity

    success, msg, bill, remaining = sell_medicine_logic(medicines, med_id_input, qty_input, filename)
    print(msg)
    return success


def delete_medicine(medicines, filename=FILE_NAME, med_id=None):
    """
    Feature 4: Delete a medicine record.
    Prompts for ID (case-insensitive). Removes record and saves changes.
    """
    print("\n--- Delete Medicine ---")
    if med_id is None:
        med_id_input = input("Enter Medicine ID to delete: ").strip()
    else:
        med_id_input = med_id

    success, msg = delete_medicine_logic(medicines, med_id_input, filename)
    print(msg)
    return success


def low_stock_report(medicines):
    """
    Feature 5: Report all medicines with quantity strictly below LOW_STOCK_LIMIT (10).
    """
    print("\n--- Low Stock Report ---")
    low_stock_list = get_low_stock_medicines(medicines, LOW_STOCK_LIMIT)
    if not low_stock_list:
        print("No low stock medicines.")
        return []

    lines = []
    for med in low_stock_list:
        line = f"{med['ID']} | {med['Name']} | Qty: {med['Quantity']} (Low stock)"
        print(line)
        lines.append(line)
    return lines


def inventory_value(medicines):
    """
    Feature 6: Calculate and display total monetary value of current inventory.
    """
    print("\n--- Inventory Value ---")
    total = calculate_inventory_value(medicines)
    print(f"Total inventory value: {total:.2f}")
    return total


# ==============================================================================
# MENU & MAIN APPLICATION LOOP
# ==============================================================================
def show_menu():
    """Display the main console menu options."""
    print("\n" + "=" * 40)
    print("       PHARMACY INVENTORY SYSTEM")
    print("=" * 40)
    print("1. Add Medicine")
    print("2. View Stock")
    print("3. Sell Medicine")
    print("4. Delete Medicine")
    print("5. Low Stock Report")
    print("6. Inventory Value")
    print("7. Exit")
    print("=" * 40)


def main():
    """
    Main driver function for Pharmacy Inventory System.
    Loads data on start, shows interactive menu, and runs until user selects 7.
    """
    print("Initializing Pharmacy Inventory System (PS No. 72)...")
    medicines = load_medicines(FILE_NAME)

    while True:
        show_menu()
        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            add_medicine(medicines, filename=FILE_NAME)
        elif choice == "2":
            view_stock(medicines)
        elif choice == "3":
            sell_medicine(medicines, filename=FILE_NAME)
        elif choice == "4":
            delete_medicine(medicines, filename=FILE_NAME)
        elif choice == "5":
            low_stock_report(medicines)
        elif choice == "6":
            inventory_value(medicines)
        elif choice == "7":
            print("\nThank you for using Pharmacy Inventory System. Goodbye!")
            break
        else:
            print("Invalid choice! Please select an option from 1 to 7.")


if __name__ == "__main__":
    main()
