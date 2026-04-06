from app.extensions import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(20), nullable=False, unique=True, index=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
    )

    user = db.relationship("User", backref=db.backref("student_profile", uselist=False))

    enrollments = db.relationship(
        "Enrollment",
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    courses = db.relationship(
        "Course",
        secondary="enrollments",
        primaryjoin="Student.id == Enrollment.student_id",
        secondaryjoin="Course.id == Enrollment.course_id",
        viewonly=True,
        lazy="selectin",
        order_by="Course.name.asc()",
    )

    @property
    def courses_count(self):
        return len(self.courses)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "student_id": self.student_id,
            "user_id": self.user_id,
            "courses": [course.to_dict() for course in self.courses],
            "courses_count": self.courses_count,
        }

    def __repr__(self):
        return f"<Student {self.student_id} - {self.name}>"
