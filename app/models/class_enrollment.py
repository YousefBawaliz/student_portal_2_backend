from app import db
from datetime import datetime

class ClassEnrollment(db.Model):
    __tablename__ = 'class_enrollment'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, dropped, completed

    # Relationships
    student = db.relationship('User', backref='class_enrollments')
    
    __table_args__ = (
        db.UniqueConstraint('student_id', 'class_id', name='unique_class_enrollment'),
    )