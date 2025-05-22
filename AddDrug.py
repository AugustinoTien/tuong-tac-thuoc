import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3  # 👉 Đổi sang mysql.connector nếu dùng MySQL

# Kết nối CSDL SQLite
conn = sqlite3.connect('drug_interaction.db')
cursor = conn.cursor()

# Tạo bảng nếu chưa có
cursor.execute("""
CREATE TABLE IF NOT EXISTS Drugs (
    drug_id INTEGER PRIMARY KEY AUTOINCREMENT,
    drug_name TEXT NOT NULL,
    generic_name TEXT,
    drug_class TEXT,
    manufacturer TEXT
);
""")
conn.commit()

# === Hàm xử lý ===
def load_data():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM Drugs")
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)

def clear_form():
    entry_id.config(state='normal')
    entry_id.delete(0, tk.END)
    entry_id.config(state='disabled')
    entry_name.delete(0, tk.END)
    entry_generic.delete(0, tk.END)
    entry_class.delete(0, tk.END)
    entry_manu.delete(0, tk.END)

def insert_drug():
    name = entry_name.get()
    generic = entry_generic.get()
    dclass = entry_class.get()
    manu = entry_manu.get()
    if not name:
        messagebox.showwarning("Lỗi", "Tên thuốc không được để trống")
        return
    cursor.execute("INSERT INTO Drugs (drug_name, generic_name, drug_class, manufacturer) VALUES (?, ?, ?, ?)",
                   (name, generic, dclass, manu))
    conn.commit()
    load_data()
    clear_form()

def update_drug():
    if entry_id.get() == "":
        messagebox.showwarning("Lỗi", "Vui lòng chọn thuốc để sửa")
        return
    cursor.execute("""
        UPDATE Drugs SET
            drug_name = ?,
            generic_name = ?,
            drug_class = ?,
            manufacturer = ?
        WHERE drug_id = ?
    """, (
        entry_name.get(),
        entry_generic.get(),
        entry_class.get(),
        entry_manu.get(),
        entry_id.get()
    ))
    conn.commit()
    load_data()
    clear_form()

def delete_drug():
    if entry_id.get() == "":
        messagebox.showwarning("Lỗi", "Vui lòng chọn thuốc để xoá")
        return
    confirm = messagebox.askyesno("Xác nhận xoá", "Bạn có chắc muốn xoá thuốc này?")
    if confirm:
        cursor.execute("DELETE FROM Drugs WHERE drug_id = ?", (entry_id.get(),))
        conn.commit()
        load_data()
        clear_form()

def on_row_select(event):
    selected = tree.focus()
    if not selected:
        return
    values = tree.item(selected, 'values')
    entry_id.config(state='normal')
    entry_id.delete(0, tk.END)
    entry_id.insert(0, values[0])
    entry_id.config(state='disabled')
    entry_name.delete(0, tk.END)
    entry_name.insert(0, values[1])
    entry_generic.delete(0, tk.END)
    entry_generic.insert(0, values[2])
    entry_class.delete(0, tk.END)
    entry_class.insert(0, values[3])
    entry_manu.delete(0, tk.END)
    entry_manu.insert(0, values[4])

# === Giao diện ===
root = tk.Tk()
root.title("Quản lý danh sách thuốc")
root.geometry("1000x600")

form_frame = tk.Frame(root)
form_frame.pack(pady=10)

# Form input
tk.Label(form_frame, text="ID").grid(row=0, column=0)
entry_id = tk.Entry(form_frame, state='disabled', width=10)
entry_id.grid(row=0, column=1, padx=5)

tk.Label(form_frame, text="Tên thuốc").grid(row=0, column=2)
entry_name = tk.Entry(form_frame)
entry_name.grid(row=0, column=3, padx=5)

tk.Label(form_frame, text="Hoạt chất").grid(row=0, column=4)
entry_generic = tk.Entry(form_frame)
entry_generic.grid(row=0, column=5, padx=5)

tk.Label(form_frame, text="Nhóm").grid(row=1, column=0)
entry_class = tk.Entry(form_frame)
entry_class.grid(row=1, column=1, padx=5)

tk.Label(form_frame, text="Hãng SX").grid(row=1, column=2)
entry_manu = tk.Entry(form_frame)
entry_manu.grid(row=1, column=3, padx=5)

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="Thêm", command=insert_drug, width=10).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Sửa", command=update_drug, width=10).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Xoá", command=delete_drug, width=10).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Làm mới", command=clear_form, width=10).pack(side=tk.LEFT, padx=5)

# Bảng dữ liệu
tree = ttk.Treeview(root, columns=("ID", "Tên thuốc", "Hoạt chất", "Nhóm", "Hãng SX"), show="headings")
tree.heading("ID", text="ID")
tree.heading("Tên thuốc", text="Tên thuốc")
tree.heading("Hoạt chất", text="Hoạt chất")
tree.heading("Nhóm", text="Nhóm")
tree.heading("Hãng SX", text="Hãng SX")
tree.pack(fill=tk.BOTH, expand=True, pady=10)
tree.bind("<ButtonRelease-1>", on_row_select)

load_data()
root.mainloop()
