## 🎓 Student Management Dashboard – Pro Edition

A production-ready Flask web application for managing students, courses, and users with authentication, role-based access control, profile picture upload, course enrollment APIs, search, and pagination.

---

## 📌 Project Overview

This project is an expanded version of the Student Management Dashboard built with Flask. It supports:

- Authentication system
- Role-based users: **Admin, Instructor, Student**
- Student-Course many-to-many relationship using an **Enrollment** table
- Course enrollment and unenrollment API
- Search, filtering, and pagination
- Relationship tests for enrollments and cascading deletes
- Profile picture upload
- HTML pages with Jinja templates
- REST API endpoints
- SQLite database with SQLAlchemy
- Seeded demo data for admin, instructor, students, courses, and enrollments

---
## 🌿 Git Branching Strategy

This project follows a simple Git workflow:

-   `main` → stable production-ready branch
-   `dev` → main development branch
-   `feature/*` → feature branches created from `dev`

### Example workflow

``` bash
git checkout -b dev
git push -u origin dev

git checkout dev
git checkout -b feature/readme-docs
```

------------------------------------------------------------------------

## 🎯 Milestones

### Milestone 1 --- Role-Based Access Control

-   Added roles: admin, instructor, student
-   Restricted access using decorators
-   Prevented students from accessing the management dashboard

### Milestone 2 --- Database Relationship Expansion

-   Replaced the plain join table with an `Enrollment` model
-   Added unique enrollment constraint per student-course pair
-   Added cascading deletes for related enrollments
-   Linked student accounts with user accounts

### Milestone 3 --- Profile Picture Upload

-   Added profile image upload
-   Stored images in uploads folder
-   Added validation

### Milestone 4 --- Course Enrollment API

-   Added enroll & unenroll endpoints
-   Added endpoints to list a student's courses and a course's students
-   Admin/Instructor can manage enrollments

### Milestone 5 --- Search, Filtering, and Pagination

-   Added search to students, courses, users
-   Added pagination to HTML pages and APIs
-   Added relationship-based filtering where applicable

### Milestone 6 --- Relationship Testing

-   Added tests for enrollments
-   Added tests for duplicate enrollment prevention
-   Added tests for cascade delete behavior

### Milestone 7 --- Documentation and Cleanup

-   Documented schema and APIs
-   Clean architecture applied

------------------------------------------------------------------------

## 🛠️ Tech Stack

-   Flask
-   SQLAlchemy
-   SQLite
-   Flask-Login
-   Jinja2
-   HTML/CSS
-   Pytest

------------------------------------------------------------------------

## 📁 Project Structure
```
Student Management Dashboard - Pro Edition/
│
├── app/
│   ├── models/
│   │   ├── user.py
│   │   ├── student.py
│   │   ├── enrollment.py
│   │   ├── course.py
│   │   └── __init__.py
│   │
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── main_routes.py
│   │   ├── student_api_routes.py
│   │   ├── student_page_routes.py
│   │   ├── course_api_routes.py
│   │   ├── course_page_routes.py
│   │   ├── user_api_routes.py
│   │   └── user_page_routes.py
│   │
│   ├── services/
│   ├── templates/
│   ├── static/
│   │   └── uploads/
│   ├── config.py
│   ├── extensions.py
│   └── __init__.py
│
├── tests/
├── seed.py
├── run.py
├── requirements.txt
└── README.md
```
------------------------------------------------------------------------

# 📘 API & Database Documentation

## 🗃️ Database Schema

### 👤 User

| Field           | Type            | Description                  |
| --------------- | --------------- | ---------------------------- |
| id              | Integer (PK)    | Unique user ID               |
| username        | String (unique) | Username                     |
| email           | String (unique) | Email address                |
| password_hash   | String          | Hashed password              |
| role            | String          | admin / instructor / student |
| profile_picture | String          | Image filename               |

---

### 🎓 Student

