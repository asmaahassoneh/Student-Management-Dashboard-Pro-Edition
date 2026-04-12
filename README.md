# 🎓 Student Management Dashboard – Pro Edition

A **production-ready Flask web application** for managing students, courses, and users with authentication, role-based access control, profile picture uploads, and REST APIs.

---

## 🌐 Live Demo

👉 **https://student-management-dashboard-pro-edition.onrender.com**


---

## 📌 Project Overview

This project is a full-stack web application built using **Flask** that allows managing:

* 👤 Users (Admin, Instructor, Student)
* 🎓 Students
* 📘 Courses
* 🔗 Student–Course enrollments

It follows a **clean architecture (Routes → Services → Models)** and includes:

* Authentication system (Login / Register)
* Role-based access control
* REST APIs + HTML pages
* Search & pagination
* Profile picture upload
* Error handling (HTML + JSON)
* Automated testing with pytest

---

## 🚀 Features

* 🔐 Authentication (Flask-Login)
* 🧑‍💼 Role-based system:

  * Admin
  * Instructor
  * Student
* 🎓 Many-to-many relationship (Students ↔ Courses)
* 📸 Profile picture upload
* 🔍 Dynamic search (Fetch API)
* 📄 Pagination (UI + API)
* 🔗 Enrollment & unenrollment APIs
* ⚙️ Clean architecture (services layer)
* 🧪 Tested with pytest
* 🌱 Database seeding
* 🎨 Modern UI (Bootstrap + custom styles)

---
## 🔑 Demo Accounts

You can use the following accounts to test the application:

### 👨‍💼 Admin

* **Email:** `admin@gmail.com`
* **Password:** `Admin1234`

---

### 👨‍🏫 Instructor

You can register/login using an email ending with:

```text
@najah.edu
```

Example:

* `instructor1@najah.edu`

---

### 🎓 Student

You can register/login using an email ending with:

```text
@stu.najah.edu
```

Example:

* `s12110002@stu.najah.edu`

> ⚠️ The system automatically detects the role based on the email format.

---

## 🧠 Notes

* Roles are assigned automatically:

  * `@stu.najah.edu` → Student
  * `@najah.edu` → Instructor
* Admin is pre-seeded in the database during setup.
* If `SEED_DB=true`, demo users and data will be created automatically.

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/asmaahassoneh/Student-Management-Dashboard-Pro-Edition.git 
cd Student-Management-Dashboard-Pro-Edition
```

---

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate   
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Create `.env` file

```env
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///students.db
FLASK_ENV=development
SEED_DB=true
```

> The app loads environment variables using `python-dotenv` 

---

### 5. Run the application

```bash
python run.py
```

---

### 6. Run tests

```bash
python -m pytest
```

---

## 📁 Folder Structure

```
Student Management Dashboard - Pro Edition/
│
├── app/
│   ├── models/        # Database models
│   ├── routes/        # API + HTML routes
│   ├── services/      # Business logic layer
│   ├── templates/     # Jinja templates
│   ├── static/        # CSS, JS, uploads
│   ├── config.py      # App configuration
│   ├── extensions.py  # Flask extensions
│   └── __init__.py    # App factory
│
├── tests/             # Pytest tests
├── seed.py            # Seed database script
├── run.py             # App entry point
├── requirements.txt
└── README.md
```

---

## 🖼️ Screenshots

### 🔐 Authentication

#### Login

![Login](screenshots/login.png)

#### Register

![Register](screenshots/register.png)

#### After Logout

![Logout](screenshots/After%20Logout.png)

---

### 🏠 Home

#### Home Page (Before Login)

![Home](screenshots/Home%20Page%20befor%20login.png)

---

### 📊 Dashboard

#### Admin Dashboard

![Admin Dashboard](screenshots/Dashboard%20if%20admin.png)

#### Non-Admin Dashboard

![User Dashboard](screenshots/Dashboard%20if%20NOT%20admin.png)

---

### 🎓 Students Management

#### Students List

![Students List](screenshots/students%20list.png)

#### View Student Details

![Student Details](screenshots/view%20student%20details.png)

#### Edit Student Courses

![Edit Student](screenshots/Edit%20students%20courses.png)

#### Student View (Own Courses)

![Student View](screenshots/student%20login%20and%20see%20his%20own%20courses.png)

#### Access Restriction (Student Cannot Access Dashboard)

![Access Denied](screenshots/student%20cant%20access%20dashboard.png)

---

### 📘 Courses Management

#### Courses List

![Courses](screenshots/Courses.png)

#### Add Course

![Add Course](screenshots/Add%20course.png)

#### Edit Course

![Edit Course](screenshots/edit%20course.png)

#### Search Courses

![Search Courses](screenshots/Search%20Course%20By%20code.png)

---

### 👤 Users Management (Admin)

#### Users List

![Users](screenshots/users.png)

#### View User

![View User](screenshots/view%20user.png)

#### Edit User

![Edit User](screenshots/edit%20user.png)

#### Search Users by Role

![Search Users](screenshots/Search%20Users%20by%20role.png)

#### Access Restriction (Non-Admin)

![Restricted](screenshots/Access%20users%20NOT%20admin.png)

---

### ⚠️ Error Pages

#### Not Found (404)

![404](screenshots/Not%20Found.png)

---


## 🌐 API Reference

### 🎓 Students

| Method | Endpoint                      | Description      |
| ------ | ----------------------------- | ---------------- |
| GET    | `/api/students`               | List students    |
| POST   | `/api/students`               | Create student   |
| GET    | `/api/students/<id>`          | Get student      |
| PUT    | `/api/students/<id>`          | Update student   |
| DELETE | `/api/students/<id>`          | Delete student   |
| POST   | `/api/students/<id>/enroll`   | Enroll in course |
| POST   | `/api/students/<id>/unenroll` | Unenroll         |

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

## 🔐 Authentication & Authorization

* Uses **Flask-Login**
* All `/api/*` endpoints require login
* Role-based permissions:

  * Admin → full access
  * Instructor → manage students & courses
  * Student → limited access

---

## 🗃️ Database Design

Entities:

* **User**
* **Student**
* **Course**
* **Enrollment (many-to-many)**

✔ Unique constraint on `(student_id, course_id)`
✔ Cascading deletes supported 

---

## 📦 Response Format

### Success

```json
{
  "success": true,
  "data": {}
}
```

### Error

```json
{
  "success": false,
  "error": "Error message"
}
```

---

## 📸 Profile Upload

* Allowed formats: `png`, `jpg`, `jpeg`, `gif`
* Max size: **2MB**
* Stored in:

```
app/static/uploads
```

---

## 🌿 Git Workflow

| Branch    | Purpose     |
| --------- | ----------- |
| main      | Production  |
| dev       | Development |
| feature/* | Features    |

---

## 🧪 Testing

* Pytest used for:

  * API tests
  * Relationship tests
  * Validation tests

---

## 👩‍💻 Author

**Asmaa Hassoneh**
Computer Engineering Student
Full Stack Developer (Flask + React)

---

## 📄 License

This project is for educational purposes.

---
