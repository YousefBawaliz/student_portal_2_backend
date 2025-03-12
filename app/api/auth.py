from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from app.models.user import User
from app.schemas.user import AuthSchema, TokenResponseSchema, UserSchema
from flask import current_app

blp = Blueprint("auth", "auth", description="Authentication operations")

@blp.route("/login")
class Login(MethodView):
    @blp.arguments(AuthSchema)
    @blp.response(200, TokenResponseSchema)
    def post(self, auth_data):
        """User Login"""
        user = User.query.filter_by(email=auth_data['email']).first()
        
        if user and user.verify_password(auth_data['password']):
            # Convert user.id to string when creating tokens
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user
            }
        
        abort(401, message="Invalid email or password")

@blp.route('/refresh')
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    @blp.response(200, TokenResponseSchema(only=('access_token',)))
    def post(self):
        """Refresh access token"""
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        
        return {'access_token': access_token}

@blp.route('/logout')
class Logout(MethodView):
    @jwt_required()
    @blp.response(200)
    def post(self):
        """Logout user"""
        jti = get_jwt()["jti"]
        # TODO: Implement token blacklisting with Redis
        return {"message": "Successfully logged out"}

@blp.route('/auth/me')
class UserInfo(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    @blp.doc(description="Get current user information")
    def get(self):
        """Get current user info
        
        Returns the current user's information based on JWT token
        ---
        responses:
          200:
            description: User information retrieved successfully
          401:
            description: Invalid or missing token
          404:
            description: User not found
        """
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        return user
