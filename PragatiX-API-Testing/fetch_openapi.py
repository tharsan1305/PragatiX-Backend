import urllib.request, json

req = urllib.request.Request('http://localhost:8080/api-docs')
resp = urllib.request.urlopen(req, timeout=10)
spec = json.loads(resp.read())
with open('openapi.json', 'w') as f:
    json.dump(spec, f, indent=2)
print('Saved openapi.json:', len(json.dumps(spec)), 'chars')

# Find auth-related paths
for path, methods in spec.get('paths', {}).items():
    if 'auth' in path.lower() or 'login' in path.lower():
        print(f"AUTH PATH: {path} -> {list(methods.keys())}")
        for method, details in methods.items():
            if 'requestBody' in details:
                print(f"  {method} body:", json.dumps(details['requestBody'], indent=2)[:500])
