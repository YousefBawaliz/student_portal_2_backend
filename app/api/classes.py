from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.models.class_ import Class
from app.models.class_enrollment import ClassEnrollment
from app.models.user import User
from app.schemas.class_ import (ClassSchema, ClassCreateSchema, 
                              ClassUpdateSchema, ClassEnrollmentSchema)
from app import db

blp = Blueprint("classes", "classes", description="Operations on classes")

@blp.route("/")
class ClassList(MethodView):
    @jwt_required()
    @blp.response(200, ClassSchema(many=True))
    def get(self):
        """Get all classes (filtered by role)"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        
        if current_user.is_admin():
            return Class.query.all()
        elif current_user.role == 'teacher':
            return Class.query.filter_by(teacher_id=current_user.id).all()
        else:
            return Class.query.join(Class.enrollments)\
                .filter_by(student_id=current_user.id).all()

    @jwt_required()
    @blp.arguments(ClassCreateSchema)
    @blp.response(201, ClassSchema)
    def post(self, class_data):
        """Create a new class (admin only)"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        
        if not current_user.is_admin():
            abort(403, message="Only admins can create classes")

        class_ = Class(**class_data)
        
        try:
            db.session.add(class_)
            db.session.commit()
            return class_
        except IntegrityError:
            abort(409, message="Class with these details already exists")

@blp.route("/<int:class_id>")
class ClassView(MethodView):
    @jwt_required()
    @blp.response(200, ClassSchema)
    def get(self, class_id):
        """Get class details"""
        class_ = Class.query.get_or_404(class_id)
        return class_

    @jwt_required()
    @blp.arguments(ClassUpdateSchema)
    @blp.response(200, ClassSchema)
    def put(self, class_data, class_id):
        """Update class details (admin only)"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        if not current_user.is_admin():
            abort(403, message="Only admins can update classes")

        class_ = Class.query.get_or_404(class_id)

        try:
            for field, value in class_data.items():
                setattr(class_, field, value)
            db.session.commit()
            return class_
        except SQLAlchemyError as e:
            abort(500, message=str(e))

@blp.route("/<int:class_id>/enroll")
class ClassEnrollmentView(MethodView):
    @jwt_required()
    @blp.response(201, ClassEnrollmentSchema)
    def post(self, class_id):
        """Enroll in a class"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        
        if current_user.role != 'student':
            abort(403, message="Only students can enroll in classes")
            
        try:
            enrollment = ClassEnrollment(
                student_id=current_user.id,
                class_id=class_id,
                status='active'
            )
            db.session.add(enrollment)
            db.session.commit()
            return enrollment
        except IntegrityError:
            abort(409, message="Already enrolled in this class")

    @jwt_required()
    def delete(self, class_id):
        """Unenroll from a class"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        enrollment = ClassEnrollment.query.filter_by(
            student_id=current_user.id,
            class_id=class_id
        ).first_or_404()
        
        db.session.delete(enrollment)
        db.session.commit()
        return {"message": "Successfully unenrolled"}