import os
import csv
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Configuration
DB_FILE = "expenses.db"
CSV_FILE = "expenses.csv"


# Database initialization
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            amount REAL
        )
    """)
    conn.commit()
    conn.close()


# CSV Functions
def add_expense_to_csv(date, category, amount):
    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["Date", "Category", "Amount"])

        writer.writerow([date, category, amount])

    print(f"✅ Expense added: {amount} in {category} on {date}")


def load_expenses_from_csv():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame(columns=["Date", "Category", "Amount"])

    return pd.read_csv(CSV_FILE)


# SQLite Functions
def add_expense_to_db(date, category, amount):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)",
                   (date, category, amount))
    conn.commit()
    conn.close()


def get_expenses_from_db():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT date, category, amount FROM expenses", conn)
    conn.close()
    return df


# Analysis Functions
def analyze_category_expenses(df):
    if df.empty:
        return pd.Series()

    # Convert Amount to numeric if needed
    df["Amount"] = pd.to_numeric(df["Amount"])

    # Calculate total spending per category
    return df.groupby("Category")["Amount"].sum()


def analyze_monthly_expenses(df):
    if df.empty:
        return pd.Series()

    # Convert Date to datetime
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    # Convert Amount to numeric if needed
    df["Amount"] = pd.to_numeric(df["Amount"])

    # Extract year-month and sum expenses
    df["Year-Month"] = df["Date"].dt.to_period("M")
    return df.groupby("Year-Month")["Amount"].sum()


# Visualization Functions
def plot_category_expenses(df):
    if df.empty:
        messagebox.showerror("Error", "No expense data found!")
        return

    category_totals = analyze_category_expenses(df)

    plt.figure(figsize=(8, 5))
    category_totals.plot(kind="bar", color="skyblue", edgecolor="black")
    plt.xlabel("Category")
    plt.ylabel("Total Spent (₹)")
    plt.title("📊 Expense Breakdown by Category")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()


def plot_category_pie_chart(df):
    if df.empty:
        messagebox.showerror("Error", "No expense data found!")
        return

    category_totals = analyze_category_expenses(df)

    plt.figure(figsize=(8, 8))
    plt.pie(category_totals, labels=category_totals.index, autopct='%1.1f%%',
            startangle=140, colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])
    plt.title("Expense Distribution by Category")
    plt.axis('equal')  # Equal aspect ratio for circular pie chart
    plt.show()


def plot_monthly_trend(df):
    if df.empty:
        messagebox.showerror("Error", "No expense data found!")
        return

    monthly_totals = analyze_monthly_expenses(df)

    if len(monthly_totals) == 0:
        messagebox.showerror("Error", "No valid date data found!")
        return

    plt.figure(figsize=(8, 5))
    plt.plot(monthly_totals.index.astype(str), monthly_totals.values,
             marker="o", linestyle="-", color="b")
    plt.xlabel("Month")
    plt.ylabel("Total Spent (₹)")
    plt.title("📈 Monthly Expense Trend")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()


# Export Functions
def export_expenses(df, file_format="csv"):
    if df.empty:
        messagebox.showerror("Error", "No expense data to export!")
        return

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_name = f"expenses_{timestamp}"

    try:
        if file_format.lower() == "csv":
            df.to_csv(f"{file_name}.csv", index=False)
            messagebox.showinfo("Success", f"Expenses exported successfully as {file_name}.csv")

        elif file_format.lower() == "excel":
            # Check if required library is available
            try:
                df.to_excel(f"{file_name}.xlsx", index=False)
                messagebox.showinfo("Success", f"Expenses exported successfully as {file_name}.xlsx")
            except ImportError:
                messagebox.showerror("Error", "Excel export requires openpyxl package. Please install it using pip.")
        else:
            messagebox.showerror("Error", "Invalid format! Please choose 'csv' or 'excel'.")
    except Exception as e:
        messagebox.showerror("Error", f"Export failed: {str(e)}")


# GUI Class
class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("400x500")

        # Set storage mode (CSV or SQLite)
        self.storage_mode = tk.StringVar(value="csv")

        # Create tabs
        self.tab_control = ttk.Notebook(root)

        # Tab 1: Add Expense
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab1, text="Add Expense")

        # Tab 2: View/Analyze
        self.tab2 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab2, text="Analyze")

        self.tab_control.pack(expand=1, fill="both")

        # Setup tabs
        self.setup_add_expense_tab()
        self.setup_analyze_tab()

        # Load initial data
        self.load_data()

    def setup_add_expense_tab(self):
        # Storage mode selection
        ttk.Label(self.tab1, text="Storage Mode:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ttk.Radiobutton(self.tab1, text="CSV", variable=self.storage_mode, value="csv").grid(row=0, column=1,
                                                                                             sticky="w")
        ttk.Radiobutton(self.tab1, text="SQLite", variable=self.storage_mode, value="sqlite").grid(row=0, column=2,
                                                                                                   sticky="w")

        # Date entry
        ttk.Label(self.tab1, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.entry_date = ttk.Entry(self.tab1)
        self.entry_date.grid(row=1, column=1, columnspan=2, sticky="we", padx=10, pady=5)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Category entry
        ttk.Label(self.tab1, text="Category:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.entry_category = ttk.Entry(self.tab1)
        self.entry_category.grid(row=2, column=1, columnspan=2, sticky="we", padx=10, pady=5)

        # Amount entry
        ttk.Label(self.tab1, text="Amount:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.entry_amount = ttk.Entry(self.tab1)
        self.entry_amount.grid(row=3, column=1, columnspan=2, sticky="we", padx=10, pady=5)

        # Add button
        ttk.Button(self.tab1, text="Add Expense", command=self.add_expense).grid(row=4, column=0, columnspan=3,
                                                                                 sticky="we", padx=10, pady=10)

        # Recent expenses frame
        ttk.Label(self.tab1, text="Recent Expenses:").grid(row=5, column=0, columnspan=3, sticky="w", padx=10, pady=5)

        self.recent_expenses = ttk.Treeview(self.tab1, columns=("Date", "Category", "Amount"), show="headings",
                                            height=10)
        self.recent_expenses.grid(row=6, column=0, columnspan=3, sticky="nsew", padx=10, pady=5)

        self.recent_expenses.heading("Date", text="Date")
        self.recent_expenses.heading("Category", text="Category")
        self.recent_expenses.heading("Amount", text="Amount")

        self.recent_expenses.column("Date", width=100)
        self.recent_expenses.column("Category", width=100)
        self.recent_expenses.column("Amount", width=100)

    def setup_analyze_tab(self):
        # Analysis buttons
        ttk.Button(self.tab2, text="Show Category Breakdown", command=self.show_category_breakdown).grid(row=0,
                                                                                                         column=0,
                                                                                                         sticky="we",
                                                                                                         padx=10,
                                                                                                         pady=10)
        ttk.Button(self.tab2, text="Show Category Pie Chart", command=self.show_category_pie).grid(row=1, column=0,
                                                                                                   sticky="we", padx=10,
                                                                                                   pady=10)
        ttk.Button(self.tab2, text="Show Monthly Trend", command=self.show_monthly_trend).grid(row=2, column=0,
                                                                                               sticky="we", padx=10,
                                                                                               pady=10)

        # Export buttons
        ttk.Label(self.tab2, text="Export Data:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        ttk.Button(self.tab2, text="Export to CSV", command=lambda: self.export_data("csv")).grid(row=4, column=0,
                                                                                                  sticky="we", padx=10,
                                                                                                  pady=5)
        ttk.Button(self.tab2, text="Export to Excel", command=lambda: self.export_data("excel")).grid(row=5, column=0,
                                                                                                      sticky="we",
                                                                                                      padx=10, pady=5)

        # Monthly summary
        ttk.Label(self.tab2, text="Monthly Summary:").grid(row=6, column=0, sticky="w", padx=10, pady=5)
        self.monthly_summary = ttk.Treeview(self.tab2, columns=("Month", "Total"), show="headings", height=6)
        self.monthly_summary.grid(row=7, column=0, sticky="nsew", padx=10, pady=5)

        self.monthly_summary.heading("Month", text="Month")
        self.monthly_summary.heading("Total", text="Total")

        self.monthly_summary.column("Month", width=150)
        self.monthly_summary.column("Total", width=150)

    def load_data(self):
        # Load expenses from selected storage
        if self.storage_mode.get() == "sqlite":
            init_db()  # Ensure DB exists
            self.df = get_expenses_from_db()
        else:  # CSV
            self.df = load_expenses_from_csv()

        # Update UI
        self.update_recent_expenses()
        self.update_monthly_summary()

    def add_expense(self):
        date = self.entry_date.get()
        category = self.entry_category.get()
        amount = self.entry_amount.get()

        if not (date and category and amount):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number!")
            return

        # Add expense to selected storage
        if self.storage_mode.get() == "sqlite":
            add_expense_to_db(date, category, amount)
        else:  # CSV
            add_expense_to_csv(date, category, amount)

        # Reload data
        self.load_data()

        # Clear inputs
        self.entry_category.delete(0, tk.END)
        self.entry_amount.delete(0, tk.END)

        messagebox.showinfo("Success", "Expense Added Successfully!")

    def update_recent_expenses(self):
        # Clear existing entries
        for item in self.recent_expenses.get_children():
            self.recent_expenses.delete(item)

        # Add expenses to treeview
        if not self.df.empty:
            # Sort by date (most recent first) and take last 10
            temp_df = self.df.copy()
            if "Date" in temp_df.columns:
                temp_df["Date"] = pd.to_datetime(temp_df["Date"], errors="coerce")
                recent_expenses = temp_df.sort_values("Date", ascending=False).head(10)

                for _, row in recent_expenses.iterrows():
                    date = row["Date"].strftime("%Y-%m-%d") if isinstance(row["Date"], pd.Timestamp) else row["Date"]
                    self.recent_expenses.insert("", tk.END, values=(date, row["Category"], f"{row['Amount']:.2f}"))

    def update_monthly_summary(self):
        # Clear existing entries
        for item in self.monthly_summary.get_children():
            self.monthly_summary.delete(item)

        # Get monthly totals
        monthly_totals = analyze_monthly_expenses(self.df)

        # Add to treeview
        for month, total in monthly_totals.items():
            self.monthly_summary.insert("", tk.END, values=(str(month), f"{total:.2f}"))

    def show_category_breakdown(self):
        plot_category_expenses(self.df)

    def show_category_pie(self):
        plot_category_pie_chart(self.df)

    def show_monthly_trend(self):
        plot_monthly_trend(self.df)

    def export_data(self, format_type):
        export_expenses(self.df, format_type)


# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()