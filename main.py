from http.server import HTTPServer, BaseHTTPRequestHandler
import sqlite3
import urllib.parse

def init_db():
    conn = sqlite3.connect('factory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, client TEXT, service TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS wallet
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, balance REAL, qicard TEXT)''')
    c.execute("SELECT COUNT(*) FROM wallet")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO wallet (balance, qicard) VALUES (150000.0, 'غير متصل')")
    conn.commit()
    conn.close()

init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>مصنع صيانة البرمجيات - العراق</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; color: #333; }
        .container { max-width: 800px; margin: auto; background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        h1, h2 { color: #0056b3; text-align: center; }
        .card { background: #eef2f7; padding: 15px; margin-bottom: 20px; border-radius: 8px; border-right: 5px solid #0056b3; }
        input, select, button { width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        button { background-color: #0056b3; color: white; font-weight: bold; cursor: pointer; }
        button:hover { background-color: #004494; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: center; }
        th { background-color: #0056b3; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>مصنع صيانة البرمجيات B2B</h1>
        <p style="text-align: center;">منصة إدارة وصيانة الأنظمة والخدمات السحابية في العراق</p>

        <div class="card">
            <h2>المحفظة السحابية والرصيد</h2>
            <p><strong>الرصيد الحالي:</strong> {balance} د.ع</p>
            <p><strong>رقم بطاقة Qi Card الحالية:</strong> {qicard}</p>
            <form method="POST" action="/update_qicard">
                <label>تحديث معلومات Qi Card (للسحب اليدوي):</label>
                <input type="text" name="qicard" placeholder="أدخل رقم بطاقة Qi Card أو الاسم" required>
                <button type="submit">حفظ بيانات السحب</button>
            </form>
        </div>

        <div class="card">
            <h2>إضافة طلب صيانة جديد (Task Queue)</h2>
            <form method="POST" action="/add_task">
                <label>اسم الشركة / العميل:</label>
                <input type="text" name="client" placeholder="مثال: شركة التقنية العراقية" required>
                <label>نوع الصيانة المطلوبة:</label>
                <input type="text" name="service" placeholder="مثال: تحديث قاعدة بيانات / إصلاح ثغرة" required>
                <button type="submit">إضافة إلى طابور المهام</button>
            </form>
        </div>

        <h2>قائمة المهام النشطة</h2>
        <table>
            <tr>
                <th>رقم الطلب</th>
                <th>اسم العميل</th>
                <th>نوع الخدمة</th>
                <th>الحالة</th>
            </tr>
            {tasks_rows}
        </table>
    </div>
</body>
</html>
"""

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            conn = sqlite3.connect('factory.db')
            c = conn.cursor()
            c.execute("SELECT balance, qicard FROM wallet WHERE id=1")
            wallet = c.fetchone()
            balance = wallet[0] if wallet else 0.0
            qicard = wallet[1] if wallet else "غير متصل"

            c.execute("SELECT id, client, service, status FROM tasks")
            tasks = c.fetchall()
            conn.close()

            tasks_rows = ""
            for t in tasks:
                tasks_rows += f"<tr><td>{t[0]}</td><td>{t[1]}</td><td>{t[2]}</td><td>{t[3]}</td></tr>"

            html = HTML_TEMPLATE.format(balance=balance, qicard=qicard, tasks_rows=tasks_rows)
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = urllib.parse.parse_qs(post_data)

        conn = sqlite3.connect('factory.db')
        c = conn.cursor()

        if self.path == '/add_task':
            client = params.get('client', [''])[0]
            service = params.get('service', [''])[0]
            if client and service:
                c.execute("INSERT INTO tasks (client, service, status) VALUES (?, ?, ?)", (client, service, 'قيد الانتظار'))
                conn.commit()
        elif self.path == '/update_qicard':
            qicard = params.get('qicard', [''])[0]
            if qicard:
                c.execute("UPDATE wallet SET qicard = ? WHERE id = 1", (qicard,))
                conn.commit()

        conn.close()
        self.send_response(303)
        self.send_header('Location', '/')
        self.end_headers()

def run():
    server_address = ('0.0.0.0', 8080)
    httpd = HTTPServer(server_address, SimpleHandler)
    print("السيرفر يعمل الآن على المنفذ 8080...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0",
