## 🧲 **Billing Management System**  
A simple yet powerful billing management desktop application built with **PySide6** and **SQLite**. This project allows you to create, store, and manage customer bills efficiently.  

---

## 🚀 **Features**
###
✅ **Item Price Management**  
- Add and store item names and rates in the database.  
- When creating a bill, the item rate is automatically fetched from the database, so you don’t have to remember the prices manually.  

✅ **Customer Auto-Fetch**  
- If the customer is already registered, the name and email are automatically fetched when you enter the phone number.  
- This saves time and avoids duplication of customer records.  

✅ **Dynamic Table for Billing**  
- The table for adding items to the bill automatically adds a new row when data is entered in the last row.  
- The serial number column updates dynamically based on the number of items.  

✅ **Show Bill Functionality**  
- A "Show Bill" button allows you to view all previous bills for a selected customer.  
- The bills are listed with a "Show" button that opens a detailed invoice popup, showing all items and total amounts.  

✅ **Scroll to Last Row**  
- After adding a new item, the table automatically scrolls to the last row.  

✅ **Error Handling and Data Integrity**  
- Prevents duplicate phone numbers and item names.  
- Shows informative error messages when required fields are missing.  

✅ **Custom Styling and Design**  
- Clean and modern design using PySide6 with custom background and button colors.  
- Content alignment and cursor changes for a smooth user experience.  

---

## 📊 **Database Schema**  
The project uses an SQLite database with the following table relationships:  

### **1. `customers` Table**  
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key (Auto Increment) |
| name | TEXT | Customer name |
| email | TEXT | Customer email |
| phone | TEXT | Unique customer phone number |

### **2. `bills` Table**  
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key (Auto Increment) |
| customer_id | INTEGER | Foreign Key from `customers` table |
| date | TEXT | Date of the bill |
| total_amount | REAL | Total amount of the bill |

### **3. `bill_items` Table**  
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key (Auto Increment) |
| bill_id | INTEGER | Foreign Key from `bills` table |
| description | TEXT | Item description |
| quantity | INTEGER | Quantity of the item |
| rate | REAL | Rate per unit |

### **4. `items` Table**  
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key (Auto Increment) |
| name | TEXT | Unique item name |
| rate | REAL | Rate per unit |

---

## 🏆 **Possible Future Improvements**  
🔹 Add customer search functionality.  
🔹 Export bill to PDF format.  
🔹 Add discount and tax calculation.  
🔹 Improve table performance for large data.  

---

## 💻 **How to Run**  
1. Clone the repository:  
```bash
git clone https://github.com/yourusername/billing-management-system.git
```
2. Navigate to the project directory:  
```bash
cd billing-management-system
```
3. Install dependencies:  
```bash
pip install PySide6
```
4. Run the app:  
```bash
python main.py
```

---

### 🛠️ **Built With**  
- **Python** – Core programming language  
- **PySide6** – GUI development  
- **SQLite** – Local database  

---

### 🌟 **Contributions**  
Feel free to contribute, report issues, or suggest improvements! 😊  



