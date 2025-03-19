import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QMessageBox, QDialog, QAbstractItemView,
                               QScrollArea)

from PySide6.QtCore import Qt, QDateTime
import sqlite3
from PySide6.QtSql import QSqlDatabase, QSqlQuery
from functools import partial




class BillingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Billing App")
        
        self.setGeometry(400, 150, 600, 250)
        self.setStyleSheet("background-color: #101218; color: white; font-size: 14px;")

        self.layout = QVBoxLayout()

        # Top Section
        top_layout = QHBoxLayout()
        self.welcome_label = QLabel("🛒 Welcome Aditya!")
        self.welcome_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.add_item_button = QPushButton("Add Item")
        self.add_item_button.setStyleSheet("background-color: #0b57d0; color: white; font-weight: bold; padding: 5px 10px; border-radius: 5px;")
        self.add_item_button.setCursor(Qt.PointingHandCursor)
        self.add_item_button.clicked.connect(self.add_item)

        top_layout.addWidget(self.welcome_label)
        top_layout.addStretch()
        top_layout.addWidget(self.add_item_button)
        top_layout.setContentsMargins(0, 0, 0, 20)
        self.layout.addLayout(top_layout)



        # Form Section
        form_layout = QHBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Customer Name")
        self.name_input.setStyleSheet("background-color: #252830; padding: 5px; border-radius: 3px; color: white;")

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Customer Number")
        self.phone_input.setStyleSheet("background-color: #252830; padding: 5px; border-radius: 3px; color: white;")
        self.phone_input.editingFinished.connect(self.on_phone_input_finished)

        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.phone_input)
        self.layout.addLayout(form_layout)

        # Email Section
        email_layout = QHBoxLayout()

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setStyleSheet("background-color: #252830; padding: 5px; border-radius: 3px; color: white;")

        self.send_email_checkbox = QCheckBox("Send Email")
        self.send_email_checkbox.setStyleSheet("font-size: 14px;")

        email_layout.addWidget(self.email_input)
        email_layout.addWidget(self.send_email_checkbox)
        self.layout.addLayout(email_layout)

        # Buttons Section
        button_layout = QHBoxLayout()

        self.create_bill_button = QPushButton("Create Bill")
        self.create_bill_button.setStyleSheet("background-color: #0b57d0; color: white; font-weight: bold; padding: 5px; border-radius: 5px;")
        self.create_bill_button.setCursor(Qt.PointingHandCursor)
        self.create_bill_button.clicked.connect(self.create_bill_table)

        self.show_bill_button = QPushButton("Show Bill")
        self.show_bill_button.setCursor(Qt.PointingHandCursor)
        self.show_bill_button.setStyleSheet("background-color: #0b57d0; color: white; font-weight: bold; padding: 5px; border-radius: 5px;")
        self.show_bill_button.clicked.connect(self.show_bills)
        

        button_layout.addWidget(self.create_bill_button)
        button_layout.addWidget(self.show_bill_button)
        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)
        self.table = None

        # Initialize DB
        self.init_db()

    def init_db(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("data.db")
        if not self.db.open():
            QMessageBox.critical(None, "Database Error", self.db.lastError().text())
            sys.exit(1)

        query = QSqlQuery()
        query.exec("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                phone TEXT UNIQUE
            )
        """)


        query.exec("""
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                date TEXT,
                total_amount REAL
            )
        """)


        query.exec("""
            CREATE TABLE IF NOT EXISTS bill_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id INTEGER,
                description TEXT,
                quantity INTEGER,
                rate REAL
                )
        """)

        query.exec("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                rate REAL
            )
        """)


    def create_bill_table(self):
        self.setGeometry(self.geometry().x(), self.geometry().y(), 600, 412)

        if self.table is None:
            self.table = QTableWidget(5, 5)

            self.table.setStyleSheet("""
                QTableWidget {
                    background-color: #17191e; /* Table background color */
                    color: white; /* Text color */
                    gridline-color: #3A3F44; /* Gridline color */
                    selection-background-color: #3A3F44; /* Selection color */
                }
                QHeaderView::section {
                    background-color: #1b2639; /* Header background color */
                    color: white;
                    padding: 5px;
                    border: 1px solid #3A3F44;
                }
                QTableWidget::item {
                    border-bottom: 1px solid #3A3F44;
                    padding: 5px;
                }
            """)

            self.table.verticalHeader().setVisible(False)
            self.table.setHorizontalHeaderLabels(["S.No.", "Quantity", "Item Description", "Rate", "Amount"])

            header = self.table.horizontalHeader()
        
            # Set fixed width for "S.No." column
            self.table.setColumnWidth(0, 50)  
            # Stretch other columns equally
            for i in range(1, 5):
                header.setSectionResizeMode(i, QHeaderView.Stretch)
          

            # Set initial serial numbers
            self.update_serial_numbers()

            self.table.cellChanged.connect(self.calculate_amount)

            self.layout.addWidget(self.table)

            # Save button
            save_button = QPushButton("Save Bill")
            save_button.setStyleSheet("background-color: #0b57d0; color: white; padding: 5px; border-radius: 5px;")
            save_button.clicked.connect(self.save_bill)
            self.layout.addWidget(save_button)


    #autimatically feth the customer data from DB
    def on_phone_input_finished(self):
        customer_number = self.phone_input.text()
        if customer_number:
            print(f"Customer number entered: {customer_number}")
            # Call any other function you want here
            query = QSqlQuery()
            query.prepare("SELECT name, email FROM customers WHERE phone = ?")
            query.addBindValue(customer_number)
            if query.exec() and query.next():
                name = query.value(0)
                email = query.value(1)
                print(name)
                print(email)
                self.name_input.setText(name)
                self.email_input.setText(email)
  

    def update_serial_numbers(self):
        for row in range(self.table.rowCount()):
            # Center-align and make "S.No." read-only
            sn_item = QTableWidgetItem(str(row + 1))
            sn_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            sn_item.setFlags(Qt.ItemIsEnabled)  # Read-only
            self.table.setItem(row, 0, sn_item)

            # Editable cells for "Quantity", "Item Description", "Rate", "Amount"
            for col in [1, 2, 3, 4]:
                item = QTableWidgetItem("")
                if col == 2:  # "Item Description" - Left align
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
                else:  # All other fields - Center align
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Ensure these cells are editable
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
                self.table.setItem(row, col, item)
 

    def add_row(self):
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        sn_item = QTableWidgetItem(str(row_count + 1))
        sn_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        sn_item.setFlags(Qt.ItemIsEnabled)  # Read-only
        self.table.setItem(row_count, 0, sn_item)

        for col in [1, 2, 3, 4]:
            item = QTableWidgetItem("")
            if col == 2:  # "Item Description" - Left align
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
            else:  # All other fields - Center align
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Ensure these cells are editable
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
            self.table.setItem(row_count, col, item)

        self.table.scrollToItem(self.table.item(row_count, 0), QAbstractItemView.PositionAtBottom)



    def calculate_amount(self, row, column):
        if column == 2:  # Item name
            item_name = self.table.item(row, 2).text()
            query = QSqlQuery()
            query.prepare("SELECT rate FROM items WHERE name = ?")
            query.addBindValue(item_name)
            if query.exec() and query.next():
                rate = query.value(0)
                self.table.setItem(row, 3, QTableWidgetItem(str(rate)))

        if column == 1 or column == 3:  # Quantity or rate
            try:
                quantity = int(self.table.item(row, 1).text())
                rate = float(self.table.item(row, 3).text())
                amount = quantity * rate
                self.table.setItem(row, 4, QTableWidgetItem(str(amount)))

                if row == self.table.rowCount() - 1:
                    self.add_row()


            except Exception:
                pass

    def calculate_total(self):
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            quantity_item = self.table.item(row, 1)
            rate_item = self.table.item(row, 3)

            if quantity_item and rate_item:
                try:
                    quantity = int(quantity_item.text()) if quantity_item.text().strip() else 0
                    rate = float(rate_item.text()) if rate_item.text().strip() else 0.0
                    if quantity > 0 and rate > 0:
                        total = quantity * rate
                        self.table.setItem(row, 4, QTableWidgetItem(f"{total:.2f}"))
                except ValueError:
                    pass
        self.table.blockSignals(False)

    def save_bill(self):
        customer_name = self.name_input.text()
        customer_phone = self.phone_input.text()

        if not customer_name or not customer_phone:
            QMessageBox.warning(self, "Missing Information", "Please enter customer name and phone number.")
            return
        
        
        customer_id = None
        query = QSqlQuery()
        query.prepare("SELECT id FROM customers WHERE phone = ?")
        query.addBindValue(customer_phone)

        if query.exec() and query.next():
            customer_id = query.value(0)
            print("Customer is found.....")

        else:
            # customer not found..in DB
            query = QSqlQuery()
            query.prepare("INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)")
            query.addBindValue(customer_name)
            query.addBindValue(self.email_input.text())
            query.addBindValue(customer_phone)

            if query.exec():
                customer_id = query.lastInsertId()
            else:
                print(f"Error inserting data: {query.lastError().text()}")

        total = 0.0
        for row in range(self.table.rowCount()):
            amount_item = self.table.item(row, 4)
            try:
                amount_item = float(amount_item.text())
                total += amount_item

            except:
                pass

        date = QDateTime.currentDateTime().toString("yyyy-MM-dd")
        
        query = QSqlQuery()
        query.prepare("INSERT INTO bills (customer_id, date, total_amount) VALUES (?, ?, ?)")
        query.addBindValue(customer_id)
        query.addBindValue(date)
        query.addBindValue(total)

        if query.exec():
            bill_id = query.lastInsertId()


        for row in range(self.table.rowCount()):
            quantity_item = self.table.item(row, 1)
            rate_item = self.table.item(row, 3)
            desc_item = self.table.item(row, 2)
            amount_item = self.table.item(row, 4)

            try:
                quantity_item = int(quantity_item.text())
                rate_item = float(rate_item.text())

            except Exception as e:
                print(f"Error : {e}")
                continue

            if quantity_item and rate_item and desc_item and amount_item:
                query.prepare("INSERT INTO bill_items (bill_id, description, quantity, rate) VALUES (?, ?, ?, ?)")
                query.addBindValue(bill_id)
                query.addBindValue(desc_item.text())
                query.addBindValue(quantity_item)
                query.addBindValue(rate_item)
                if query.exec():
                    item_id = query.lastInsertId()
                    print(f"item is saved : {item_id}")
                else:
                    print(f"Error inserting data: {query.lastError().text()}")
                    

        QMessageBox.information(self, "Saved", "Bill saved successfully!")


    def show_bills(self):
        customer_name = self.name_input.text()
        customer_phone = self.phone_input.text()

        if not customer_name:
            QMessageBox.warning(self, "Missing Info", "Please enter customer name.")
            return
    
        if not customer_phone:
            QMessageBox.warning(self, "Missing Info", "Please enter customer phone.")
            return

        
        query = QSqlQuery()
        query.prepare("SELECT id FROM customers WHERE phone = ?")
        query.addBindValue(customer_phone)
        print("exeuinggg....")

        if query.exec() and query.next():
            customer_id = query.value(0)
            print("Customer is found.....", customer_id)
            self.open_bill_viewer(customer_id)
         
        else:
            print(f"Error :{query.lastError().text()}")
            QMessageBox.warning(self, "Not Found", "Customer not found.")


    # Example to open the dialog
    def open_bill_viewer(self, customer_id):

        dialog = BillViewer(customer_id = customer_id)  # Pass customer_id dynamically
        dialog.exec()

    def add_item(self):
        self.item_window = AddItemWindow()
        self.item_window.exec()


class AddItemWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Item")
        self.setGeometry(400, 150, 500, 400)
        self.setStyleSheet("background-color: #101218; color: white;")

        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Rate"])
        self.table.setRowCount(5)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setColumnHidden(0, True)

        layout.addWidget(self.table)

        self.save_btn = QPushButton("Save")
        self.save_btn.setStyleSheet("background-color: #0b57d0; color: white; font-weight: bold; padding: 10px;")
        self.save_btn.clicked.connect(self.save_items)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def save_items(self):
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
            rate = self.table.item(row, 2).text() if self.table.item(row, 2) else ""

            if name and rate:
                query = QSqlQuery()
                query.prepare("INSERT OR REPLACE INTO items (name, rate) VALUES (?, ?)")
                query.addBindValue(name)
                query.addBindValue(rate)
                query.exec()

                if row == self.table.rowCount() - 1:
                    self.table.insertRow(self.table.rowCount())

        self.save_btn.setText("Saved.. Now close")
        self.save_btn.clicked.connect(self.closeWin)

    def closeWin(self):
        # Update the button text when the window is closed
        self.close()


class BillViewer(QDialog):
    def __init__(self, customer_id):
        super().__init__()
        self.setWindowTitle("Customer Bills")
        self.setGeometry(400, 150, 600, 400)
        self.customer_id = customer_id

        print(f"customer_id : {customer_id}")

        layout = QVBoxLayout(self)

        # Scroll area for bill buttons
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        scroll_widget = QWidget()
        self.bill_list_layout = QVBoxLayout(scroll_widget)
        self.scroll_area.setWidget(scroll_widget)

        layout.addWidget(QLabel("Customer Bills:"))
        layout.addWidget(self.scroll_area)

        # Table to show bill items
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([ "Quantity", "Description", "Rate", "Amount"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.total_amnt = QLabel("")
        self.total_amnt.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.total_amnt.setAlignment(Qt.AlignRight)
        self.total_amnt.setContentsMargins(2, 2, 13, 0)

        layout.addWidget(self.total_amnt)

        self.load_bills()

    def load_bills(self):
        query = QSqlQuery()
        query.prepare("SELECT id, date, total_amount FROM bills WHERE customer_id = ?")
        query.addBindValue(self.customer_id)
        if query.exec():
            while query.next():
                bill_id = query.value(0)
                date = query.value(1)
                total_amount = query.value(2)

                # Create a button for each bill
                button = QPushButton(f"Bill Number :  {bill_id}              date = {date}              Total Amount = {total_amount}           Show")
                button.clicked.connect(partial(self.show_bill_items, bill_id))

                button.setStyleSheet("background-color: #0b57d0; color: white; padding: 5px; font-weight: bold; border-radius: 5px;")
                button.setCursor(Qt.PointingHandCursor)
                self.bill_list_layout.addWidget(button)

        else:
            QMessageBox.information(self, "No Bills", "No bills found for this customer.")


    def show_bill_items(self, bill_id):
        self.table.setRowCount(0)  # Clear existing rows
        print("BillId==> ",bill_id)

       
        query = QSqlQuery()
        query.prepare("SELECT description, quantity, rate FROM bill_items WHERE bill_id = ?")
        query.addBindValue(int(bill_id))
        if query.exec():
            row = 0
            total = 0
            while query.next():
                description = query.value(0)
                quantity = query.value(1)
                rate = query.value(2)
                amount = quantity * rate

                print(f"Des      = {description}")
                print(f"quantity = {quantity}")
                print(f"rate     = {rate}")
                print(f"amount   = {amount}")

                total += amount

                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(quantity)))
                self.table.setItem(row, 1, QTableWidgetItem(str(description)))
                self.table.setItem(row, 2, QTableWidgetItem(f"{rate}"))
                self.table.setItem(row, 3, QTableWidgetItem(f"{amount}"))

                for col in range(4):
                    self.table.item(row, col).setTextAlignment(Qt.AlignCenter)

                row += 1

            self.total_amnt.setText(f"Grand Total : {total}")

        else:
            print(f"Error inserting data: {query.lastError().text()}")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BillingApp()
    window.show()
    sys.exit(app.exec())
