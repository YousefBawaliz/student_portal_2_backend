from app import db
from datetime import datetime

class Assessment(db.Model):
    __tablename__ = 'assessment'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # quiz, assignment, exam
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    class_ = db.relationship('Class', backref='assessments')
    creator = db.relationship('User', backref='created_assessments')
    scores = db.relationship('Score', backref='assessment', lazy='dynamic')

    __table_args__ = (
        db.CheckConstraint(
            type.in_(['quiz', 'assignment', 'exam']),
            name='valid_assessment_type'
        ),
    )