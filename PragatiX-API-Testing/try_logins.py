import json, urllib.request, urllib.error

login_url = 'http://localhost:8080/api/v1/auth/login'
student_login_url = 'http://localhost:8080/api/v1/auth/student-login'

# Try common passwords for admin (username=admin)
print('=== Trying admin passwords ===')
for pwd in ['admin', 'password', '123456', 'admin123', 'admin@123', 'root', 'spdms', 'stharsan1305', 'magic', 'Admin@123', 'Admin123', 'P@ssw0rd', 'admin@spdms.com']:
    try:
        data = json.dumps({'username': 'admin', 'password': pwd}).encode('utf-8')
        req = urllib.request.Request(login_url, data=data, headers={'Content-Type': 'application/json'})
        resp = urllib.request.urlopen(req, timeout=5)
        body = resp.read().decode('utf-8')
        print(f'admin/{pwd}: {resp.status} -> {body[:200]}')
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(f'admin/{pwd}: {e.code}')
    except Exception as e:
        print(f'admin/{pwd}: error {e}')

# Try common passwords for jaga (username=jaga)
print('\n=== Trying jaga passwords ===')
for pwd in ['admin', 'password', '123456', 'jaga', 'jaga123', 'teacher', 'teacher123', 'magic', 'Jaga@123']:
    try:
        data = json.dumps({'username': 'jaga', 'password': pwd}).encode('utf-8')
        req = urllib.request.Request(login_url, data=data, headers={'Content-Type': 'application/json'})
        resp = urllib.request.urlopen(req, timeout=5)
        body = resp.read().decode('utf-8')
        print(f'jaga/{pwd}: {resp.status} -> {body[:200]}')
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(f'jaga/{pwd}: {e.code}')
    except Exception as e:
        print(f'jaga/{pwd}: error {e}')

# Try common passwords for sharu (username=sharu)
print('\n=== Trying sharu passwords ===')
for pwd in ['admin', 'password', '123456', 'sharu', 'sharu123', 'teacher', 'teacher123', 'magic', 'Sharu@123']:
    try:
        data = json.dumps({'username': 'sharu', 'password': pwd}).encode('utf-8')
        req = urllib.request.Request(login_url, data=data, headers={'Content-Type': 'application/json'})
        resp = urllib.request.urlopen(req, timeout=5)
        body = resp.read().decode('utf-8')
        print(f'sharu/{pwd}: {resp.status} -> {body[:200]}')
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(f'sharu/{pwd}: {e.code}')
    except Exception as e:
        print(f'sharu/{pwd}: error {e}')

# Check students
print('\n=== Checking students ===')
import mysql.connector
conn = mysql.connector.connect(host='localhost', port=3306, database='spdms_lab', user='root', password='stharsan1305')
cursor = conn.cursor()
cursor.execute("SELECT id, student_id, reg_no, full_name, email, active FROM students LIMIT 10")
rows = cursor.fetchall()
for r in rows:
    print(r)
cursor.close()
conn.close()