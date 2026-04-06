from app.extensions import db


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

    enrollments = db.relationship(
        "Enrollment",
        back_populates="course",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    students = db.relationship(
        "Student",
        secondary="enrollments",
        primaryjoin="Course.id == Enrollment.course_id",
        secondaryjoin="Student.id == Enrollment.student_id",
        viewonly=True,
        lazy="selectin",
        order_by="Student.name.asc()",
    )

    def to_dict(self, include_students=False):
        data = {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "students_count": len(self.students),
        }

        if include_students:
            data["students"] = [student.to_dict() for student in self.students]

        return data

    def __repr__(self):
        return f"<Course {self.code} - {self.name}>"
