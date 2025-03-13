# /backend/app/models/user.py

from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property

class User(db.Model):
    """User model for authentication and profile management"""
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    theme_preference = db.Column(db.String(20), default='light')
    profile_image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_teacher(self):
        return self.role == 'teacher'

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role,
            'theme_preference': self.theme_preference,
            'profile_image': self.profile_image,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'last_login': self.last_login,
            'is_active': self.is_active
        }

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.email}>'
