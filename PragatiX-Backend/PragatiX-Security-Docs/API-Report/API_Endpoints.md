# API Endpoints List

Below is the list of all API endpoints extracted from the documentation, organized by controller.

## SUMMARY
* **Total Controllers:** 17
* **Total APIs:** 102
* **GET:** 45
* **POST:** 32
* **PUT:** 15
* **PATCH:** 0
* **DELETE:** 10
* **Public APIs:** 2
* **Protected APIs:** 100

---

## APIs Grouped By Controller

### AdminActivityController
* `GET /api/v1/admin/my-activities`
* `GET /api/v1/admin/subgroups/{subgroupId}/activities`
* `POST /api/v1/admin/subgroups/{subgroupId}/activities`
* `PUT /api/v1/admin/activities/{activityId}`
* `POST /api/v1/admin/activities/{id}/assign`
* `DELETE /api/v1/admin/activities/{activityId}`
* `GET /api/v1/admin/frequencies/custom`
* `POST /api/v1/admin/frequencies/custom`

### AdminDashboardController
* `GET /api/v1/admin/stats`

### AdminDepartmentController
* `GET /api/v1/admin/departments`
* `POST /api/v1/admin/departments`
* `PUT /api/v1/admin/departments/{id}`
* `DELETE /api/v1/admin/departments/{id}`
* `GET /api/v1/admin/departments/{id}/sections`
* `POST /api/v1/admin/departments/{id}/sections`
* `DELETE /api/v1/admin/departments/{id}/sections/{sectionId}`
* `GET /api/v1/admin/departments/class-coordinators`

### AdminFacultyController
* `PUT /api/v1/admin/subgroups/{id}/assign-faculty`

### AdminLookupController
* `GET /api/v1/admin/academic-years`
* `GET /api/v1/admin/years`
* `GET /api/v1/admin/semesters`
* `GET /api/v1/admin/genders`
* `GET /api/v1/admin/sections`

### AdminRoleController
* `GET /api/v1/admin/roles`
* `POST /api/v1/admin/roles`

### AdminStageController
* `GET /api/v1/admin/stages`
* `POST /api/v1/admin/stages`
* `GET /api/v1/admin/stages/{id}`
* `PUT /api/v1/admin/stages/{id}`
* `GET /api/v1/admin/stages/{id}/report`
* `DELETE /api/v1/admin/stages/{id}`

### AdminSubgroupController
* `POST /api/v1/admin/stages/{stageId}/subgroups`
* `PUT /api/v1/admin/subgroups/{id}`
* `DELETE /api/v1/admin/subgroups/{id}`

### AdminSubjectController
* `GET /api/v1/admin/subjects`
* `POST /api/v1/admin/subjects`
* `DELETE /api/v1/admin/subjects/{id}`

### AdminUserController
* `GET /api/v1/admin/users`
* `POST /api/v1/admin/users`
* `PUT /api/v1/admin/users/{id}`
* `DELETE /api/v1/admin/users/{id}`

### AuthController
* `POST /api/v1/auth/login`
* `POST /api/v1/auth/student-login`
* `GET /api/v1/auth/me`

### GroupActivityController
* `GET /api/v1/group-activities/assignments/{assignmentId}/teams`
* `POST /api/v1/group-activities/teams/{teamId}/award-xp`

### LevelBadgeController
* `GET /api/v1/levels`
* `GET /api/v1/levels/student/{studentId}/current`
* `GET /api/v1/levels/me/current`
* `GET /api/v1/badges`
* `GET /api/v1/badges/student/me`
* `GET /api/v1/badges/student/{studentId}`
* `POST /api/v1/badges/submit`
* `PUT /api/v1/badges/{id}/approve`
* `PUT /api/v1/badges/{id}/reject`
* `GET /api/v1/badges/pending`

### StudentController
* `POST /api/v1/students`
* `GET /api/v1/students`
* `GET /api/v1/students/{id}`
* `GET /api/v1/students/search`
* `DELETE /api/v1/students/{id}`
* `PUT /api/v1/students/{id}`
* `POST /api/v1/students/bulk-parse`
* `POST /api/v1/students/bulk-import`
* `POST /api/v1/students/{id}/adjust-points`
* `GET /api/v1/students/{id}/discipline-logs`
* `GET /api/v1/students/department-performance`
* `POST /api/v1/students/{id}/make-captain`
* `POST /api/v1/students/{id}/remove-captain`
* `GET /api/v1/students/stages`
* `GET /api/v1/students/subgroups/{subgroupId}/activities`

### StudentXpController
* `GET /api/v1/my-activities/{activityId}/years`
* `GET /api/v1/my-activities/{activityId}/departments`
* `GET /api/v1/my-activities/{activityId}/sections`
* `GET /api/v1/my-activities/{activityId}/students`
* `POST /api/v1/student-xp/award`
* `POST /api/v1/student-xp/award/batch`

### TeamController
* `POST /api/v1/teams`
* `GET /api/v1/teams`
* `GET /api/v1/teams/my-team`
* `GET /api/v1/teams/{id}`
* `PUT /api/v1/teams/{id}`
* `POST /api/v1/teams/{id}/members`
* `DELETE /api/v1/teams/{id}/members/{studentId}`
* `POST /api/v1/teams/{id}/captain`
* `GET /api/v1/teams/my-classmates`
* `POST /api/v1/teams/my-team/add-member`
* `POST /api/v1/teams/{id}/add-member`
* `POST /api/v1/teams/{id}/remove-member`
* `POST /api/v1/teams/my-team/remove-request`
* `GET /api/v1/teams/removal-requests/pending`
* `PUT /api/v1/teams/removal-requests/{id}/approve`
* `PUT /api/v1/teams/removal-requests/{id}/reject`
* `PUT /api/v1/teams/{id}/limit`
* `DELETE /api/v1/teams/{teamId}`

### XpController
* `GET /api/v1/xp/{studentId}/summary`
* `GET /api/v1/xp/{studentId}/history`
* `GET /api/v1/xp/{studentId}/streaks`
* `POST /api/v1/xp/submit`
* `PUT /api/v1/xp/{id}/approve`
* `PUT /api/v1/xp/{id}/reject`
* `POST /api/v1/xp/penalty`
