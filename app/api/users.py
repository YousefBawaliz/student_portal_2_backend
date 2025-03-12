from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.models.user import User
from app.schemas.user import UserSchema, UserCreateSchema, UserUpdateSchema, PaginationSchema
from app import db

blp = Blueprint("users", "users", description="Operations on users")

@blp.route("/me")
class CurrentUser(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self):
        """Get current user's profile"""
        user_id = int(get_jwt_identity())  # Convert string ID back to integer
        user = User.query.get_or_404(user_id)
        return user

    @jwt_required()
    @blp.arguments(UserUpdateSchema)
    @blp.response(200, UserSchema)
    def put(self, user_data):
        """Update current user's profile"""
        user_id = int(get_jwt_identity())  # Convert string ID back to integer
        user = User.query.get_or_404(user_id)

        try:
            allowed_fields = ['first_name', 'last_name', 'email', 'theme_preference', 'profile_image']
            for field in allowed_fields:
                if field in user_data:
                    setattr(user, field, user_data[field])
            
            if 'password' in user_data:
                user.set_password(user_data['password'])
            
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            abort(409, message="Email already exists")
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=str(e))

@blp.route("/")
class UserList(MethodView):
    @jwt_required()
    @blp.arguments(PaginationSchema, location="query")
    @blp.response(200, UserSchema(many=True))
    def get(self, pagination_args):
        """Get all users (admin only)"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))  # Convert string ID back to integer
        if not current_user.is_admin:
            abort(403, message="Admin access required")
        
        page = pagination_args.get('page', 1)
        per_page = pagination_args.get('per_page', 20)
        return User.query.paginate(page=page, per_page=per_page, error_out=False).items

    @jwt_required()
    @blp.arguments(UserCreateSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        """Create a new user (admin only)"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        if not current_user.is_admin():
            abort(403, message="Admin access required")

        try:
            user = User(
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data.get('role', 'student'),
                theme_preference=user_data.get('theme_preference', 'light')
            )
            # Use the password property setter instead of set_password
            user.password = user_data['password']
            
            db.session.add(user)
            db.session.commit()
            
            return user, 201
        except IntegrityError:
            db.session.rollback()
            abort(409, message="Email already exists")
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=str(e))

@blp.route("/<int:user_id>")
class UserView(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):
        """Get specific user"""
        current_user = User.query.get_or_404(get_jwt_identity())
        
        if not current_user.is_admin() and current_user.id != user_id:
            abort(403, message="Access denied")
        
        user = User.query.get_or_404(user_id)
        return user

    @jwt_required()
    @blp.arguments(UserUpdateSchema)
    @blp.response(200, UserSchema)
    def put(self, user_data, user_id):
        """Update specific user (admin only)"""
        current_user = User.query.get_or_404(get_jwt_identity())
        
        if not current_user.is_admin():
            abort(403, message="Admin access required")
        
        user = User.query.get_or_404(user_id)
        
        try:
            for field in ['first_name', 'last_name', 'email', 'role', 'theme_preference', 'profile_image']:
                if field in user_data:
                    setattr(user, field, user_data[field])
            
            if 'password' in user_data:
                user.password = user_data['password']
            
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            abort(400, message="Email already exists.")
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=str(e))

    @jwt_required()
    @blp.response(204)
    def delete(self, user_id):
        """Delete specific user (admin only)"""
        current_user = User.query.get_or_404(get_jwt_identity())
        
        if not current_user.is_admin():
            abort(403, message="Admin access required")
        
        user = User.query.get_or_404(user_id)
        
        try:
            db.session.delete(user)
            db.session.commit()
            return '', 204
        except SQLAlchemyError as e:
            db.session.rollback()
        return '', 204
