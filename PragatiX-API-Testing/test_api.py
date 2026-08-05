import urllib.request, json, sys

def api_call(method, url, body=None, headers=None):
    try:
        data = json.dumps(body).encode('utf-8') if body else None
        req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
        resp = urllib.request.urlopen(req, timeout=5)
        return resp.status, resp.read().decode('utf-8', errors='replace')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='replace')
    except Exception as e:
        return None, str(e)

print("Testing login endpoints...", flush=True)
for creds in [
    {'username': 'admin', 'password': 'admin'},
    {'username': 'admin', 'password': 'password'},
    {'username': 'test', 'password': 'test'},
    {'username': 'teacher', 'password': 'teacher'},
    {'username': 'student', 'password': 'student'},
    {'username': 'root', 'password': 'root'},
]:
    status, body = api_call('POST', 'http://localhost:8080/api/v1/auth/login', creds, {'Content-Type': 'application/json'})
    print(f"  {creds['username']}/{creds['password']}: {status}", flush=True)
    if status == 200:
        try:
            j = json.loads(body)
            print(f"    -> token: {str(j)[:200]}", flush=True)
        except:
            pass

print("Testing student login...", flush=True)
for creds in [
    {'username': 'student', 'password': 'student'},
    {'username': 'student1', 'password': 'student1'},
    {'username': 'test', 'password': 'test'},
]:
    status, body = api_call('POST', 'http://localhost:8080/api/v1/auth/student-login', creds, {'Content-Type': 'application/json'})
    print(f"  {creds['username']}/{creds['password']}: {status}", flush=True)
    if status == 200:
        try:
            j = json.loads(body)
            print(f"    -> token: {str(j)[:200]}", flush=True)
        except:
            pass
