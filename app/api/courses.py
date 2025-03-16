from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.models.course import Course
from app.models.user import User
from app.schemas.course import CourseSchema, CourseCreateSchema, CourseUpdateSchema
from app import db

blp = Blueprint("courses", "courses", description="Operations on courses")

@blp.route("/")
class CourseList(MethodView):
    @jwt_required()
    @blp.response(200, CourseSchema(many=True))
    def get(self):
        """Get all courses"""
        return Course.query.all()

    @jwt_required()
    @blp.arguments(CourseCreateSchema)
    @blp.response(201, CourseSchema)
    def post(self, course_data):
        """Create a new course (admin only)"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        
        if not current_user.is_admin():
            abort(403, message="Admin access required")

        course = Course(**course_data)
        
        try:
            db.session.add(course)
            db.session.commit()
            return course, 201
        except IntegrityError:
            db.session.rollback()
            abort(409, message="Course with this code already exists")
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=str(e))

@blp.route("/<int:course_id>")
class CourseView(MethodView):
    @jwt_required()
    @blp.response(200, CourseSchema)
    def get(self, course_id):
        """Get course details"""
        return Course.query.get_or_404(course_id)

    @jwt_required()
    @blp.arguments(CourseUpdateSchema)
    @blp.response(200, CourseSchema)
    def put(self, course_data, course_id):
        """Update course details (admin only)"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        if not current_user.is_admin():
            abort(403, message="Admin access required")

        course = Course.query.get_or_404(course_id)
        
        for key, value in course_data.items():
            setattr(course, key, value)
            
        try:
            db.session.commit()
            return course
        except IntegrityError:
            db.session.rollback()
            abort(409, message="Course with this code already exists")
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=str(e))

    @jwt_required()
    def delete(self, course_id):
        """Delete a course (admin only)"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        if not current_user.is_admin():
            abort(403, message="Admin access required")

        course = Course.query.get_or_404(course_id)
        try:
            db.session.delete(course)
            db.session.commit()
            return {"message": "Course deleted successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=str(e))


