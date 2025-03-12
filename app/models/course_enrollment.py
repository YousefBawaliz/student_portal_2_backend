from app import db
from datetime import datetime

class CourseEnrollment(db.Model):
    __tablename__ = 'course_enrollment'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, completed, dropped

    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', name='unique_enrollment'),
    )