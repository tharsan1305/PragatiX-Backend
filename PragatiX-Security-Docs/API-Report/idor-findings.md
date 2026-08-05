# IDOR Findings

## Insecure Direct Object Reference Vulnerabilities

### Finding 1: GET /api/v1/students/{id}/discipline-logs

- **Severity:** Critical
- **Status Code:** 200 (should be 403/404)
- **Description:** The endpoint returns discipline logs for any student ID, including non-existent IDs. This allows an attacker to enumerate student IDs and access discipline records they should not have access to.
- **Impact:** Unauthorized access to other students' discipline records, potentially violating FERPA/privacy regulations.
- **Remediation:** Implement proper authorization checks to verify the requesting user has access to the specified student's data. Return 403 for unauthorized access and 404 for non-existent resources.

## Test Results

| Endpoint | Status Code | Expected | Result |
|----------|-------------|----------|--------|
| GET /api/v1/students/{id}/discipline-logs | 200 | 403/404 | VULNERABLE |
| GET /api/v1/admin/activities/{id}/assignments | 404 | 403/404 | OK |
| GET /api/v1/admin/departments/{id}/sections | 404 | 403/404 | OK |
| GET /api/v1/admin/stages/{id} | 404 | 403/404 | OK |
| GET /api/v1/admin/stages/{id}/report | 404 | 403/404 | OK |
| GET /api/v1/students/{id} | 404 | 403/404 | OK |
| GET /api/v1/teams/{id} | 404 | 403/404 | OK |

## Summary

- **Total IDOR tests:** 7
- **Vulnerable:** 1
- **Properly blocked:** 6
