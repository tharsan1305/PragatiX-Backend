# Mass Assignment Findings

## Endpoints Accepting Empty Bodies

The following endpoints accept POST/PUT requests with empty bodies and return 200, which may indicate mass assignment vulnerabilities where an attacker could set arbitrary fields.

### Affected Endpoints

- **POST /api/v1/admin/stages/evaluate-promotions** - `Empty Body Input Validation` - Status: 200
- **POST /api/v1/attendance-engine/reset** - `Empty Body Input Validation` - Status: 200
- **POST /api/v1/attendance-engine/run-weekly** - `Empty Body Input Validation` - Status: 200

## Impact

Mass assignment vulnerabilities allow attackers to:
- Set arbitrary fields on objects (e.g., `isAdmin`, `role`)
- Override intended field values
- Create unauthorized records with elevated privileges

## Remediation

1. Use DTOs (Data Transfer Objects) with explicit field allowlists
2. Implement strict input validation for all request bodies
3. Use framework-level protections against mass assignment (e.g., `@JsonIgnore` in Jackson)
4. Never bind request bodies directly to domain entities
5. Require all mandatory fields and validate their types and values

## Summary

- **Total mass assignment tests:** 3
- **All endpoints should validate input bodies before processing**
