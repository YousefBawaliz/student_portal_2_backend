from app import db
from datetime import datetime

class Score(db.Model):
    __tablename__ = 'score'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    score_value = db.Column(db.Float, nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = db.relationship('User', backref='scores')

    __table_args__ = (
        db.UniqueConstraint('student_id', 'assessment_id', name='unique_student_assessment'),
    )