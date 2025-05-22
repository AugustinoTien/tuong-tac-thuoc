import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# --- Kết nối CSDL ---
conn = sqlite3.connect("drug_interaction.db")
cursor = conn.cursor()

# --- Tạo các bảng nếu chưa có ---
cursor.executescript("""
CREATE TABLE IF NOT EXISTS Drugs (
    drug_id INTEGER PRIMARY KEY AUTOINCREMENT,
    drug_name TEXT NOT NULL,
    generic_name TEXT,
    drug_class TEXT,
    manufacturer TEXT
);

CREATE TABLE IF NOT EXISTS DrugLeaflets (
    leaflet_id INTEGER PRIMARY KEY AUTOINCREMENT,
    drug_id INTEGER,
    active_ingredient TEXT,
    indication TEXT,
    dosage TEXT,
    administration TEXT,
    contraindications TEXT,
    precautions TEXT,
    side_effects TEXT,
    interaction_text TEXT,
    storage TEXT,
    warnings TEXT,
    FOREIGN KEY (drug_id) REFERENCES Drugs(drug_id)
);

CREATE TABLE IF NOT EXISTS ParsedInteractions (
    interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_drug_id INTEGER,
    target_drug_id INTEGER,
    interaction_level TEXT,
    evidence_text TEXT,
    FOREIGN KEY (source_drug_id) REFERENCES Drugs(drug_id),
    FOREIGN KEY (target_drug_id) REFERENCES Drugs(drug_id)
);
""")
conn.commit()

# --- Giao diện chính ---
root = tk.Tk()
root.title("Quản lý tương tác thuốc")
root.geometry("1100x650")

bang_hien_tai = tk.StringVar(value="Drugs")
nhap_lieu = {}

# --- Nhãn tiếng Việt cho từng bảng ---
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

# Các hàm xử lý vẫn giữ nguyên...

# Gọi lại tai_du_lieu() để cập nhật thay đổi

tai_du_lieu()
root.mainloop()
