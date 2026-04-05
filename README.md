# 🎓 Student Management Dashboard – Pro Edition

A production-ready Flask web application for managing students, courses, and users with authentication, role-based access control, profile picture upload, course enrollment APIs, search, and pagination.

---

## 📌 Project Overview

This project is an expanded version of the Student Management Dashboard built with Flask. It supports:

- Authentication system
- Role-based users: **Admin, Instructor, Student**
- Student-Course **many-to-many** relationship
- Profile picture upload
- Course enrollment and unenrollment API
- Search and pagination
- HTML pages with Jinja templates
- REST API endpoints
- SQLite database with SQLAlchemy
- Seeded demo data

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

-   Added many-to-many relationship between students and courses
-   Linked student accounts with user accounts

### Milestone 3 --- Profile Picture Upload

-   Added profile image upload
-   Stored images in uploads folder
-   Added validation

### Milestone 4 --- Course Enrollment API

-   Added enroll & unenroll endpoints
-   Admin/Instructor can manage enrollments

### Milestone 5 --- Search and Pagination

-   Added search to students, courses, users
-   Added pagination

### Milestone 6 --- Documentation and Cleanup

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

## 🗃️ Database Schema

### User
- id (PK)
- username (unique)
- email (unique)
- password_hash
- role (admin, instructor, student)
- profile_picture

### Student
- id (PK)
- name
- student_id (unique)
- user_id (FK)

### Course
- id (PK)
- name (unique)
- code (unique)
- description

### student_courses
- student_id (FK)
- course_id (FK)

---

## 🌐 API Endpoints

### Students
GET /api/students  
POST /api/students  
GET /api/students/<id>  
PUT /api/students/<id>  
DELETE /api/students/<id>  
POST /api/students/<id>/enroll  
POST /api/students/<id>/unenroll  

### Courses
GET /api/courses  
POST /api/courses  
GET /api/courses/<id>  
PUT /api/courses/<id>  
DELETE /api/courses/<id>  

### Users
GET /api/users  
POST /api/users  
GET /api/users/<id>  
PUT /api/users/<id>  
DELETE /api/users/<id>  

---

## 🔎 Search & Pagination

Example:
GET /api/students?search=ali&page=1&per_page=5

---
## 🖼️ Profile Picture Upload

- Supported: png, jpg, jpeg, gif
- Max size: 2MB
- Folder: app/static/uploads

------------------------------------------------------------------------

## 🔐 Roles

### Admin

-   Full access

### Instructor

-   Manage students & courses

### Student

-   View own courses only


------------------------------------------------------------------------

## 🌱 Seed Data

-   Admin: admin@gmail.com
-   Instructor: instructor1@najah.edu

------------------------------------------------------------------------

## ⚙️ Setup

``` bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python seed.py
python run.py
```

------------------------------------------------------------------------

## 🧪 Tests

``` bash
python -m pytest
```

