from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.student import Student
from app.models.course import Course


def extract_student_id(email):
    """
    Extract student_id from email:
    s12112458@stu.najah.edu -> 12112458
    """
    email = email.strip().lower()

    if not email.endswith("@stu.najah.edu"):
        return None

    local_part = email.split("@")[0]

    if not local_part.startswith("s") or not local_part[1:].isdigit():
        return None

    return local_part[1:]


def seed():
    print("🌱 Seeding database...")

    admin_email = "admin@najah.edu"
    admin = User.query.filter_by(email=admin_email).first()

    if not admin:
        admin = User(
            username="admin",
            email=admin_email,
            role=User.ROLE_ADMIN,
        )
        admin.set_password("Admin1234")
        db.session.add(admin)
        print("✅ Admin created")
    else:
        print("ℹ️ Admin already exists")

    instructor_email = "instructor1@najah.edu"
    instructor = User.query.filter_by(email=instructor_email).first()

    if not instructor:
        instructor = User(
            username="instructor1",
            email=instructor_email,
            role=User.ROLE_INSTRUCTOR,
        )
        instructor.set_password("Instructor123")
        db.session.add(instructor)
        print("✅ Instructor created")
    else:
        print("ℹ️ Instructor already exists")

    db.session.commit()

    courses_data = [
        {"name": "Data Structures", "code": "CSE201", "description": "Learn DS"},
        {"name": "Algorithms", "code": "CSE301", "description": "Learn Algorithms"},
        {"name": "Databases", "code": "CSE302", "description": "Learn DB"},
        {"name": "Operating Systems", "code": "CSE303", "description": "Learn OS"},
    ]

    courses = []
    for c in courses_data:
        course = Course.query.filter_by(code=c["code"]).first()
        if not course:
            course = Course(**c)
            db.session.add(course)
            print(f"✅ Course created: {c['name']}")
        else:
            print(f"ℹ️ Course exists: {c['name']}")
        courses.append(course)

    db.session.commit()

    students_data = [
        {
            "name": "Asmaa Hassoneh",
            "username": "asmaa",
            "email": "s12110001@stu.najah.edu",
            "password": "Asmaa1234",
        },
        {
            "name": "Ali Ahmad",
            "username": "ali",
            "email": "s12110002@stu.najah.edu",
            "password": "Ali12345",
        },
        {
            "name": "Sara Khaled",
            "username": "sara",
            "email": "s12110003@stu.najah.edu",
            "password": "Sara12345",
        },
    ]

    for s in students_data:
        existing_user = User.query.filter_by(email=s["email"]).first()

        if existing_user:
            print(f"ℹ️ Student user exists: {s['name']}")
            continue

        student_id = extract_student_id(s["email"])

        if not student_id:
            print(f"❌ Invalid student email: {s['email']}")
            continue

        user = User(
            username=s["username"],
            email=s["email"],
            role=User.ROLE_STUDENT,
        )
        user.set_password(s["password"])

        db.session.add(user)
        db.session.flush()

        student = Student(
            name=s["name"],
            student_id=student_id,
            user_id=user.id,
        )

        student.courses = courses[:2]

        db.session.add(student)

        print(f"✅ Student created: {s['name']}")

    db.session.commit()

    print("🎉 Seeding completed successfully!")


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        db.create_all()
        seed()
