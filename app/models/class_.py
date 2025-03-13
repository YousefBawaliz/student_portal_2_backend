from app import db
from datetime import datetime

class Class(db.Model):
    __tablename__ = 'class'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    section_number = db.Column(db.String(10), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    teacher = db.relationship('User', backref='teaching_classes')
    enrollments = db.relationship('ClassEnrollment', backref='class_', lazy='dynamic')
    
    __table_args__ = (
        db.UniqueConstraint('course_id', 'section_number', 'semester', 'year', 
                           name='unique_class_section'),
    )