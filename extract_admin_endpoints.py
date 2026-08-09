import os, re

root = r'N:\pragatiX\Backend'
results = []

for r, d, files in os.walk(root):
    for f in files:
        if f.endswith('.java') and not 'target' in r and not 'PragatiX-Security-HTML' in r:
            path = os.path.join(r, f)
            try:
                content = open(path, encoding='utf-8', errors='ignore').read()
            except:
                continue
            if '@RestController' in content or '@Controller' in content:
                base_path = ''
                base_match = re.search(r'@RequestMapping\s*\(\s*(?:value\s*=\s*|path\s*=\s*)?["\']([^"\']+)["\']', content)
                if base_match:
                    base_path = base_match.group(1)
                
                # Split by methods to check @PreAuthorize per method
                lines = content.split('\n')
                current_preauth = ''
                for i, line in enumerate(lines):
                    if '@PreAuthorize' in line:
                        current_preauth = line
                    method_match = re.search(r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)\s*(?:\(\s*(?:value\s*=\s*|path\s*=\s*)?["\']([^"\']*)["\']\s*\))?', line)
                    if method_match:
                        http_verb = method_match.group(1)
                        sub = method_match.group(2) or ''
                        http_method = http_verb.replace('Mapping', '').upper()
                        full_path = (base_path + '/' + sub).replace('//', '/').rstrip('/')
                        if not full_path:
                            full_path = base_path or '/'
                        
                        is_admin = ('admin' in full_path.lower() or 'admin' in f.lower() or 'modules\\admin' in path.lower() 
                                    or 'superadmin' in full_path.lower() or 'ADMIN' in current_preauth)
                        
                        if is_admin:
                            results.append((http_method, full_path, f, current_preauth.strip()))
                        current_preauth = ''

print(f"Total Admin REST Endpoints: {len(results)}\n")

grouped = {}
for m, p, f, auth in sorted(results, key=lambda x: (x[2], x[1])):
    grouped.setdefault(f, []).append((m, p, auth))

for controller, eps in grouped.items():
    print(f"### {controller}")
    for m, p, auth in eps:
        auth_str = f" [{auth}]" if auth else ""
        print(f"  {m:7s} {p}{auth_str}")
    print()
