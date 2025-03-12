from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.models.course import Course
from app.models.user import User
from app.models.course_enrollment import CourseEnrollment
from app.schemas.course import CourseSchema, CourseCreateSchema, CourseUpdateSchema
from app import db

blp = Blueprint("courses", "courses", description="Operations on courses")

@blp.route("/")
class CourseList(MethodView):
    @jwt_required()
    @blp.response(200, CourseSchema(many=True))
    def get(self):
        """Get all courses (filtered by role)"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        
        if current_user.is_admin():
            return Course.query.all()
        elif current_user.role == 'teacher':
            return Course.query.filter_by(teacher_id=current_user.id).all()
        else:
            return current_user.courses_enrolled

    @jwt_required()
    @blp.arguments(CourseCreateSchema)
    @blp.response(201, CourseSchema)
    def post(self, course_data):
        """Create a new course (teachers and admins only)"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        
        if not current_user.is_admin():
            abort(403, message="Only admins can create courses")

        # Verify teacher exists
        teacher_id = course_data.get('teacher_id', current_user.id)
        teacher = User.query.get_or_404(teacher_id)
        if teacher.role != 'teacher':
            abort(400, message="Assigned user must be a teacher")

        course = Course(
            course_code=course_data['course_code'],
            title=course_data['title'],
            description=course_data.get('description', ''),
            teacher_id=teacher_id
        )
        
        try:
            db.session.add(course)
            db.session.commit()
            return course
        except IntegrityError:
            abort(409, message="Course code already exists")

@blp.route("/<int:course_id>")
class CourseView(MethodView):
    @jwt_required()
    @blp.response(200, CourseSchema)
    def get(self, course_id):
        """Get course details"""
        course = Course.query.get_or_404(course_id)
        return course

    @jwt_required()
    @blp.arguments(CourseUpdateSchema)
    @blp.response(200, CourseSchema)
    def put(self, course_data, course_id):
        """Update course details (teacher of course or admin only)"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        course = Course.query.get_or_404(course_id)
        
        if not (current_user.is_admin() or course.teacher_id == current_user.id):
            abort(403, message="Not authorized to update this course")

        try:
            for field in ['title', 'description', 'is_active']:
                if field in course_data:
                    setattr(course, field, course_data[field])
            
            db.session.commit()
            return course
        except SQLAlchemyError as e:
            abort(500, message=str(e))

    @jwt_required()
    def delete(self, course_id):
        """Delete a course (admin only)"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        if not current_user.is_admin():
            abort(403, message="Admin access required")

        course = Course.query.get_or_404(course_id)
        db.session.delete(course)
        db.session.commit()
        return {"message": "Course deleted"}

@blp.route("/<int:course_id>/enroll")
class CourseEnrollmentView(MethodView):
    @jwt_required()
    def post(self, course_id):
        """Enroll in a course"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        course = Course.query.get_or_404(course_id)
        
        if current_user.role != 'student':
            abort(403, message="Only students can enroll in courses")
            
        try:
            enrollment = CourseEnrollment(
                student_id=current_user.id,
                course_id=course_id
            )
            db.session.add(enrollment)
            db.session.commit()
            return {"message": "Successfully enrolled"}, 201
        except IntegrityError:
            abort(409, message="Already enrolled in this course")

    @jwt_required()
    def delete(self, course_id):
        """Unenroll from a course"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        enrollment = CourseEnrollment.query.filter_by(
            student_id=current_user.id,
            course_id=course_id
        ).first_or_404()
        
        db.session.delete(enrollment)
        db.session.commit()
        return {"message": "Successfully unenrolled"}
