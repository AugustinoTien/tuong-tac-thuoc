import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# --- Kết nối CSDL MySQL ---
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="drug_interaction"
)
cursor = conn.cursor()

# --- Giao diện chính ---
root = tb.Window(themename="flatly")
root.title("💊 PHẦN MỀM QUẢN LÝ TƯƠNG TÁC THUỐC")
root.geometry("1200x720")

# --- Thanh tiêu đề ---
titlebar = tb.Label(root, text="💊 PHẦN MỀM QUẢN LÝ TƯƠNG TÁC THUỐC", font=("Segoe UI", 18, "bold"), bootstyle="inverse-primary")
titlebar.pack(fill=X, pady=(0, 10))

# --- Tab chuyển đổi giữa các bảng ---
tabs = tb.Notebook(root)
tabs.pack(fill=BOTH, expand=True)
tab_frames = {}

# --- Các biến ---
bang_hien_tai = tb.StringVar()
nhap_lieu = {}

# --- Tên tiếng Việt ---
nhan_viet_hoa = {
    "Drugs": {
        "drug_id": "Mã thuốc",
        "drug_name": "Tên thuốc",
        "generic_name": "Hoạt chất",
        "drug_class": "Nhóm thuốc",
        "manufacturer": "Hãng sản xuất"
    },
    "DrugLeaflets": {
        "leaflet_id": "Mã tờ hướng dẫn",
        "drug_id": "Thuốc",
        "active_ingredient": "Hoạt chất chính",
        "indication": "Chỉ định",
        "dosage": "Liều dùng",
        "administration": "Cách dùng",
        "contraindications": "Chống chỉ định",
        "precautions": "Thận trọng",
        "side_effects": "Tác dụng phụ",
        "interaction_text": "Tương tác",
        "storage": "Bảo quản",
        "warnings": "Cảnh báo"
    },
    "ParsedInteractions": {
        "interaction_id": "Mã tương tác",
        "source_drug_id": "Thuốc A",
        "target_drug_id": "Thuốc B",
        "interaction_level": "Mức độ",
        "evidence_text": "Chi tiết"
    }
}

# --- Cập nhật hàm chọn dòng ---
def chon_dong(tree):
    bang = bang_hien_tai.get()
    selected = tree.focus()
    if not selected:
        return
    values = tree.item(selected, 'values')
    for k, v in zip(nhap_lieu.keys(), values):
        widget = nhap_lieu[k]
        if isinstance(widget, ttk.Combobox):
            for name, id in nhap_lieu.get("_drug_map", {}).items():
                if str(id) == str(v):
                    widget.set(name)
                    break
        else:
            widget.config(state='normal')
            widget.delete(0, tk.END)
            widget.insert(0, v)
            if k.endswith('_id'):
                widget.config(state='disabled')

# --- Thêm dòng này vào cuối hàm tai_du_lieu để cập nhật bảng hiện tại ---
def tai_du_lieu(bang, frame):
    bang_hien_tai.set(bang)  # Cập nhật bảng hiện tại
    form_frame, btn_frame, tree, label_hint = frame
    for item in tree.get_children():
        tree.delete(item)
    for widget in form_frame.winfo_children():
        widget.destroy()
    nhap_lieu.clear()
    label_hint.config(text="")

    cursor.execute(f"SELECT * FROM {bang}")
    rows = cursor.fetchall()
    cols = cursor.column_names
    tree["columns"] = cols
    tree["show"] = "headings"
    for col in cols:
        tree.heading(col, text=nhan_viet_hoa[bang].get(col, col))
        tree.column(col, anchor=tk.W, width=150)
    for row in rows:
        tree.insert("", tk.END, values=row)

    drug_map = {}
    if bang in ["DrugLeaflets", "ParsedInteractions"]:
        cursor.execute("SELECT drug_id, drug_name FROM Drugs")
        drug_map = {f"{name} (ID {id})": id for id, name in cursor.fetchall()}
        nhap_lieu["_drug_map"] = drug_map

    for i, col in enumerate(cols):
        tb.Label(form_frame, text=nhan_viet_hoa[bang].get(col, col)).grid(row=i, column=0, sticky='w')
        if bang == "DrugLeaflets" and col == "drug_id" or bang == "ParsedInteractions" and col in ["source_drug_id", "target_drug_id"]:
            cb = ttk.Combobox(form_frame, values=list(drug_map.keys()), width=47)
            cb.grid(row=i, column=1, pady=2, sticky='w')
            if bang == "ParsedInteractions":
                cb.bind("<<ComboboxSelected>>", lambda e: kiem_tra_tuong_tac(label_hint))
            nhap_lieu[col] = cb
        else:
            ent = ttk.Entry(form_frame, width=50)
            ent.grid(row=i, column=1, pady=2, sticky='w')
            if i == 0:
                ent.config(state='disabled')
            nhap_lieu[col] = ent

    tree.bind("<ButtonRelease-1>", lambda e: chon_dong(tree))
