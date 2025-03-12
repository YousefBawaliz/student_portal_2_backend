from functools import wraps
from flask_jwt_extended import get_jwt_identity
from app.models.user import User
from app.utils.error_handlers import forbidden

def admin_required(f):
    """Decorator to require admin role for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user or not current_user.is_admin():
            return forbidden()
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    """Decorator to require teacher role for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user or not current_user.is_teacher():
            return forbidden()
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Helper function to get current user from JWT identity."""
    current_user_id = get_jwt_identity()
    return User.query.get(current_user_id) if current_user_id else None