| Field      | Type            | Description           |
| ---------- | --------------- | --------------------- |
| id         | Integer (PK)    | Unique ID             |
| name       | String          | Full name             |
| student_id | String (unique) | University student ID |
| user_id    | Integer (FK)    | Linked user account   |

---

### 📘 Course

| Field       | Type            | Description          |
| ----------- | --------------- | -------------------- |
| id          | Integer (PK)    | Unique ID            |
| name        | String (unique) | Course name          |
| code        | String (unique) | Course code          |
| description | String          | Optional description |

---

### 🔗 Enrollment

| Field       | Type             | Description                         |
| ----------- | ---------------- | ----------------------------------- |
| id          | Integer (PK)     | Unique enrollment ID                |
| student_id  | FK → students.id | Student reference                   |
| course_id   | FK → courses.id  | Course reference                    |
| enrolled_at | DateTime         | UTC timestamp when enrollment added |

**Constraints**
- Unique constraint on `(student_id, course_id)` to prevent duplicate enrollments
- Cascading delete when a student or course is removed

---

## 🌐 API Endpoints

### 🎓 Students API

#### Get all students (with search, filtering & pagination)

```http
GET /api/students?search=ali&course_id=1&page=1&per_page=5
```

#### Create student

```
POST /api/students
Content-Type: application/json

{
  "name": "Ali Ahmad",
  "student_id": "12110002",
  "course_ids": [1, 2]
}
```

#### Get single student

```
GET /api/students/<student_id>
```

#### Update student

```
PUT /api/students/<student_id>
```

#### Delete student

```
DELETE /api/students/<student_id>
```

#### Enroll student in course

```
POST /api/students/<student_id>/enroll

{
  "course_id": 1
}
```

#### Unenroll student

```
POST /api/students/<student_id>/unenroll
```

---

### 📘 Courses API

### 📘 Courses API

#### Get all courses (with search, filtering & pagination)

```http
GET /api/courses?search=data&student_db_id=1&page=1&per_page=5
```

#### Create course

```
POST /api/courses
```

#### Get course

```
GET /api/courses/<id>
```
#### Get students enrolled in a course
```
GET /api/courses/<id>/students
```
#### Update course

```
PUT /api/courses/<id>
```

#### Delete course

```
DELETE /api/courses/<id>
```

---

### 👤 Users API (Admin Only)

#### Get all users

```
GET /api/users
```

#### Create user

```
POST /api/users
```

#### Get user

```
GET /api/users/<id>
```

#### Update user

```
PUT /api/users/<id>
```

#### Delete user

```
DELETE /api/users/<id>
```

⚠️ Note: Admin cannot delete their own account (protected in backend logic).

---

## 🔐 Authentication Notes
This app uses session-based authentication (Flask-Login).

* All endpoints require login
- Login via `/login`
- Session cookie is used automatically
* Role-based access enforced:

  * Admin → full access
  * Instructor → manage students & courses
  * Student → limited access

---

## 📦 Response Format

### Success

```
{
  "success": true,
  "data": {...}
}
```

### Error

```
{
  "success": false,
  "error": "Error message"
}
```

---

## 🔎 Pagination Response Example

```
{
  "success": true,
  "count": 5,
  "total": 20,
  "page": 1,
  "pages": 4,
  "filters": {
    "search": "ali",
    "course_id": 1
  },
  "data": [...]

```

---

## 🧪 Notes from Implementation

* Validation handled in **services layer**
* Errors:

  * 400 → ValidationError
  * 404 → NotFoundError
  * 409 → ConflictError
* API returns JSON for all `/api/*` routes 





---
## 🖼️ Profile Picture Upload

- Supported: png, jpg, jpeg, gif
- Max size: 2MB
- Folder: app/static/uploads


------------------------------------------------------------------------

## ⚙️ Setup

``` bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

------------------------------------------------------------------------

## 🧪 Tests

``` bash
python -m pytest
```

---

