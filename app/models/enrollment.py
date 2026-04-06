from datetime import datetime, UTC

from app.extensions import db


class Enrollment(db.Model):
    __tablename__ = "enrollments"
    __table_args__ = (
        db.UniqueConstraint(
            "student_id", "course_id", name="uq_enrollment_student_course"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    enrolled_at = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))

    student = db.relationship("Student", back_populates="enrollments")
    course = db.relationship("Course", back_populates="enrollments")

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "enrolled_at": self.enrolled_at.isoformat() if self.enrolled_at else None,
        }

    def __repr__(self):
        return f"<Enrollment student_id={self.student_id} course_id={self.course_id}>"
