from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.student import Student
from app.models.course import Course
from app.utils.role_helpers import extract_student_id


def seed():
    print("🌱 Seeding database...")

    admin = User.query.filter(
        (User.email == "admin@gmail.com") | (User.username == "admin")
    ).first()

    if not admin:
        admin = User(
            username="admin",
            email="admin@gmail.com",
            role=User.ROLE_ADMIN,
            profile_picture="admin.png",
        )
        admin.set_password("Admin1234")
        db.session.add(admin)
        print("✅ Admin created")
    else:
        admin.email = "admin@gmail.com"
        admin.role = User.ROLE_ADMIN
        admin.profile_picture = "admin.png"
        print("ℹ️ Admin already exists -> updated")

    instructor = User.query.filter(
        (User.email == "instructor1@najah.edu") | (User.username == "instructor1")
    ).first()

    if not instructor:
        instructor = User(
            username="instructor1",
            email="instructor1@najah.edu",
            role=User.ROLE_INSTRUCTOR,
            profile_picture="instructor.jpg",
        )
        instructor.set_password("Instructor123")
        db.session.add(instructor)
        print("✅ Instructor created")
    else:
        instructor.email = "instructor1@najah.edu"
        instructor.role = User.ROLE_INSTRUCTOR
        instructor.profile_picture = "instructor.jpg"
        print("ℹ️ Instructor already exists -> updated")

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
            course.name = c["name"]
            course.description = c["description"]
            print(f"ℹ️ Course exists: {c['name']} -> updated")
        courses.append(course)

    db.session.commit()

    students_data = [
        {
            "name": "Ali Ahmad",
            "username": "ali",
            "email": "s12110002@stu.najah.edu",
            "password": "Ali12345",
            "profile_picture": "ali.jpg",
        },
        {
            "name": "Sara Khaled",
            "username": "sara",
            "email": "s12110003@stu.najah.edu",
            "password": "Sara12345",
            "profile_picture": "sara.webp",
        },
    ]

    for s in students_data:
        student_id = extract_student_id(s["email"])

        if not student_id:
            print(f"❌ Invalid student email: {s['email']}")
            continue

        user = User.query.filter(
            (User.email == s["email"]) | (User.username == s["username"])
        ).first()

        if not user:
            user = User(
                username=s["username"],
                email=s["email"],
                role=User.ROLE_STUDENT,
                profile_picture=s["profile_picture"],
            )
            user.set_password(s["password"])
            db.session.add(user)
            db.session.flush()
            print(f"✅ Student user created: {s['name']}")
        else:
            user.email = s["email"]
            user.username = s["username"]
            user.role = User.ROLE_STUDENT
            user.profile_picture = s["profile_picture"]
            print(f"ℹ️ Student user exists: {s['name']} -> updated")

        student = Student.query.filter_by(student_id=student_id).first()

        if not student:
            student = Student(
                name=s["name"],
                student_id=student_id,
                user_id=user.id,
            )
            db.session.add(student)
            print(f"✅ Student profile created: {s['name']}")
        else:
            student.name = s["name"]
            student.user_id = user.id
            print(f"ℹ️ Student profile exists: {s['name']} -> updated")

        student.courses = courses[:2]

    db.session.commit()
    print("🎉 Seeding completed successfully!")


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        db.create_all()
