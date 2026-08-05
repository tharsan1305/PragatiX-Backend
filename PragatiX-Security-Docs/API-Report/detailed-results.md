# Detailed Test Results

## All Test Results by Endpoint

| Endpoint | Test | Status Code | Result | Details |
|----------|------|-------------|--------|---------|
| DELETE /api/v1/academic-calendar/alternate-working-days/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| DELETE /api/v1/academic-calendar/alternate-working-days/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/academic-calendar/alternate-working-days/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/academic-calendar/holidays/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| DELETE /api/v1/academic-calendar/holidays/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/academic-calendar/holidays/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/academic-calendar/weeks/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| DELETE /api/v1/academic-calendar/weeks/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/academic-calendar/weeks/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/admin/activities/assignments/{assignmentId} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| DELETE /api/v1/admin/activities/assignments/{assignmentId} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/admin/activities/assignments/{assignmentId} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/admin/activities/{activityId} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| DELETE /api/v1/admin/activities/{activityId} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/admin/activities/{activityId} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/admin/activities/{activityId}/assignments/clear | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| DELETE /api/v1/admin/activities/{activityId}/assignments/clear | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/admin/activities/{activityId}/assignments/clear | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/admin/departments/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| DELETE /api/v1/admin/departments/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/admin/departments/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/admin/departments/{id}/sections/{sectionId} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| DELETE /api/v1/admin/departments/{id}/sections/{sectionId} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/admin/departments/{id}/sections/{sectionId} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/admin/stages/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| DELETE /api/v1/admin/stages/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/admin/stages/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/admin/stages/{stageId}/activities/{activityId} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| DELETE /api/v1/admin/stages/{stageId}/activities/{activityId} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/admin/stages/{stageId}/activities/{activityId} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/admin/subgroups/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| DELETE /api/v1/admin/subgroups/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/admin/subgroups/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/admin/subjects/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| DELETE /api/v1/admin/subjects/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/admin/subjects/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/admin/users/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| DELETE /api/v1/admin/users/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/admin/users/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/students/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| DELETE /api/v1/students/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/students/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/teams/{id}/captain | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| DELETE /api/v1/teams/{id}/captain | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/teams/{id}/captain | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/teams/{id}/members/{regNo} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| DELETE /api/v1/teams/{id}/members/{regNo} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/teams/{id}/members/{regNo} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/teams/{id}/vice-captain | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| DELETE /api/v1/teams/{id}/vice-captain | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/teams/{id}/vice-captain | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/teams/{teamId} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| DELETE /api/v1/teams/{teamId} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| DELETE /api/v1/teams/{teamId} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/activity-requests/inbox | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/activity-requests/inbox | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/activity-requests/inbox | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/activity-requests/my-requests | Authenticated Access | 403 | FAIL | Expected 2xx, got 403 |
| GET /api/activity-requests/my-requests | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/activity-requests/my-requests | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/admin/attendance/summary | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/admin/attendance/summary | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/admin/attendance/summary | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/admin/badge-requests | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/admin/badge-requests | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/admin/badge-requests | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/badge-requests/my | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/badge-requests/my | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/badge-requests/my | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/cc/badge-requests | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/cc/badge-requests | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/cc/badge-requests | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/penalties/cc-inbox | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/penalties/cc-inbox | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/penalties/cc-inbox | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/penalties/my-requests | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/penalties/my-requests | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/penalties/my-requests | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/student/attendance/history | Authenticated Access | 500 | FAIL | Expected 2xx, got 500 |
| GET /api/student/attendance/history | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/student/attendance/history | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/student/attendance/summary | Authenticated Access | 500 | FAIL | Expected 2xx, got 500 |
| GET /api/student/attendance/summary | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/student/attendance/summary | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/teacher/attendance/students | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/teacher/attendance/students | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/teacher/attendance/students | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/academic-calendar/month | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/academic-calendar/month | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/academic-calendar/month | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/academic-calendar/month/{monthId}/alternate-working-days | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/academic-calendar/month/{monthId}/alternate-working-days | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/academic-calendar/month/{monthId}/alternate-working-days | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/academic-calendar/month/{monthId}/holidays | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/academic-calendar/month/{monthId}/holidays | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/academic-calendar/month/{monthId}/holidays | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/academic-calendar/month/{monthId}/weeks | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/academic-calendar/month/{monthId}/weeks | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/academic-calendar/month/{monthId}/weeks | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/admin/academic-years | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/admin/academic-years | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/academic-years | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/activities | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/admin/activities | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/activities | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/activities/grouped | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/admin/activities/grouped | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/activities/grouped | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/activities/{id}/assignments | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/admin/activities/{id}/assignments | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/admin/activities/{id}/assignments | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/admin/activities/{id}/assignments | IDOR Test (access non-existent/other user resource) | 404 | PASS | Expected 403/404, got 404 |
| GET /api/v1/admin/captain-reward/settings/{year} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/admin/captain-reward/settings/{year} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/admin/captain-reward/settings/{year} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/admin/departments | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/admin/departments | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/departments | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/departments/class-coordinators | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/admin/departments/class-coordinators | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/departments/class-coordinators | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/departments/{id}/sections | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/admin/departments/{id}/sections | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/admin/departments/{id}/sections | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/admin/departments/{id}/sections | IDOR Test (access non-existent/other user resource) | 404 | PASS | Expected 403/404, got 404 |
| GET /api/v1/admin/frequencies/custom | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/admin/frequencies/custom | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/frequencies/custom | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/genders | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/admin/genders | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/genders | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/my-activities | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/admin/my-activities | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/my-activities | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/roles | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/admin/roles | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/roles | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/sections | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/admin/sections | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/sections | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/semesters | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/admin/semesters | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/semesters | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/stages | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/admin/stages | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/stages | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/stages/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/admin/stages/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/admin/stages/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/admin/stages/{id} | IDOR Test (access non-existent/other user resource) | 404 | PASS | Expected 403/404, got 404 |
| GET /api/v1/admin/stages/{id}/report | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/admin/stages/{id}/report | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/admin/stages/{id}/report | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/admin/stages/{id}/report | IDOR Test (access non-existent/other user resource) | 404 | PASS | Expected 403/404, got 404 |
| GET /api/v1/admin/stages/{stageId}/activities | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/admin/stages/{stageId}/activities | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/admin/stages/{stageId}/activities | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/admin/stats | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/admin/stats | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/stats | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/subgroups/{subgroupId}/activities | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/admin/subgroups/{subgroupId}/activities | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/admin/subgroups/{subgroupId}/activities | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/admin/subjects | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/admin/subjects | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/subjects | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/users | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/admin/users | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/users | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/years | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/admin/years | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/admin/years | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/attendance/departments | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/analytics/attendance/departments | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/attendance/departments | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/attendance/distribution | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/analytics/attendance/distribution | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/attendance/distribution | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/attendance/export | Authenticated Access | 0 | FAIL | Expected 2xx, got 0 |
| GET /api/v1/analytics/attendance/export | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/attendance/export | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/attendance/low-attendance | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/analytics/attendance/low-attendance | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/attendance/low-attendance | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/attendance/overview | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/analytics/attendance/overview | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/attendance/overview | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/attendance/sections | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/analytics/attendance/sections | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/attendance/sections | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/attendance/summary-table | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/analytics/attendance/summary-table | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/attendance/summary-table | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/attendance/trend | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/analytics/attendance/trend | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/attendance/trend | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/student | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/analytics/student | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/student | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/teacher | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/analytics/teacher | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/teacher | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/xp/activities | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/analytics/xp/activities | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/xp/activities | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/xp/award-penalty | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/analytics/xp/award-penalty | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/xp/award-penalty | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/xp/departments | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/analytics/xp/departments | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/xp/departments | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/xp/export-history | Authenticated Access | 0 | FAIL | Expected 2xx, got 0 |
| GET /api/v1/analytics/xp/export-history | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/xp/export-history | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/xp/heatmap | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/analytics/xp/heatmap | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/xp/heatmap | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/xp/history | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/analytics/xp/history | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/xp/history | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/xp/low-xp | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/analytics/xp/low-xp | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/xp/low-xp | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/xp/sections | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/analytics/xp/sections | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/xp/sections | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/xp/top-performers | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/analytics/xp/top-performers | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/analytics/xp/top-performers | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/attendance-engine/status | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/attendance-engine/status | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/attendance-engine/status | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/attendance-settings | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/attendance-settings | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/attendance-settings | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/auth/me | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/auth/me | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/auth/me | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/badges | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/badges | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/badges | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/badges/pending | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/badges/pending | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/badges/pending | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/badges/student/me | Authenticated Access | 500 | FAIL | Expected 2xx, got 500 |
| GET /api/v1/badges/student/me | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/badges/student/me | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/badges/student/{regNo} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/badges/student/{regNo} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/badges/student/{regNo} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/cc/dashboard/stats | Authenticated Access | 500 | FAIL | Expected 2xx, got 500 |
| GET /api/v1/cc/dashboard/stats | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/cc/dashboard/stats | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/group-activities/assignments/{assignmentId}/teams | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/group-activities/assignments/{assignmentId}/teams | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/group-activities/assignments/{assignmentId}/teams | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/leaderboard | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/leaderboard | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/leaderboard | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/leaderboard/filters | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/leaderboard/filters | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/leaderboard/filters | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/levels | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/levels | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/levels | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/levels/me/current | Authenticated Access | 500 | FAIL | Expected 2xx, got 500 |
| GET /api/v1/levels/me/current | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/levels/me/current | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/levels/student/{regNo}/current | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/levels/student/{regNo}/current | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/levels/student/{regNo}/current | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/my-activities/{activityId}/departments | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/my-activities/{activityId}/departments | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/my-activities/{activityId}/departments | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/my-activities/{activityId}/sections | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/my-activities/{activityId}/sections | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/my-activities/{activityId}/sections | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/my-activities/{activityId}/students | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/my-activities/{activityId}/students | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/my-activities/{activityId}/students | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/my-activities/{activityId}/years | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/my-activities/{activityId}/years | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/my-activities/{activityId}/years | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/profile/me | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/profile/me | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/profile/me | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/public/debug/attendance-activity | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/public/debug/attendance-activity | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/public/debug/attendance-activity | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/student-level/progression | Authenticated Access | 403 | FAIL | Expected 2xx, got 403 |
| GET /api/v1/student-level/progression | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/student-level/progression | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/students | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/students | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/students | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/students/department-performance | Authenticated Access | 403 | FAIL | Expected 2xx, got 403 |
| GET /api/v1/students/department-performance | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/students/department-performance | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/students/me/activity-streaks | Authenticated Access | 403 | FAIL | Expected 2xx, got 403 |
| GET /api/v1/students/me/activity-streaks | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/students/me/activity-streaks | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/students/search | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/students/search | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/students/search | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/students/stages | Authenticated Access | 403 | FAIL | Expected 2xx, got 403 |
| GET /api/v1/students/stages | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/students/stages | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/students/subgroups/{subgroupId}/activities | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/students/subgroups/{subgroupId}/activities | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/students/subgroups/{subgroupId}/activities | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/students/team-member-search | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/students/team-member-search | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/students/team-member-search | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/students/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/students/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/students/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/students/{id} | IDOR Test (access non-existent/other user resource) | 404 | PASS | Expected 403/404, got 404 |
| GET /api/v1/students/{id}/discipline-logs | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/students/{id}/discipline-logs | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/students/{id}/discipline-logs | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/students/{id}/discipline-logs | IDOR Test (access non-existent/other user resource) | 200 | FAIL | Expected 403/404, got 200 |
| GET /api/v1/superadmin/year-admins | Authenticated Access | 403 | FAIL | Expected 2xx, got 403 |
| GET /api/v1/superadmin/year-admins | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/superadmin/year-admins | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/teams | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/teams | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/teams | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/teams/my-classmates | Authenticated Access | 403 | FAIL | Expected 2xx, got 403 |
| GET /api/v1/teams/my-classmates | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/teams/my-classmates | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/teams/my-team | Authenticated Access | 500 | FAIL | Expected 2xx, got 500 |
| GET /api/v1/teams/my-team | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/teams/my-team | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/teams/my-team/details | Authenticated Access | 403 | FAIL | Expected 2xx, got 403 |
| GET /api/v1/teams/my-team/details | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/teams/my-team/details | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/teams/removal-requests/pending | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| GET /api/v1/teams/removal-requests/pending | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/teams/removal-requests/pending | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| GET /api/v1/teams/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/teams/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/teams/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/teams/{id} | IDOR Test (access non-existent/other user resource) | 404 | PASS | Expected 403/404, got 404 |
| GET /api/v1/xp/{regNo}/history | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/xp/{regNo}/history | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/xp/{regNo}/history | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/xp/{regNo}/streaks | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/xp/{regNo}/streaks | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/xp/{regNo}/streaks | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/xp/{regNo}/summary | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| GET /api/v1/xp/{regNo}/summary | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| GET /api/v1/xp/{regNo}/summary | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/activity-requests | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/activity-requests | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/activity-requests | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/activity-requests | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/badge-requests | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/badge-requests | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/badge-requests | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/badge-requests | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/penalties | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/penalties | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/penalties | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/penalties | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/teacher/attendance/save | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/teacher/attendance/save | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/teacher/attendance/save | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/teacher/attendance/save | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/academic-calendar/alternate-working-days | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/academic-calendar/alternate-working-days | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/academic-calendar/alternate-working-days | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/academic-calendar/alternate-working-days | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/academic-calendar/holidays | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/academic-calendar/holidays | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/academic-calendar/holidays | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/academic-calendar/holidays | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/academic-calendar/weeks | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/academic-calendar/weeks | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/academic-calendar/weeks | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/academic-calendar/weeks | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/admin/activities/{id}/assign | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/admin/activities/{id}/assign | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/admin/activities/{id}/assign | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/admin/activities/{id}/assign | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/admin/activities/{id}/assignments | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/admin/activities/{id}/assignments | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/admin/activities/{id}/assignments | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/admin/activities/{id}/assignments | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/admin/activity/{id}/assign | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/admin/activity/{id}/assign | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/admin/activity/{id}/assign | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/admin/activity/{id}/assign | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/admin/departments | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/admin/departments | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/admin/departments | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/admin/departments | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/admin/departments/{id}/sections | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/admin/departments/{id}/sections | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/admin/departments/{id}/sections | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/admin/departments/{id}/sections | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/admin/frequencies/custom | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/admin/frequencies/custom | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/admin/frequencies/custom | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/admin/frequencies/custom | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/admin/roles | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/admin/roles | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/admin/roles | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/admin/roles | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/admin/stages | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/admin/stages | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/admin/stages | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/admin/stages | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/admin/stages/evaluate-promotions | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| POST /api/v1/admin/stages/evaluate-promotions | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/admin/stages/evaluate-promotions | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/admin/stages/evaluate-promotions | Empty Body Input Validation | 200 | FAIL | Expected 400/422, got 200 |
| POST /api/v1/admin/stages/{stageId}/activities/{activityId} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/admin/stages/{stageId}/activities/{activityId} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/admin/stages/{stageId}/activities/{activityId} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/admin/stages/{stageId}/activities/{activityId} | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/admin/stages/{stageId}/subgroups | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/admin/stages/{stageId}/subgroups | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/admin/stages/{stageId}/subgroups | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/admin/stages/{stageId}/subgroups | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/admin/subgroups/{subgroupId}/activities | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/admin/subgroups/{subgroupId}/activities | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/admin/subgroups/{subgroupId}/activities | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/admin/subgroups/{subgroupId}/activities | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/admin/subjects | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/admin/subjects | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/admin/subjects | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/admin/subjects | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/admin/users | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/admin/users | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/admin/users | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/admin/users | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/attendance-engine/reset | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| POST /api/v1/attendance-engine/reset | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/attendance-engine/reset | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/attendance-engine/reset | Empty Body Input Validation | 200 | FAIL | Expected 400/422, got 200 |
| POST /api/v1/attendance-engine/run-both | Authenticated Access | 500 | FAIL | Expected 2xx, got 500 |
| POST /api/v1/attendance-engine/run-both | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/attendance-engine/run-both | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/attendance-engine/run-both | Empty Body Input Validation | 500 | FAIL | Expected 400/422, got 500 |
| POST /api/v1/attendance-engine/run-daily | Authenticated Access | 500 | FAIL | Expected 2xx, got 500 |
| POST /api/v1/attendance-engine/run-daily | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/attendance-engine/run-daily | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/attendance-engine/run-daily | Empty Body Input Validation | 500 | FAIL | Expected 400/422, got 500 |
| POST /api/v1/attendance-engine/run-weekly | Authenticated Access | 200 | PASS | Expected 2xx, got 200 |
| POST /api/v1/attendance-engine/run-weekly | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/attendance-engine/run-weekly | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/attendance-engine/run-weekly | Empty Body Input Validation | 200 | FAIL | Expected 400/422, got 200 |
| POST /api/v1/badges/submit | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/badges/submit | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/badges/submit | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/badges/submit | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/group-activities/teams/{teamId}/award-xp | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/group-activities/teams/{teamId}/award-xp | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/group-activities/teams/{teamId}/award-xp | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/group-activities/teams/{teamId}/award-xp | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/student-xp/award | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/student-xp/award | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/student-xp/award | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/student-xp/award | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/student-xp/award/batch | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/student-xp/award/batch | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/student-xp/award/batch | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/student-xp/award/batch | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/students | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/students | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/students | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/students | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/students/bulk-import | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/students/bulk-import | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/students/bulk-import | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/students/bulk-import | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/students/bulk-parse | Authenticated Access | 500 | FAIL | Expected 2xx, got 500 |
| POST /api/v1/students/bulk-parse | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/students/bulk-parse | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/students/bulk-parse | Empty Body Input Validation | 500 | FAIL | Expected 400/422, got 500 |
| POST /api/v1/students/{id}/adjust-points | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/students/{id}/adjust-points | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/students/{id}/adjust-points | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/students/{id}/adjust-points | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/students/{id}/make-captain | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/students/{id}/make-captain | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/students/{id}/make-captain | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/students/{id}/make-captain | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/students/{id}/remove-captain | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/students/{id}/remove-captain | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/students/{id}/remove-captain | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/students/{id}/remove-captain | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/teams | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/teams | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/teams | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/teams | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/teams/my-team/add-member | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/teams/my-team/add-member | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/teams/my-team/add-member | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/teams/my-team/add-member | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/teams/my-team/remove-request | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/teams/my-team/remove-request | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/teams/my-team/remove-request | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/teams/my-team/remove-request | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/teams/{id}/add-member | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/teams/{id}/add-member | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/teams/{id}/add-member | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/teams/{id}/add-member | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/teams/{id}/captain | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/teams/{id}/captain | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/teams/{id}/captain | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/teams/{id}/captain | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/teams/{id}/members | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/teams/{id}/members | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/teams/{id}/members | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/teams/{id}/members | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/teams/{id}/remove-member | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/teams/{id}/remove-member | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/teams/{id}/remove-member | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| POST /api/v1/teams/{id}/remove-member | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/xp/penalty | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/xp/penalty | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/xp/penalty | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/xp/penalty | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| POST /api/v1/xp/submit | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| POST /api/v1/xp/submit | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/xp/submit | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| POST /api/v1/xp/submit | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/activity-requests/{id}/approve | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/activity-requests/{id}/approve | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/activity-requests/{id}/approve | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/activity-requests/{id}/approve | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/activity-requests/{id}/reject | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/activity-requests/{id}/reject | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/activity-requests/{id}/reject | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/activity-requests/{id}/reject | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/admin/badge-requests/{id}/approve | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/admin/badge-requests/{id}/approve | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/admin/badge-requests/{id}/approve | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/admin/badge-requests/{id}/approve | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/admin/badge-requests/{id}/reject | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/admin/badge-requests/{id}/reject | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/admin/badge-requests/{id}/reject | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/admin/badge-requests/{id}/reject | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/cc/badge-requests/{id}/approve | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/cc/badge-requests/{id}/approve | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/cc/badge-requests/{id}/approve | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/cc/badge-requests/{id}/approve | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/cc/badge-requests/{id}/reject | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/cc/badge-requests/{id}/reject | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/cc/badge-requests/{id}/reject | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/cc/badge-requests/{id}/reject | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/penalties/{id}/approve | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/penalties/{id}/approve | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/penalties/{id}/approve | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/penalties/{id}/approve | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/penalties/{id}/reject | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/penalties/{id}/reject | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/penalties/{id}/reject | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/penalties/{id}/reject | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/academic-calendar/alternate-working-days/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/academic-calendar/alternate-working-days/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/academic-calendar/alternate-working-days/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/academic-calendar/alternate-working-days/{id} | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/academic-calendar/holidays/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/academic-calendar/holidays/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/academic-calendar/holidays/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/academic-calendar/holidays/{id} | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/academic-calendar/weeks/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/academic-calendar/weeks/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/academic-calendar/weeks/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/academic-calendar/weeks/{id} | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/admin/activities/{activityId} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/admin/activities/{activityId} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/admin/activities/{activityId} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/admin/activities/{activityId} | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/admin/captain-reward/settings/{year} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/admin/captain-reward/settings/{year} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/admin/captain-reward/settings/{year} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/admin/captain-reward/settings/{year} | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/admin/departments/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/admin/departments/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/admin/departments/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/admin/departments/{id} | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/admin/stages/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/admin/stages/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/admin/stages/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/admin/stages/{id} | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/admin/subgroups/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/admin/subgroups/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/admin/subgroups/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/admin/subgroups/{id} | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/admin/subgroups/{id}/assign-faculty | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/admin/subgroups/{id}/assign-faculty | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/admin/subgroups/{id}/assign-faculty | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/admin/subgroups/{id}/assign-faculty | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/admin/users/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/admin/users/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/admin/users/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/admin/users/{id} | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/attendance-settings | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/attendance-settings | No Auth (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| PUT /api/v1/attendance-settings | Invalid Token (should be 401/403) | 401 | PASS | Expected 401/403, got 401 |
| PUT /api/v1/attendance-settings | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/badges/{id}/approve | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/badges/{id}/approve | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/badges/{id}/approve | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/badges/{id}/approve | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/badges/{id}/reject | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/badges/{id}/reject | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/badges/{id}/reject | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/badges/{id}/reject | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/students/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/students/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/students/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/students/{id} | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/superadmin/year-admins/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/superadmin/year-admins/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/superadmin/year-admins/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/superadmin/year-admins/{id} | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/teams/removal-requests/{id}/approve | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/teams/removal-requests/{id}/approve | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/teams/removal-requests/{id}/approve | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/teams/removal-requests/{id}/approve | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/teams/removal-requests/{id}/reject | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/teams/removal-requests/{id}/reject | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/teams/removal-requests/{id}/reject | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/teams/removal-requests/{id}/reject | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/teams/{id} | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/teams/{id} | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/teams/{id} | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/teams/{id} | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/teams/{id}/captain | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/teams/{id}/captain | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/teams/{id}/captain | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/teams/{id}/captain | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/teams/{id}/limit | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/teams/{id}/limit | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/teams/{id}/limit | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/teams/{id}/limit | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/teams/{id}/vice-captain | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/teams/{id}/vice-captain | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/teams/{id}/vice-captain | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/teams/{id}/vice-captain | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/xp/{id}/approve | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/xp/{id}/approve | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/xp/{id}/approve | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/xp/{id}/approve | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
| PUT /api/v1/xp/{id}/reject | Authenticated Access | 400 | FAIL | Expected 2xx, got 400 |
| PUT /api/v1/xp/{id}/reject | No Auth (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/xp/{id}/reject | Invalid Token (should be 401/403) | 400 | FAIL | Expected 401/403, got 400 |
| PUT /api/v1/xp/{id}/reject | Empty Body Input Validation | 400 | PASS | Expected 400/422, got 400 |
