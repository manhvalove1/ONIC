import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QLineEdit, QMessageBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ================== ДАННЫЕ ==================
income = 0.0
expenses = []
savings = 0.0

def load_data():
    global income, expenses, savings
    try:
        with open('transactions.json', 'r') as file:
            data = json.load(file)
            income = data.get('income', 0.0)
            expenses = data.get('expenses', [])
            savings = data.get('savings', 0.0)
    except FileNotFoundError:
        pass

def save_data():
    global income, expenses, savings
    data = {
        'income': income,
        'expenses': expenses,
        'savings': savings
    }
    with open('transactions.json', 'w') as file:
        json.dump(data, file)

# ================== GUI ==================
class FinanceTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Personal Finance Tracker")
        self.setGeometry(200, 200, 600, 500)
        load_data()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # ===== ДОХОД =====
        self.income_input = QLineEdit()
        self.income_input.setPlaceholderText("Enter income amount")
        self.income_btn = QPushButton("Add Income")
        self.income_btn.clicked.connect(self.add_income)
        layout.addWidget(QLabel("Income:"))
        layout.addWidget(self.income_input)
        layout.addWidget(self.income_btn)

        # ===== РАСХОД =====
        self.expense_desc = QLineEdit()
        self.expense_desc.setPlaceholderText("Expense description")
        self.expense_amount = QLineEdit()
        self.expense_amount.setPlaceholderText("Expense amount")
        self.expense_category = QLineEdit()
        self.expense_category.setPlaceholderText("Expense category")
        self.expense_btn = QPushButton("Add Expense")
        self.expense_btn.clicked.connect(self.add_expense)

        layout.addWidget(QLabel("Expense:"))
        layout.addWidget(self.expense_desc)
        layout.addWidget(self.expense_amount)
        layout.addWidget(self.expense_category)
        layout.addWidget(self.expense_btn)

        # ===== КНОПКИ РАСЧЕТ =====
        self.savings_btn = QPushButton("Calculate Savings")
        self.savings_btn.clicked.connect(self.calculate_savings)
        layout.addWidget(self.savings_btn)

        self.report_category = QLineEdit()
        self.report_category.setPlaceholderText("Enter category for report")
        self.report_btn = QPushButton("Generate Expense Report")
        self.report_btn.clicked.connect(self.generate_expense_report)
        layout.addWidget(self.report_category)
        layout.addWidget(self.report_btn)

        self.chart_btn = QPushButton("Generate Expense Chart")
        self.chart_btn.clicked.connect(self.generate_expense_chart)
        layout.addWidget(self.chart_btn)

        self.setLayout(layout)

    # ================== ФУНКЦИИ ==================
    def add_income(self):
        global income
        try:
            amount = float(self.income_input.text())
            income += amount
            QMessageBox.information(self, "Success", f"Income of {amount} added!")
            self.income_input.clear()
        except ValueError:
            QMessageBox.warning(self, "Error", "Enter a valid number!")

    def add_expense(self):
        global expenses
        try:
            amount = float(self.expense_amount.text())
            desc = self.expense_desc.text()
            cat = self.expense_category.text()
            expense = {'description': desc, 'amount': amount, 'category': cat}
            expenses.append(expense)
            QMessageBox.information(self, "Success", "Expense added!")
            self.expense_desc.clear()
            self.expense_amount.clear()
            self.expense_category.clear()
        except ValueError:
            QMessageBox.warning(self, "Error", "Enter a valid number!")

    def calculate_savings(self):
        global savings
        savings = income - sum(exp['amount'] for exp in expenses)
        QMessageBox.information(self, "Savings", f"Your savings: {savings}")

    def generate_expense_report(self):
        category = self.report_category.text()
        total = sum(exp['amount'] for exp in expenses if exp['category'] == category)
        if total == 0:
            QMessageBox.information(self, "Report", f"No expenses found for category: {category}")
        else:
            QMessageBox.information(self, "Report", f"Total spent on {category}: {total}")

    def generate_expense_chart(self):
        if not expenses:
            QMessageBox.information(self, "Chart", "No expenses to show!")
            return

        categories = list({exp['category'] for exp in expenses})
        values = [sum(exp['amount'] for exp in expenses if exp['category'] == cat) for cat in categories]

        # Создаём график
        fig = Figure(figsize=(5, 4))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.pie(values, labels=categories, autopct='%1.1f%%')
        ax.set_title("Expenses by Category")
        fig.tight_layout()

        # Создаём окно для графика
        chart_window = QWidget()
        chart_window.setWindowTitle("Expense Chart")
        chart_layout = QVBoxLayout()
        chart_layout.addWidget(canvas)
        chart_window.setLayout(chart_layout)
        chart_window.setGeometry(300, 300, 500, 400)
        chart_window.show()

# ================== MAIN ==================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FinanceTracker()
    window.show()
    sys.exit(app.exec_())
