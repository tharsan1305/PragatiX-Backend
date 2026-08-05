import json

with open('openapi.json') as f:
    spec = json.load(f)

schemas = spec.get('components', {}).get('schemas', {})
for name in ['LoginRequest', 'StudentLoginRequest', 'AuthResponse', 'JwtResponse', 'User']:
    if name in schemas:
        print(f'=== {name} ===')
        print(json.dumps(schemas[name], indent=2)[:800])
        print()

# Find all auth paths
print('=== AUTH PATHS ===')
for path, methods in spec.get('paths', {}).items():
    if 'auth' in path.lower() or 'login' in path.lower() or 'me' == path.split('/')[-1]:
        print(f'{path}: {list(methods.keys())}')

# Find all paths with {id} or {regNo} for IDOR testing
print('\n=== IDOR-CANDIDATE PATHS ===')
idor_paths = []
for path, methods in spec.get('paths', {}).items():
    if '{id}' in path or '{regNo}' in path or '{studentId}' in path:
        for method in methods.keys():
            if method in ['get', 'put', 'delete', 'patch']:
                idor_paths.append((method, path))
for m, p in idor_paths[:30]:
    print(f'{m.upper()} {p}')
