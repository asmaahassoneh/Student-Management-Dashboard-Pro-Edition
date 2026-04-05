from app.extensions import db

student_courses = db.Table(
    "student_courses",
    db.Column(
        "student_id",
        db.Integer,
        db.ForeignKey("students.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "course_id",
        db.Integer,
        db.ForeignKey("courses.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

    students = db.relationship(
        "Student",
        secondary=student_courses,
        back_populates="courses",
        lazy="subquery",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "students_count": len(self.students),
        }

    def __repr__(self):
        return f"<Course {self.code} - {self.name}>"
