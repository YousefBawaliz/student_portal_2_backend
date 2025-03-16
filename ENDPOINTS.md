# Student Portal API Endpoints

## Authentication Endpoints (`/api/auth`)
- POST /api/auth/login
  - Description: User Login
  - Auth: None
  - Request Body: { email, password }
  - Response: { access_token, refresh_token, user }

- POST /api/auth/refresh
  - Description: Refresh access token
  - Auth: JWT Refresh Token
  - Response: { access_token }

- POST /api/auth/logout
  - Description: Logout user
  - Auth: JWT Required
  - Response: { message }

## User Endpoints (`/api/users`)
- GET /api/users/me
  - Description: Get current user's profile
  - Auth: JWT Required
  - Response: User object

- PUT /api/users/me
  - Description: Update current user's profile
  - Auth: JWT Required
  - Request Body: { first_name?, last_name?, email?, theme_preference?, profile_image?, password? }
  - Response: Updated user object

- GET /api/users/
  - Description: Get all users (admin only)
  - Auth: JWT Required (Admin)
  - Query Params: pagination parameters
  - Response: Array of user objects

## Course Endpoints (`/api/courses`)
- GET /api/courses/
  - Description: Get all courses (filtered by role)
  - Auth: JWT Required
  - Response: Array of course objects

- POST /api/courses/
  - Description: Create a new course (admin only)
  - Auth: JWT Required (Admin)
  - Request Body: { course_code, title, description? }
  - Response: Created course object

- GET /api/courses/<course_id>
  - Description: Get course details
  - Auth: JWT Required
  - Response: Course object

- PUT /api/courses/<course_id>
  - Description: Update course details (admin only)
  - Auth: JWT Required (Admin)
  - Request Body: { title?, description?, is_active? }
  - Response: Updated course object

- DELETE /api/courses/<course_id>
  - Description: Delete a course (admin only)
  - Auth: JWT Required (Admin)
  - Response: { message }

## Class Endpoints (`/api/classes`)
- GET /api/classes/
  - Description: Get all classes (filtered by role)
  - Auth: JWT Required
  - Response: Array of class objects

- POST /api/classes/
  - Description: Create a new class (admin only)
  - Auth: JWT Required (Admin)
  - Request Body: ClassCreateSchema
  - Response: Created class object

- GET /api/classes/<class_id>
  - Description: Get class details
  - Auth: JWT Required
  - Response: Class object

- PUT /api/classes/<class_id>
  - Description: Update class details (admin only)
  - Auth: JWT Required (Admin)
  - Request Body: ClassUpdateSchema
  - Response: Updated class object

- POST /api/classes/<class_id>/enroll
  - Description: Enroll in a class (students only)
  - Auth: JWT Required
  - Response: Enrollment object

- DELETE /api/classes/<class_id>/enroll
  - Description: Unenroll from a class
  - Auth: JWT Required
  - Response: { message }

## Assessment Endpoints (`/api/assessments`)
- GET /api/assessments/
  - Description: Get all assessments (filtered by role)
  - Auth: JWT Required
  - Response: Array of assessment objects
  - Notes: 
    - Admins see all assessments
    - Teachers see assessments for their classes
    - Students see assessments for enrolled classes

- POST /api/assessments/
  - Description: Create a new assessment (teacher only)
  - Auth: JWT Required (Teacher)
  - Request Body: { 
      class_id, 
      title, 
      type, 
      date 
    }
  - Response: Created assessment object

- GET /api/assessments/<assessment_id>
  - Description: Get assessment details
  - Auth: JWT Required
  - Response: Assessment object

- PUT /api/assessments/<assessment_id>
  - Description: Update assessment details (teacher only)
  - Auth: JWT Required (Teacher)
  - Request Body: { 
      title?, 
      type?, 
      date? 
    }
  - Response: Updated assessment object

- DELETE /api/assessments/<assessment_id>
  - Description: Delete an assessment (teacher only)
  - Auth: JWT Required (Teacher)
  - Response: { message }

- GET /api/assessments/<assessment_id>/scores
  - Description: Get all scores for an assessment
  - Auth: JWT Required
  - Response: Array of score objects
  - Notes:
    - Students can only see their own scores
    - Teachers can only see scores for their classes
    - Admins can see all scores

## Score Endpoints (`/api/scores`)
- POST /api/scores/
  - Description: Create a new score (teacher only)
  - Auth: JWT Required (Teacher)
  - Request Body: { student_id, assessment_id, score_value, feedback? }
  - Response: Created score object

- GET /api/scores/<score_id>
  - Description: Get a specific score
  - Auth: JWT Required
  - Response: Score object
  - Notes:
    - Students can only view their own scores
    - Teachers can only view scores for their classes
    - Admins can see all scores

- PUT /api/scores/<score_id>
  - Description: Update a score (teacher only)
  - Auth: JWT Required (Teacher)
  - Request Body: { score_value?, feedback? }
  - Response: Updated score object

- DELETE /api/scores/<score_id>
  - Description: Delete a score (teacher only)
  - Auth: JWT Required (Teacher)
  - Response: { message }

- GET /api/scores/student/<student_id>
  - Description: Get all scores for a student
  - Auth: JWT Required
  - Response: Array of score objects

- GET /api/scores/student/<student_id>/assessment
  - Description: Get a student's score by assessment title
  - Auth: JWT Required
  - Query Params: title (required)
  - Response: Score object

## Debug Endpoints
- GET /api/test-jwt
  - Description: Verify JWT configuration
  - Auth: JWT Required
  - Response: { message, user_id }

## Response Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 409: Conflict
- 500: Internal Server Error

## Authentication
All protected endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Notes
- All endpoints are prefixed with `/api`
- Pagination is available on list endpoints where applicable
- Role-based access control is implemented (Student, Teacher, Admin)
- JWT tokens are required for most endpoints