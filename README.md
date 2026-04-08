## 🎓 Student Management Dashboard – Pro Edition

A production-ready Flask web application for managing students, courses, and users with authentication, role-based access control, profile picture upload, course enrollment APIs, search, and pagination.

---

## 🚀 Features

* 🔐 Authentication system (Register / Login / Logout)
* 🧑‍💼 Role-based access control:

  * **Admin**
  * **Instructor**
  * **Student**
* 🎓 Student–Course **many-to-many relationship**
* 📸 Profile picture upload (with validation)
* 🔗 Course enrollment & unenrollment APIs
* 🔍 Dynamic search (via Fetch API)
* 📄 Pagination (UI + API)
* ⚙️ Clean architecture (Routes → Services)
* 🧪 Full test coverage with pytest
* 🌱 Automatic database seeding
* 🎨 Modern UI (Bootstrap + custom styling)

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
- Error handling (JSON + HTML)
- CI-ready structure

---
## 🌿 Git Branching Strategy

| Branch      | Purpose            |
| ----------- | ------------------ |
| `main`      | Stable production  |
| `dev`       | Active development |
| `feature/*` | Feature branches   |

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

### Milestone 6 --- Testing

-   Relationship tests
-   API tests
-   Error handling tests

### Milestone 7 --- Documentation and Cleanup

-   Documented schema and APIs
-   Clean architecture applied

------------------------------------------------------------------------

## 🛠️ Tech Stack

-   Flask
-   SQLAlchemy
-   SQLite
-   Flask-Login
-   Flask-WTF (CSRF protection)
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
│   │   ├── uploads/
│   │   └── js/
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

### 🎓 Students

| Method | Endpoint                      | Description    |
| ------ | ----------------------------- | -------------- |
| GET    | `/api/students`               | List students  |
| POST   | `/api/students`               | Create student |
| GET    | `/api/students/<id>`          | Get student    |
| PUT    | `/api/students/<id>`          | Update         |
| DELETE | `/api/students/<id>`          | Delete         |
| POST   | `/api/students/<id>/enroll`   | Enroll         |
| POST   | `/api/students/<id>/unenroll` | Unenroll       |

---

### 📘 Courses

| Method | Endpoint                     |
| ------ | ---------------------------- |
| GET    | `/api/courses`               |
| POST   | `/api/courses`               |
| GET    | `/api/courses/<id>`          |
| PUT    | `/api/courses/<id>`          |
| DELETE | `/api/courses/<id>`          |
| GET    | `/api/courses/<id>/students` |

---

### 👤 Users (Admin Only)

| Method | Endpoint          |
| ------ | ----------------- |
| GET    | `/api/users`      |
| POST   | `/api/users`      |
| GET    | `/api/users/<id>` |
| PUT    | `/api/users/<id>` |
| DELETE | `/api/users/<id>` |

⚠️ Admin cannot delete their own account.

---

## 🔐 Authentication

* Session-based authentication (Flask-Login)
* All `/api/*` routes require login 
* Role-based permissions:

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

## 🖼️ Profile Upload

* Allowed: png, jpg, jpeg, gif
* Max size: 2MB
* Stored in: `app/static/uploads`

---

## ⚙️ Environment Variables

Create a `.env` file:

```
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///students.db
FLASK_ENV=development
```

---



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

