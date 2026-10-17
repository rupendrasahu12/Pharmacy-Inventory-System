# Pharmacy Inventory System (PS No. 72)

A clean, beginner-friendly, and robust console-based Python application to manage a pharmacy's medicine stock. Built using standard Python 3 with persistent CSV storage, clean modular functions, and comprehensive input validation.

---

## 1. Problem Statement
Pharmacies need a reliable, lightweight, and easy-to-use tool to track medicine stock levels, record sales transactions, generate customer bills, identify low-inventory items to prevent stockouts, and assess the total valuation of their current inventory. 

This project solves this need by providing an interactive command-line interface (CLI) that persists all data automatically to a CSV file (`medicines.csv`) after every change, ensuring zero data loss without requiring external databases or third-party dependencies.

---

## 2. Features
- **Auto-Generated Unique IDs**: Assigns identifiers sequentially (`M1`, `M2`, `M3`, ...) based on the highest existing numeric ID, ensuring no duplicate IDs are generated even after record deletion.
- **Add Medicine**: Easily register new medicines with name, quantity, and unit price.
- **View Stock**: Displays all stocked medicines in a clean, aligned tabular format with prices formatted to two decimal places.
- **Sell Medicine**: Validates stock availability, deducts sold units, calculates sales bills, updates CSV, and warns if stock is low (< 10) or exhausted (0).
- **Delete Medicine**: Safely remove discontinued medicines from the catalog with case-insensitive ID matching.
- **Low Stock Report**: Instantly filters and alerts which medicines have quantity strictly below 10 units.
- **Inventory Valuation**: Computes the exact monetary value of the entire medicine stock ($\sum \text{Quantity} \times \text{Price}$).
- **Automatic CSV Initialization**: Automatically creates `medicines.csv` with standard headers if it does not already exist.

---

## 3. Technologies & Concepts Used
- **Language**: Python 3 (Standard Library only — no third-party packages required).
- **Data Structures**:
  - `List`: For ordered sequences of inventory records.
  - `Dictionary`: In-memory representation of individual medicine records (`{"ID": "M1", "Name": "Paracetamol", "Quantity": 50, "Price": 2.50}`).
- **File I/O**:
  - `csv.DictReader`: Loads structured CSV rows into dictionary objects.
  - `csv.DictWriter`: Writes structured dictionary records back to disk after every modification.
- **Control Flow & Functions**: Modular functions separating business logic from interactive I/O.
- **Exception Handling**: `try/except ValueError` for robust input sanitization preventing application crashes on invalid input.

---

## 4. Project Structure
```text
pharmacy-inventory-system/
├── pharmacy.py          # Main application containing all business logic and CLI menu
├── test_pharmacy.py     # Automated unittest suite verifying all 4 test cases
├── medicines.csv        # CSV file acting as persistent data storage
├── README.md            # Comprehensive project documentation and usage guide
├── REPORT.md            # College project submission report with Mermaid flowchart
└── .gitignore           # Git ignore configuration for Python artifacts
```

---

## 5. How to Run

### Prerequisites
- Python 3.6 or higher installed on your computer.
- Terminal / PowerShell / Command Prompt.

### Step 1: Open Terminal in Project Folder
Navigate to the project directory:
```bash
cd pharmacy-inventory-system
```

### Step 2: Run the Application
Execute the following command:
```bash
python pharmacy.py
```

### Step 3: Run the Automated Unit Tests
To run all test cases using temporary in-memory files (without modifying `medicines.csv`):
```bash
python test_pharmacy.py
```

---

## 6. Menu Description

Upon launching the application, the user is presented with the numbered main menu:

```text
========================================
       PHARMACY INVENTORY SYSTEM
========================================
1. Add Medicine
2. View Stock
3. Sell Medicine
4. Delete Medicine
5. Low Stock Report
6. Inventory Value
7. Exit
========================================
```

