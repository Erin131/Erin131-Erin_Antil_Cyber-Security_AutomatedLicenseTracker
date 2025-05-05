import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import mysql.connector
from datetime import datetime, timedelta
from plyer import notification

# --- Database Connection ---
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="aman@9971",
        database="DB_ATL"
    )

# --- Core Functions ---
def add_license(serial, name, days):
    try:
        expiry = (datetime.now() + timedelta(days=int(days))).date()
        today = datetime.now().date()
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO equipment (serial_no, name, license_expiry, last_renewed) VALUES (%s, %s, %s, %s)",
                       (serial, name, expiry, today))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Added {name} with expiry on {expiry}.")
    except mysql.connector.IntegrityError:
        messagebox.showerror("Error", "Serial number already exists.")


def delete_license(serial):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM equipment WHERE serial_no = %s", (serial,))
    if cursor.rowcount == 0:
        messagebox.showerror("Not Found", "Serial number not found.")
    else:
        conn.commit()
        messagebox.showinfo("Deleted", f"Deleted equipment with serial {serial}.")
    conn.close()


def view_licenses(tree):
    for row in tree.get_children():
        tree.delete(row)
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM equipment")
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        messagebox.showinfo("Empty", "Sorry, no records available.")
    else:
        for row in rows:
            tree.insert('', 'end', values=row)


def check_and_renew():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT serial_no, name, license_expiry FROM equipment")
    rows = cursor.fetchall()
    today = datetime.now().date()

    if not rows:
        messagebox.showinfo("Empty", "Sorry, no records available.")
        conn.close()
        return

    for serial, name, expiry in rows:
        if expiry <= today:
            new_expiry = today + timedelta(days=365)
            cursor.execute("UPDATE equipment SET license_expiry = %s, last_renewed = %s WHERE serial_no = %s",
                           (new_expiry, today, serial))
            conn.commit()
            notification.notify(title="License Renewed",
                                message=f"{name} ({serial}) renewed till {new_expiry}", timeout=5)
        elif (expiry - today).days <= 7:
            notification.notify(title="License Reminder",
                                message=f"{name} ({serial}) expires on {expiry}", timeout=5)
    conn.close()

# --- GUI Setup ---
root = tk.Tk()
root.title("Automated Medical License Tracker")
root.geometry("750x600")
root.configure(bg="#f0f4f7")

header = tk.Label(root, text="Automated Medical Equipment License Tracker", font=("Helvetica", 18, "bold"), bg="#f0f4f7", fg="#2c3e50")
header.pack(pady=15)

# Add Frame
frame = tk.Frame(root, bg="#f0f4f7")
frame.pack(pady=10)

tk.Label(frame, text="Serial No:", bg="#f0f4f7", fg="#34495e", font=("Helvetica", 10, "bold")).grid(row=0, column=0, padx=10, pady=5)
serial_entry = tk.Entry(frame, width=30)
serial_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(frame, text="Name:", bg="#f0f4f7", fg="#34495e", font=("Helvetica", 10, "bold")).grid(row=1, column=0, padx=10, pady=5)
name_entry = tk.Entry(frame, width=30)
name_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame, text="Valid Days:", bg="#f0f4f7", fg="#34495e", font=("Helvetica", 10, "bold")).grid(row=2, column=0, padx=10, pady=5)
days_entry = tk.Entry(frame, width=30)
days_entry.grid(row=2, column=1, padx=10, pady=5)

add_btn = tk.Button(frame, text="Add License", bg="#27ae60", fg="white", width=20, command=lambda: add_license(serial_entry.get(), name_entry.get(), days_entry.get()))
add_btn.grid(row=3, column=0, columnspan=2, pady=10)

# Delete Section
delete_btn = tk.Button(root, text="Delete License", bg="#c0392b", fg="white", width=20, command=lambda: delete_license(simpledialog.askstring("Delete", "Enter Serial No to delete:")))
delete_btn.pack(pady=10)

# View Table
tree_frame = tk.Frame(root)
tree_frame.pack(pady=10)

style = ttk.Style()
style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
style.configure("Treeview", font=("Helvetica", 10), rowheight=25)

scroll = tk.Scrollbar(tree_frame)
scroll.pack(side=tk.RIGHT, fill=tk.Y)

tree = ttk.Treeview(tree_frame, columns=("Serial", "Name", "Expiry", "Renewed"), show='headings', yscrollcommand=scroll.set, height=10)
scroll.config(command=tree.yview)

for col in ("Serial", "Name", "Expiry", "Renewed"):
    tree.heading(col, text=col)
    tree.column(col, width=150, anchor="center")
tree.pack()

view_btn = tk.Button(root, text="View Licenses", bg="#2980b9", fg="white", width=20, command=lambda: view_licenses(tree))
view_btn.pack(pady=5)

# Check and Renew
check_btn = tk.Button(root, text="Check & Renew Licenses", bg="#8e44ad", fg="white", width=25, command=check_and_renew)
check_btn.pack(pady=10)

root.mainloop()

