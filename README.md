# Expense Tracker

A simple yet powerful desktop application for tracking personal expenses, built with Python and Tkinter.

## Features

- **Dual Storage Options**: Choose between CSV and SQLite database storage
- **Easy Expense Entry**: Quick input of date, category, and amount
- **Visual Analytics**:
  - Category breakdown bar charts
  - Category distribution pie charts
  - Monthly expense trend graphs
- **Data Management**:
  - View recent expenses
  - Monthly expense summaries
  - Export data to CSV or Excel

## Screenshots

![Screenshot 2025-03-19 124614.png](../../Desktop/Screenshot%202025-03-19%20124614.png)

## Requirements

- Python 3.x
- Required packages:
  - pandas
  - matplotlib
  - openpyxl (optional, for Excel export)

## Installation

1. Clone this repository
   ```
   git clone https://github.com/yourusername/expense-tracker.git
   cd expense-tracker
   ```

2. Install required packages
   ```
   pip install -r requirements.txt
   ```

3. Run the application
   ```
   python expense_tracker.py
   ```

## Usage

1. **Add Expenses**:
   - Select your preferred storage method (CSV or SQLite)
   - Enter date, category, and amount
   - Click "Add Expense"

2. **Analyze Expenses**:
   - View category breakdowns with bar charts
   - See spending distribution with pie charts
   - Track spending trends over time
   
3. **Export Data**:
   - Export to CSV for universal compatibility
   - Export to Excel for advanced analysis

## Project Structure

```
expense-tracker/
│
├── expense_tracker.py       # Main application file
├── expenses.db              # SQLite database (created on first run)
├── expenses.csv             # CSV storage file (created on first run)
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```