| Option | Function | Description |
|---|---|---|
| **1** | `add_medicine` | Prompts for Name, Quantity, and Price. Validates input, generates the next `M<n>` ID, appends to CSV, and confirms addition. |
| **2** | `view_stock` | Displays a formatted table containing ID, Name, Quantity, and Price (formatted to 2 decimal places). Prints `"No medicines in stock."` if empty. |
| **3** | `sell_medicine` | Prompts for Medicine ID (case-insensitive) and Quantity. Checks stock availability, deducts sold quantity, calculates total bill, prints receipt status, and saves to CSV. |
| **4** | `delete_medicine` | Prompts for Medicine ID (case-insensitive) and removes it from inventory and CSV. |
| **5** | `low_stock_report` | Scans inventory and displays all items whose Quantity is strictly `< 10`. |
| **6** | `inventory_value` | Calculates and displays total inventory valuation: $\sum (\text{Quantity} \times \text{Price})$. |
| **7** | `Exit` | Displays a friendly exit message and terminates the program cleanly. |

---

## 7. Sample Input & Output (Test Cases)

### Test Case 1: Normal Input (Add Medicine)
- **Initial State**: Empty `medicines.csv` (header only).
- **Action**: Select Option `1`.
  - Enter medicine name: `Paracetamol`
  - Enter quantity: `50`
  - Enter price: `2.50`
- **Expected Console Output**:
  ```text
  Medicine added. ID: M1 | Paracetamol | Qty: 50 | Price: 2.50
  ```

---

### Test Case 2: Boundary / Minimum Input (Sell Entire Stock)
- **Initial State**: `M1,Paracetamol,50,2.50`
- **Action**: Select Option `3`.
  - Enter Medicine ID: `M1`
  - Enter Quantity to sell: `50`
- **Expected Console Output**:
  ```text
  Sold 50 units. Bill: 125.00
  Stock left: 0 | Out of stock!
  ```
*(Note: Medicine remains in `medicines.csv` with Quantity `0`)*

---

### Test Case 3: Invalid Input (Insufficient Stock)
- **Initial State**: `M1,Paracetamol,5,2.50`
- **Action**: Select Option `3`.
  - Enter Medicine ID: `M1`
  - Enter Quantity to sell: `8`
- **Expected Console Output**:
  ```text
  Insufficient stock. Available: 5
  ```
*(Stock remains unchanged at 5 units)*

---

### Test Case 4: Different Valid Scenario
- **Initial State** (`medicines.csv`):
  ```csv
  ID,Name,Quantity,Price
  M1,Paracetamol,50,2.50
  M2,Cetirizine,8,5.00
  M3,Amoxicillin,30,12.00
  ```

#### 4(a) Low Stock Report (Menu Option 5)
- **Expected Console Output**:
  ```text
  M2 | Cetirizine | Qty: 8 (Low stock)
  ```

#### 4(b) Delete Medicine (Menu Option 4)
- **Action**: Enter Medicine ID: `M3`
- **Expected Console Output**:
  ```text
  Medicine M3 deleted.
  ```

#### 4(c) Inventory Value (Menu Option 6)
- **Calculation**: 
  - M1: $50 \times 2.50 = 125.00$
  - M2: $8 \times 5.00 = 40.00$
  - Total: $125.00 + 40.00 = 165.00$
- **Expected Console Output**:
  ```text
  Total inventory value: 165.00
  ```

---

## 8. Validation Rules
1. **Empty Names**: Medicine names cannot be blank or whitespace-only.
2. **Numeric Types**: Quantities must be valid integers; prices must be valid numbers.
3. **Negative Values**: Negative quantity and negative price inputs are rejected with clear error messages.
4. **Sales Constraints**:
   - Quantity to sell must be strictly positive ($> 0$).
   - Cannot sell more than available quantity.
5. **Case-Insensitive ID Lookup**: Looking up `m1`, `M1`, or `  M1  ` resolves correctly.
6. **Graceful Exception Handling**: `ValueError` and `TypeError` are intercepted using `try/except` blocks so that invalid user entries never crash the program.

---

## 9. Future Improvements
- **Database Integration**: Migrate from flat CSV files to SQLite / PostgreSQL for concurrent multi-terminal access.
- **Role-Based Authentication**: Admin vs. Pharmacist/Cashier logins with distinct permission levels.
- **Expiry Date & Batch Tracking**: Track medicine batch numbers and alert on expired or near-expiry batches.
- **PDF Receipt Generation**: Export formatted PDF invoices for customer purchases with timestamps.
- **Graphical / Web User Interface**: Build an intuitive UI using Tkinter, PyQt, or a lightweight web framework like Flask / FastAPI.
