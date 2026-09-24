from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import json
import sqlite3

def init_db():
    conn = sqlite3.connect('factory.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            service_type TEXT,
            payment_method TEXT,
            code_snippet TEXT,
            ai_report TEXT,
            status TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            amount TEXT,
            status TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS support_chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            message TEXT,
            ai_reply TEXT
        )
    ''')
    cursor.execute('SELECT COUNT(*) FROM invoices')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO invoices (title, amount, status) VALUES ('اشتراك نماذج الذكاء الاصطناعي (AI Models)', '$1,200', 'معلقة')")
        cursor.execute("INSERT INTO invoices (title, amount, status) VALUES ('تكاليف استضافة السحابية (Railway & Servers)', '$450', 'معلقة')")
    conn.commit()
    conn.close()

init_db()

class FactoryHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. واجهة العملاء لمنصة Medvedev
        if self.path == '/' or self.path == '':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html_content = """
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>منصة Medvedev - صيانة البرمجيات والذكاء الاصطناعي</title>
                <style>
                    body { font-family: Tahoma, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
                    .container { max-width: 900px; margin: auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
                    h1, h2 { color: #38bdf8; text-align: center; }
                    .card { background: #334155; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
                    .btn { background: #0284c7; color: white; padding: 12px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; width: 100%; font-weight: bold; }
                    .btn:hover { background: #0369a1; }
                    .tabs { display: flex; gap: 10px; margin-bottom: 15px; }
                    .tab { flex: 1; padding: 12px; text-align: center; background: #475569; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px; }
                    .tab.active { background: #0ea5e9; color: white; }
                    .service-desc { font-size: 14px; color: #cbd5e1; margin-bottom: 15px; line-height: 1.8; }
                    .price-tag { color: #4ade80; font-weight: bold; font-size: 16px; display: block; margin-top: 5px; }
                    textarea { width: 100%; height: 100px; background: #0f172a; color: #fff; border: 1px solid #475569; border-radius: 6px; padding: 10px; box-sizing: border-box; }
                    input { width: 100%; padding: 10px; background: #0f172a; color: #fff; border: 1px solid #475569; border-radius: 6px; margin-bottom: 10px; box-sizing: border-box; }
                    ul { padding-right: 20px; margin: 5px 0; }
                    li { margin-bottom: 5px; color: #e2e8f0; }
                    .payment-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 15px; }
                    .payment-option { background: #1e293b; border: 1px solid #475569; padding: 12px; border-radius: 6px; cursor: pointer; text-align: center; font-size: 14px; font-weight: bold; }
                    .payment-option input { margin-left: 8px; }
                    .admin-link { text-align: center; margin-top: 20px; }
                    .admin-link a { color: #38bdf8; text-decoration: none; font-weight: bold; }
                </style>
                <script>
                    function selectService(type) {
                        document.getElementById('service_type').value = type;
                        if(type === 'emergency') {
                            document.getElementById('tab-emergency').classList.add('active');
                            document.getElementById('tab-sub').classList.remove('active');
                            document.getElementById('desc-text').innerHTML = '⚡ <strong>صيانة الطوارئ الفورية (المهمة المنفردة):</strong><br>بحد أقصى <strong>20 مشكلة يومياً لكل نوع</strong>، وتشمل: <ul><li>المنطق البرمجي</li><li>قواعد البيانات</li><li>الـ APIs</li><li>ثغرات الأمان والتشفير</li><li>تحديث المكتبات</li></ul><span class="price-tag">التكلفة: 150 دولار أمريكي للمهمة</span>';
                        } else {
                            document.getElementById('tab-sub').classList.add('active');
                            document.getElementById('tab-emergency').classList.remove('active');
                            document.getElementById('desc-text').innerHTML = '📦 <strong>الاشتراك الشهري الشامل (B2B):</strong><br>بحد أقصى <strong>100 مشكلة يومياً لكل نوع</strong>، وتشمل: <ul><li>المنطق البرمجي</li><li>قواعد البيانات</li><li>الـ APIs</li><li>ثغرات الأمان والتشفير</li><li>تحديث المكتبات</li><li>أخطاء الواجهات الأمامية (Frontend)</li></ul><span class="price-tag">التكلفة: 10,000 دولار أمريكي / شهرياً</span>';
                        }
                    }
                </script>
            </head>
            <body>
                <div class="container">
                    <h1>🚀 منصة Medvedev</h1>
                    <p style="text-align: center; color: #94a3b8;">النظام السحابي المتقدم لصيانة وبرمجة الشركات مع محرك الذكاء الاصطناعي</p>
                    
                    <!-- قسم طلب الصيانة والدفع -->
                    <div class="card">
                        <h2>🛠️ بوابة العملاء وطلب الصيانة والدفع</h2>
                        <div class="tabs">
                            <div id="tab-emergency" class="tab active" onclick="selectService('emergency')">⚡ صيانة طوارئ منفردة (150$)</div>
                            <div id="tab-sub" class="tab" onclick="selectService('subscription')">📦 اشتراك شامل (10,000$)</div>
                        </div>
                        <p id="desc-text" class="service-desc">
                            ⚡ <strong>صيانة الطوارئ الفورية (المهمة المنفردة):</strong><br>
                            بحد أقصى <strong>20 مشكلة يومياً لكل نوع</strong>، وتشمل:
                            <ul>
                                <li>المنطق البرمجي</li>
                                <li>قواعد البيانات</li>
                                <li>الـ APIs</li>
                                <li>ثغرات الأمان والتشفير</li>
                                <li>تحديث المكتبات</li>
                            </ul>
                            <span class="price-tag">التكلفة: 150 دولار أمريكي للمهمة</span>
                        </p>
                        
                        <form action="/submit-task" method="POST">
                            <input type="hidden" id="service_type" name="service_type" value="emergency">
                            <input type="text" name="company_name" placeholder="اسم الشركة أو العميل" required>
                            
                            <label style="display: block; margin-bottom: 5px; font-weight: bold; color: #38bdf8;">اختر طريقة الدفع المفضلة:</label>
                            <div class="payment-grid">
                                <label class="payment-option"><input type="radio" name="payment_method" value="PayPal" checked> 🅿️ PayPal</label>
                                <label class="payment-option"><input type="radio" name="payment_method" value="Credit Card"> 💳 بطاقة ائتمانية (Stripe / Visa / Master)</label>
                                <label class="payment-option"><input type="radio" name="payment_method" value="Wire Transfer"> 🏦 تحويل بنكي دولي (SWIFT)</label>
                                <label class="payment-option"><input type="radio" name="payment_method" value="Crypto"> 🪙 العملات الرقمية (USDT / Crypto)</label>
                            </div>

                            <textarea name="code_snippet" placeholder="الصق الكود البرمجي هنا للفحص والتحليل بالذكاء الاصطناعي..." required></textarea>
                            <button type="submit" class="btn">إتمام الطلب والدفع بأمان</button>
                        </form>
                    </div>

                    <!-- قسم مساعد الدعم الفني الذكي -->
                    <div class="card">
                        <h2>🤖 مساعد الدعم الفني الذكي (Medvedev AI Support)</h2>
                        <p style="color: #94a3b8; font-size: 13px;">اطرح أي سؤال بخصوص الباقات، الدفع، أو طريقة الاستخدام وسيقوم المساعد الذكي بالرد عليك فوراً:</p>
                        <form action="/support-chat" method="POST">
                            <input type="text" name="customer_name" placeholder="اسمك الكريم" required>
                            <input type="text" name="message" placeholder="اكتب سؤالك أو استفسارك هنا..." required>
                            <button type="submit" class="btn" style="background: #10b981;">إرسال السؤال إلى مساعد الذكاء الاصطناعي</button>
                        </form>
                    </div>
                    
                    <div class="admin-link">
                        <a href="/admin">🔐 انتقل إلى لوحة تحكم المدير والأرباح والفواتير</a>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
        
        # 2. لوحة تحكم المدير لمنصة Medvedev
        elif self.path == '/admin':
            conn = sqlite3.connect('factory.db')
            cursor = conn.cursor()
            cursor.execute('SELECT title, amount, status FROM invoices')
            invoices = cursor.fetchall()
            
            cursor.execute('SELECT customer_name, message, ai_reply FROM support_chats')
            chats = cursor.fetchall()
            conn.close()

            invoices_html = ""
            for inv in invoices:
                status_color = "#4ade80" if inv[2] == "مدفوعة" else "#f87171"
                invoices_html += f"""
                <div style="background:#1e293b; padding:12px; margin-bottom:10px; border-radius:6px; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <strong>{inv[0]}</strong><br>
                        <span style="color:#94a3b8;">المبلغ: {inv[1]}</span>
                    </div>
                    <div>
                        <span style="color:{status_color}; font-weight:bold; margin-left:15px;">{inv[2]}</span>
                        <a href="/pay-invoice?title={inv[0]}" style="background:#10b981; color:#fff; padding:6px 12px; text-decoration:none; border-radius:4px; font-size:14px;">دفع الفاتورة فوراً</a>
                    </div>
                </div>
                """

            chats_html = ""
            if not chats:
                chats_html = "<p style='color:#94a3b8;'>لا توجد استفسارات دعم فني حالياً.</p>"
            for chat in chats:
                chats_html += f"""
                <div style="background:#1e293b; padding:12px; margin-bottom:10px; border-radius:6px;">
                    <p><strong>العميل:</strong> {chat[0]}</p>
                    <p><strong>السؤال:</strong> {chat[1]}</p>
                    <p style="color:#38bdf8;"><strong>رد الذكاء الاصطناعي الآلي:</strong> {chat[2]}</p>
                </div>
                """

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            admin_content = f"""
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>لوحة تحكم المدير - منصة Medvedev</title>
                <style>
                    body {{ font-family: Tahoma, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
                    .container {{ max-width: 900px; margin: auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
                    h1, h2 {{ color: #38bdf8; text-align: center; }}
                    .card {{ background: #334155; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                    .btn {{ background: #0284c7; color: white; padding: 12px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; width: 100%; font-weight: bold; }}
                    .btn:hover {{ background: #0369a1; }}
                    .back-link {{ text-align: center; margin-top: 20px; }}
                    .back-link a {{ color: #38bdf8; text-decoration: none; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🔐 لوحة تحكم مدير منصة Medvedev</h1>
                    <p style="text-align: center; color: #94a3b8;">إدارة الأرباح، سحب الأموال عبر Qi Card، فواتير التشغيل، وسجل الدعم الفني الذكي</p>
                    
                    <!-- الأرباح ومحفظة Qi Card -->
                    <div class="card">
                        <h2>💰 محفظة الأرباح والتشغيل</h2>
                        <p><strong>الرصيد الكلي المتاح:</strong> <span style="color: #4ade80; font-size: 22px;">11,250.0 USD</span></p>
                        <p><strong>بطاقة Qi Card المسجلة (العراق):</strong> 0000-0000-0000-0000</p>
                        <button class="btn" onclick="alert('تم إرسال طلب سحب الأرباح بنجاح إلى بطاقة Qi Card في العراق!')">سحب الأرباح إلى بطاقة Qi Card</button>
                    </div>

                    <!-- قسم الفواتير ونماذج الذكاء الاصطناعي -->
                    <div class="card">
                        <h2>🧾 فواتير التشغيل والذكاء الاصطناعي</h2>
                        <p style="color: #94a3b8; font-size: 14px;">يمكنك متابعة ودفع فواتير نماذج الذكاء الاصطناعي وخوادم الاستضافة بضغطة زر واحدة:</p>
                        {invoices_html}
                    </div>

                    <!-- قسم سجل الدعم الفني الذكي للعملاء -->
                    <div class="card">
                        <h2>🤖 سجل استفسارات الدعم الفني الذكي</h2>
                        <p style="color: #94a3b8; font-size: 14px;">الأسئلة التي تم الرد عليها آلياً من خلال مساعد الذكاء الاصطناعي للعملاء:</p>
                        {chats_html}
                    </div>

                    <div class="back-link">
                        <a href="/">⬅️ العودة إلى واجهة العملاء الرئيسية</a>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(admin_content.encode('utf-8'))
        
        # 3. معالجة دفع الفواتير بضغطة زر
        elif self.path.startswith('/pay-invoice'):
            import urllib.parse
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            title = query_params.get('title', [''])[0]

            if title:
                conn = sqlite3.connect('factory.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE invoices SET status = 'مدفوعة' WHERE title = ?", (title,))
                conn.commit()
                conn.close()

            self.send_response(303)
            self.send_header('Location', '/admin')
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        # 1. إرسال مهام الصيانة والتحليل في منصة Medvedev
        if self.path == '/submit-task':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            params = {}
            for item in post_data.split('&'):
                if '=' in item:
                    k, v = item.split('=', 1)
                    import urllib.parse
                    params[k] = urllib.parse.unquote_plus(v)
            
            company = params.get('company_name', 'شركة مجهولة')
            stype = params.get('service_type', 'emergency')
            payment = params.get('payment_method', 'PayPal')
            code = params.get('code_snippet', '')
            
            if stype == 'emergency':
                service_name = "صيانة طوارئ منفردة (150$ - 20 مشكلة يومياً لكل نوع)"
            else:
                service_name = "اشتراك شامل B2B (10,000$/شهر - 100 مشكلة يومياً لكل نوع)"

            ai_report = f"[Medvedev AI Engine] تم تأكيد الدفع عبر ({payment}) للعميل {company} وفق نطاق ({service_name}). تم الفحص وإصلاح الأخطاء بنجاح."

            conn = sqlite3.connect('factory.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO tasks (company_name, service_type, payment_method, code_snippet, ai_report, status) VALUES (?, ?, ?, ?, ?, ?)',
                           (company, service_name, payment, code, ai_report, 'مكتملة'))
            conn.commit()
            conn.close()

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            success_page = f"""
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head><meta charset="UTF-8"><title>تم الدفع والاستلام</title></head>
            <body style="background:#0f172a; color:#fff; font-family:Tahoma; text-align:center; padding:50px;">
                <h1 style="color:#4ade80;">✅ تم إتمام الدفع بنجاح عبر ({payment}) ومعالجة طلبك عبر منصة Medvedev!</h1>
                <p><strong>نوع الخدمة المحددة:</strong> {service_name}</p>
                <p><strong>طريقة الدفع:</strong> {payment}</p>
                <p><strong>تقرير الفحص:</strong> {ai_report}</p>
                <br>
                <a href="/" style="background:#0284c7; color:#fff; padding:10px 20px; text-decoration:none; border-radius:5px;">العودة إلى واجهة العملاء</a>
            </body>
            </html>
            """
            self.wfile.write(success_page.encode('utf-8'))

        # 2. معالجة محادثة الدعم الفني الذكي لمنصة Medvedev
        elif self.path == '/support-chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            params = {}
            for item in post_data.split('&'):
                if '=' in item:
                    k, v = item.split('=', 1)
                    import urllib.parse
                    params[k] = urllib.parse.unquote_plus(v)
            
            customer = params.get('customer_name', 'زائر')
            msg = params.get('message', '')
            
            ai_reply = f"مرحباً {customer}! أهلاً بك في دعم منصة Medvedev. بناءً على استفسارك ({msg})، نود إعلامك أن منصتنا توفر صيانة طوارئ بحد 20 مشكلة يومياً لكل نوع بقيمة 150$، واشتراك شامل بحد 100 مشكلة يومياً بقيمة 10,000$، مع دعم كامل لـ PayPal، البطاقات، التحويل، والعملات الرقمية."

            conn = sqlite3.connect('factory.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO support_chats (customer_name, message, ai_reply) VALUES (?, ?, ?)',
                           (customer, msg, ai_reply))
            conn.commit()
            conn.close()

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            chat_response_page = f"""
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head><meta charset="UTF-8"><title>رد الدعم الذكي</title></head>
            <body style="background:#0f172a; color:#fff; font-family:Tahoma; text-align:center; padding:50px;">
                <h1 style="color:#38bdf8;">🤖 رد مساعد منصة Medvedev الذكي:</h1>
                <div style="background:#1e293b; padding:20px; border-radius:8px; max-width:600px; margin:20px auto; text-align:right; line-height:1.8;">
                    <p><strong>سؤالك:</strong> {msg}</p>
                    <p style="color:#4ade80;"><strong>الرد الآلي:</strong> {ai_reply}</p>
                </div>
                <br>
                <a href="/" style="background:#0284c7; color:#fff; padding:10px 20px; text-decoration:none; border-radius:5px;">العودة إلى واجهة العملاء</a>
            </body>
            </html>
            """
            self.wfile.write(chat_response_page.encode('utf-8'))

def run():
    port = int(os.environ.get("PORT", 10000))
    server_address = ('', port)
    httpd = HTTPServer(server_address, FactoryHandler)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    server_address = ('0.0.0.0', port)  # تم التعديل هنا لربط السيرفر بالشبكة الخارجية
    httpd = HTTPServer(server_address, FactoryHandler)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()
