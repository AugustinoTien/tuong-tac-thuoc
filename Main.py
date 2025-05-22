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

# --- Kiểm tra tương tác thuốc ---
def kiem_tra_tuong_tac(label_hint):
    src = nhap_lieu.get("source_drug_id")
    tgt = nhap_lieu.get("target_drug_id")
    drug_map = nhap_lieu.get("_drug_map", {})
    if not src or not tgt:
        label_hint.config(text="❗ Vui lòng chọn đủ cả hai thuốc")
        return
    src_id = drug_map.get(src.get())
    tgt_id = drug_map.get(tgt.get())
    if not src_id or not tgt_id:
        label_hint.config(text="❗ Không tìm thấy ID của thuốc")
        return
    cursor.execute("""
        SELECT interaction_level, evidence_text FROM ParsedInteractions
        WHERE (source_drug_id = %s AND target_drug_id = %s)
           OR (source_drug_id = %s AND target_drug_id = %s)
    """, (src_id, tgt_id, tgt_id, src_id))
    result = cursor.fetchone()
    if result:
        label_hint.config(text=f"⚠️ Tương tác đã tồn tại: {result[0]} – {result[1]}")
    else:
        label_hint.config(text="✅ Không tìm thấy tương tác. Đã tạo mới.")
        cursor.execute("""
            INSERT INTO ParsedInteractions (source_drug_id, target_drug_id, interaction_level, evidence_text)
            VALUES (%s, %s, %s, %s)
        """, (src_id, tgt_id, "Chưa xác định", "Chưa có thông tin chi tiết"))
        conn.commit()
        tai_du_lieu("ParsedInteractions", tab_frames["ParsedInteractions"])

# --- Cập nhật hàm chọn dòng ---
def chon_dong(tree):
    if not nhap_lieu or len(nhap_lieu) < 2:
        print("[DEBUG] Bỏ qua chọn dòng vì form chưa khởi tạo xong.")
        return
    bang = bang_hien_tai.get()
    selected = tree.focus()
    if not selected:
        return
    tree.selection_set(selected)
    values = tree.item(selected, 'values')
    cols = getattr(tree, "_col_order", [])

    if len(values) != len(cols):
        print("⚠️ Số lượng giá trị không khớp với số cột.")
        return

    for k, v in zip(cols, values):
        k = str(k).strip()
        if k not in nhap_lieu:
            print(f"[DEBUG] Không tìm thấy widget cho key: {k} — nhap_lieu keys: {list(nhap_lieu.keys())}")
            continue
        widget = nhap_lieu[k]
        if isinstance(widget, ttk.Combobox) and bang in ["DrugLeaflets", "ParsedInteractions"]:
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

