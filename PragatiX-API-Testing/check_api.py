import urllib.request, json, sys

print("Starting...", flush=True)
sys.stdout.flush()

try:
    req = urllib.request.Request('http://localhost:8080/api-docs')
    resp = urllib.request.urlopen(req, timeout=5)
    status = resp.status
    data = resp.read()
    print(f"Status: {status}", flush=True)
    print(f"Length: {len(data)}", flush=True)
    spec = json.loads(data)
    paths = list(spec.get('paths', {}).keys())
    print(f"Paths: {len(paths)}", flush=True)
    for p in paths[:5]:
        print(f"  {p}", flush=True)
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)[:200]}", flush=True)
