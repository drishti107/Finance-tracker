import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime

# Paths
expense_file_path = "expense.csv"
recurring_file_path = "recurring.csv"
budget = 3000

# ---------- Functions ----------
def save_expense():
    name = name_entry.get()
    amount = amount_entry.get()
    category = category_var.get()
    
    if not name or not amount or not category:
        messagebox.showerror("Error", "Please fill all fields!")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number!")
        return

    date = datetime.now().strftime("%Y-%m-%d")
    
    with open(expense_file_path, "a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, name, amount, category])

    messagebox.showinfo("Success", "Expense saved successfully!")
    name_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    
    update_expense_table()
    update_total_spent()
    check_budget_alert()

def delete_expense():
    selected_item = table.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select an expense to delete.")
        return

    item = table.item(selected_item)
    values = item['values']

    if not values:
        return

    expenses = []
    with open(expense_file_path, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            if row != values:
                expenses.append(row)

    with open(expense_file_path, "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(expenses)

    table.delete(selected_item)
    messagebox.showinfo("Success", "Expense deleted successfully!")
    update_total_spent()

def update_expense_table():
    for row in table.get_children():
        table.delete(row)

    if os.path.exists(expense_file_path):
        with open(expense_file_path, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                table.insert("", "end", values=row)

def update_total_spent():
    total_spent = 0
    if os.path.exists(expense_file_path):
        with open(expense_file_path, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                try:
                    total_spent += float(row[2])
                except ValueError:
                    continue

    total_spent_label.config(text=f"Total Spent: ₹{total_spent:.2f}")

def check_budget_alert():
    total_spent = 0
    current_month = datetime.now().strftime("%Y-%m")

    if os.path.exists(expense_file_path):
        with open(expense_file_path, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                date, _, amount, _ = row
                if date.startswith(current_month):
                    total_spent += float(amount)

    if total_spent >= budget * 0.8:
        messagebox.showwarning("Budget Alert", f"You've spent ₹{total_spent:.2f}, over your budget!")

def apply_table_colors():
    for i, item in enumerate(table.get_children()):
        if i % 2 == 0:
            table.item(item, tags=("evenrow",))
        else:
            table.item(item, tags=("oddrow",))

def add_recurring_expenses():
    current_month = datetime.now().strftime("%Y-%m")

    if os.path.exists(recurring_file_path):
        with open(recurring_file_path, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                name, amount, category = row
                with open(expense_file_path, "a", newline='') as exp_file:
                    writer = csv.writer(exp_file)
                    writer.writerow([current_month + "-01", name, amount, category])

        messagebox.showinfo("Success", "Recurring expenses added!")

def search_expenses():
    search_term = search_entry.get().lower()

    for row in table.get_children():
        table.delete(row)

    if os.path.exists(expense_file_path):
        with open(expense_file_path, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if any(search_term in col.lower() for col in row):
                    table.insert("", "end", values=row)

# ---------- GUI ----------
root = tk.Tk()
root.title("Finance Tracker")
root.geometry("600x700")

frame = tk.Frame(root)
frame.pack(pady=10)

# Input fields
tk.Label(frame, text="Expense Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
name_entry = tk.Entry(frame)
name_entry.grid(row=0, column=1)

tk.Label(frame, text="Expense Amount:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
amount_entry = tk.Entry(frame)
amount_entry.grid(row=1, column=1)

tk.Label(frame, text="Category:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
category_var = tk.StringVar()
category_menu = ttk.Combobox(frame, textvariable=category_var, values=["Food", "College", "Fun", "Clothes", "Living", "Misc"], state="readonly")
category_menu.grid(row=2, column=1)

# Buttons
tk.Button(root, text="Add Expense", command=save_expense).pack(pady=5)
tk.Button(root, text="Add Recurring", command=add_recurring_expenses).pack(pady=5)
tk.Button(root, text="Search", command=search_expenses).pack(pady=5)

# Search field
search_entry = tk.Entry(root, width=30)
search_entry.pack(pady=5)

# Total spent label
total_spent_label = tk.Label(root, text="Total Spent: ₹0.00", font=("Arial", 12, "bold"))
total_spent_label.pack(pady=5)

# Table
table = ttk.Treeview(root, columns=("Date", "Name", "Amount", "Category"), show="headings")
table.heading("Date", text="Date")
table.heading("Name", text="Expense Name")
table.heading("Amount", text="Amount (₹)")
table.heading("Category", text="Category")
table.pack(pady=10)

update_expense_table()
update_total_spent()

root.mainloop()
