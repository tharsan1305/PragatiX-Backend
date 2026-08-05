# Information Disclosure Findings

## HTTP 500 Errors (Potential Stack Trace Leakage)

The following endpoints return HTTP 500 Internal Server Error responses, which may leak stack traces, database queries, or other internal server details.

### Affected Endpoints

- **GET /api/student/attendance/history** - `Authenticated Access` - Status: 500
- **GET /api/student/attendance/summary** - `Authenticated Access` - Status: 500
- **POST /api/v1/attendance-engine/run-both** - `Authenticated Access` - Status: 500
- **POST /api/v1/attendance-engine/run-daily** - `Authenticated Access` - Status: 500
- **GET /api/v1/badges/student/me** - `Authenticated Access` - Status: 500
- **GET /api/v1/cc/dashboard/stats** - `Authenticated Access` - Status: 500
- **GET /api/v1/levels/me/current** - `Authenticated Access` - Status: 500
- **POST /api/v1/students/bulk-parse** - `Authenticated Access` - Status: 500
- **GET /api/v1/teams/my-team** - `Authenticated Access` - Status: 500

## Impact

HTTP 500 errors with detailed error messages can reveal:
- Database schema information
- File paths on the server
- Stack traces exposing code structure
- Internal error messages that aid attackers

## Remediation

1. Configure the application to return generic error messages in production
2. Implement global exception handlers that return consistent error responses
3. Log detailed errors server-side but return minimal information to clients
4. Disable stack trace display in production environments
5. Add proper input validation to prevent the errors from occurring

## Summary

- **Total 500 errors found:** 12
- **Unique endpoints affected:** 9
