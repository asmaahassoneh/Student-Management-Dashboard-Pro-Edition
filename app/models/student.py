from app.extensions import db
from app.models.course import student_courses


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(20), nullable=False, unique=True, index=True)

    courses = db.relationship(
        "Course",
        secondary=student_courses,
        back_populates="students",
        lazy="subquery",
    )

    @property
    def courses_count(self):
        return len(self.courses)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "student_id": self.student_id,
            "courses": [course.to_dict() for course in self.courses],
            "courses_count": self.courses_count,
        }