def tai_du_lieu(bang, frame):
    bang_hien_tai.set(bang)
    form_frame, btn_frame, tree, label_hint = frame
    for item in tree.get_children():
        tree.delete(item)
    for widget in form_frame.winfo_children():
        widget.destroy()
    for widget in btn_frame.winfo_children():
        widget.destroy()
    nhap_lieu.clear()
    label_hint.config(text="")

    cursor.execute(f"SELECT * FROM {bang}")
    rows = cursor.fetchall()
    cols = cursor.column_names
    cols = [col.decode() if isinstance(col, bytes) else col for col in cols]
    tree["columns"] = cols
    tree._col_order = cols  # lưu thứ tự cột thực tế để dùng lại
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

    for i, col_raw in enumerate(cols):
        col = str(col_raw)
        tb.Label(form_frame, text=nhan_viet_hoa[bang].get(col, col)).grid(row=i, column=0, sticky='w')
        if bang == "DrugLeaflets" and col == "drug_id" or bang == "ParsedInteractions" and col in ["source_drug_id", "target_drug_id"]:
            cb = ttk.Combobox(form_frame, values=list(drug_map.keys()), width=47)
            cb.grid(row=i, column=1, pady=2, sticky='w')
            if bang == "ParsedInteractions" and not hasattr(cb, "_bound"):
                cb.bind("<<ComboboxSelected>>", lambda e: kiem_tra_tuong_tac(label_hint))
                cb._bound = True
            nhap_lieu[col] = cb
        else:
            ent = ttk.Entry(form_frame, width=50)
            ent.grid(row=i, column=1, pady=2, sticky='w')
            # Đừng disable entry tại đây, sẽ làm mất dữ liệu khi chọn dòng
            nhap_lieu[col] = ent

    tree.bind("<ButtonRelease-1>", lambda e: chon_dong(tree))

    def insert():
        cols = tree._col_order
        values = []
        for k in cols:
            w = nhap_lieu[k]
            if isinstance(w, ttk.Combobox) and bang in ["DrugLeaflets", "ParsedInteractions"]:
                values.append(nhap_lieu["_drug_map"].get(w.get()))
            else:
                values.append(w.get())
        qmarks = ", ".join(["%s"] * len(values))
        cursor.execute(f"INSERT INTO {bang} ({', '.join(cols[1:])}) VALUES ({qmarks})", values[1:])
        conn.commit()
        tai_du_lieu(bang, frame)

    def update():
        cols = tree._col_order
        values = []
        for k in cols:
            w = nhap_lieu[k]
            if isinstance(w, ttk.Combobox) and bang in ["DrugLeaflets", "ParsedInteractions"]:
                values.append(nhap_lieu["_drug_map"].get(w.get()))
            else:
                values.append(w.get())
        sets = ", ".join([f"{col} = %s" for col in cols[1:]])
        cursor.execute(f"UPDATE {bang} SET {sets} WHERE {cols[0]} = %s", values[1:] + [values[0]])
        conn.commit()
        tai_du_lieu(bang, frame)

    def delete():
        cols = tree._col_order
        k = nhap_lieu[cols[0]].get()
        if not k:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn dòng để xoá")
            return
        cursor.execute(f"DELETE FROM {bang} WHERE {cols[0]} = %s", (k,))
        conn.commit()
        tai_du_lieu(bang, frame)

    def clear():
        for k, w in nhap_lieu.items():
            if isinstance(w, ttk.Combobox):
                w.set("")
            elif hasattr(w, 'config'):
                w.config(state='normal')
                w.delete(0, tk.END)
                if k.endswith('_id'):
                    w.config(state='disabled')

    tb.Button(btn_frame, text="Thêm", bootstyle="success", command=insert).pack(side=LEFT, padx=5)
    tb.Button(btn_frame, text="Cập nhật", bootstyle="warning", command=update).pack(side=LEFT, padx=5)
    tb.Button(btn_frame, text="Xoá", bootstyle="danger", command=delete).pack(side=LEFT, padx=5)
    tb.Button(btn_frame, text="Làm mới", bootstyle="info", command=clear).pack(side=LEFT, padx=5)

# --- Hàm tạo tab cho mỗi bảng ---
def tao_tab_cho_bang(bang):
    frame = tb.Frame(tabs)
    tabs.add(frame, text=bang)
    form_frame = tb.LabelFrame(frame, text="Thông tin")
    form_frame.pack(side=TOP, fill=X, padx=10, pady=5)
    btn_frame = tb.Frame(frame)
    btn_frame.pack(side=TOP, fill=X, padx=10, pady=5)
    tree = ttk.Treeview(frame, height=12)
    tree.pack(fill=BOTH, expand=True, padx=10, pady=5)
    label_hint = tb.Label(frame, text="", foreground="red")
    label_hint.pack()
    tab_frames[bang] = (form_frame, btn_frame, tree, label_hint)
    tai_du_lieu(bang, tab_frames[bang])

# --- Tạo giao diện cho tất cả bảng ---
for bang in ["Drugs", "DrugLeaflets", "ParsedInteractions"]:
    tao_tab_cho_bang(bang)

def khi_chuyen_tab(e):
    selected_tab_id = tabs.select()
    selected_tab_text = tabs.tab(selected_tab_id, "text")  # lấy tên bảng đang chọn
    if selected_tab_text in tab_frames:
        tai_du_lieu(selected_tab_text, tab_frames[selected_tab_text])

tabs.bind("<<NotebookTabChanged>>", khi_chuyen_tab)

# --- Khởi chạy giao diện ---
root.mainloop()
