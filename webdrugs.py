from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# --- Kết nối CSDL MySQL ---
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="drug_interaction"
)
cursor = conn.cursor(dictionary=True)

# --- Tên tiếng Việt ---
nhan_viet_hoa = {
    "Drugs": ["Mã thuốc", "Tên thuốc", "Hoạt chất", "Nhóm thuốc", "Hãng sản xuất"],
    "DrugLeaflets": ["Mã tờ hướng dẫn", "Thuốc", "Hoạt chất chính", "Chỉ định", "Liều dùng", "Cách dùng", "Chống chỉ định", "Thận trọng", "Tác dụng phụ", "Tương tác", "Bảo quản", "Cảnh báo"],
    "ParsedInteractions": ["Mã tương tác", "Thuốc A", "Thuốc B", "Mức độ", "Chi tiết"]
}

# --- Trang chủ chuyển hướng đến bảng Drugs ---
@app.route('/')
def index():
    return redirect(url_for('view_table', table='Drugs'))

# --- Hiển thị bảng dữ liệu ---
@app.route('/<table>')
def view_table(table):
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    cursor.execute("SHOW COLUMNS FROM " + table)
    cols = [col['Field'] for col in cursor.fetchall()]
    display_names = nhan_viet_hoa.get(table, cols)

    # Lấy danh sách thuốc nếu cần dropdown
    drug_options = []
    if table in ["DrugLeaflets", "ParsedInteractions"]:
        cursor.execute("SELECT drug_id, drug_name FROM Drugs")
        drug_options = cursor.fetchall()

    return render_template("table.html", table=table, rows=rows, cols=cols, labels=display_names, drug_options=drug_options)

# --- Thêm hoặc cập nhật dữ liệu ---
@app.route('/submit/<table>', methods=['POST'])
def submit(table):
    data = request.form.to_dict()
    id_key = list(data.keys())[0]
    id_val = data[id_key]

    if id_val:
        sets = ", ".join([f"{k}=%s" for k in data.keys() if k != id_key])
        values = [data[k] for k in data.keys() if k != id_key] + [id_val]
        query = f"UPDATE {table} SET {sets} WHERE {id_key}=%s"
    else:
        cols = ", ".join(data.keys()[1:])
        qmarks = ", ".join(["%s"] * (len(data) - 1))
        values = [data[k] for k in list(data.keys())[1:]]
        query = f"INSERT INTO {table} ({cols}) VALUES ({qmarks})"

    cursor.execute(query, values)
    conn.commit()
    return redirect(url_for('view_table', table=table))

# --- Xoá dòng ---
@app.route('/delete/<table>/<id>')
def delete(table, id):
    cursor.execute(f"DELETE FROM {table} WHERE {table.lower().rstrip('s')}_id = %s", (id,))
    conn.commit()
    return redirect(url_for('view_table', table=table))

if __name__ == '__main__':
    app.run(debug=True)
