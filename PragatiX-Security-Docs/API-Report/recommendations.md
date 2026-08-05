# Security Recommendations

## Critical Priority

### 1. Fix IDOR in Student Discipline Logs
**Endpoint:** `GET /api/v1/students/{id}/discipline-logs`

The endpoint returns discipline logs for any student ID without verifying that the requesting user has access to that student's data.

**Fix:**
- Add authorization check to verify the requesting user (teacher/admin) is associated with the student
- Return 403 for unauthorized access attempts
- Return 404 for non-existent student IDs

### 2. Add Input Validation to Endpoints Accepting Empty Bodies
**Endpoints:**
- `POST /api/v1/admin/stages/evaluate-promotions`
- `POST /api/v1/attendance-engine/reset`
- `POST /api/v1/attendance-engine/run-weekly`

These endpoints accept empty request bodies and process them as valid requests.

**Fix:**
- Add `@Valid` annotations to request DTOs
- Require all mandatory fields in request bodies
- Return 400 Bad Request for missing or invalid input

### 3. Fix 500 Errors on Invalid Input
**Endpoints:**
- `POST /api/v1/attendance-engine/run-both`
- `POST /api/v1/attendance-engine/run-daily`
- `POST /api/v1/students/bulk-parse`

These endpoints crash with 500 errors instead of returning proper 400 validation errors.

**Fix:**
- Add proper input validation before processing
- Implement global exception handler to return consistent error responses
- Never let unhandled exceptions reach the client

## High Priority

### 4. Prevent Information Disclosure via 500 Errors
Configure the application to return generic error messages in production instead of detailed stack traces.

### 5. Remove Token from /auth/me Response
The `/api/v1/auth/me` endpoint returns the JWT token in the response body. While the client already has this token, returning it in API responses can be a concern if responses are logged or cached.

## Medium Priority

### 6. Implement Mass Assignment Protection
Use DTOs with explicit field allowlists instead of binding request bodies directly to domain entities.

### 7. Add Rate Limiting
Implement rate limiting on authentication endpoints (`/api/v1/auth/login`, `/api/v1/auth/student-login`) to prevent brute-force attacks.

### 8. Add Account Lockout
Implement account lockout after repeated failed login attempts (e.g., 5 failed attempts = 15 minute lockout).

## Low Priority

### 9. Security Headers
Add security headers to all responses:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`

### 10. CORS Configuration
Review and restrict CORS configuration to only allow trusted origins.

### 11. API Versioning
Ensure API versioning is properly implemented to prevent version confusion attacks.

### 12. Request Size Limits
Configure maximum request body sizes to prevent denial-of-service attacks via oversized payloads.
