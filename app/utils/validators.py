from marshmallow import ValidationError
from app.models.user import User

def validate_email(email):
    """
    Validate email uniqueness and format.
    
    Args:
        email (str): Email address to validate
    
    Raises:
        ValidationError: If email is already in use
    """
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        raise ValidationError('Email address is already in use.')