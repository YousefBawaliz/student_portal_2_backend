from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.models.assessment import Assessment
from app.models.score import Score
from app.models.user import User
from app.models.class_ import Class
from app.schemas.assessment import (AssessmentSchema, AssessmentCreateSchema, 
                                  AssessmentUpdateSchema, ScoreSchema)
from app import db

blp = Blueprint("assessments", "assessments", description="Operations on assessments")

@blp.route("/")
class AssessmentList(MethodView):
    @jwt_required()
    @blp.response(200, AssessmentSchema(many=True))
    def get(self):
        """Get all assessments (filtered by role)"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        
        if current_user.is_admin():
            return Assessment.query.all()
        elif current_user.role == 'teacher':
            return Assessment.query.join(Assessment.class_)\
                .filter_by(teacher_id=current_user.id).all()
        else:
            return Assessment.query.join(Assessment.class_)\
                .join(Class.enrollments)\
                .filter_by(student_id=current_user.id).all()

    @jwt_required()
    @blp.arguments(AssessmentCreateSchema)
    @blp.response(201, AssessmentSchema)
    def post(self, assessment_data):
        """Create a new assessment (teacher only)"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        
        if current_user.role not in ['teacher', 'admin']:
            abort(403, message="Only teachers can create assessments")

        # Verify the teacher is assigned to this class
        class_ = Class.query.get_or_404(assessment_data['class_id'])
        if current_user.role == 'teacher' and class_.teacher_id != current_user.id:
            abort(403, message="You can only create assessments for your classes")

        assessment = Assessment(
            **assessment_data,
            created_by=current_user.id
        )
        
        try:
            db.session.add(assessment)
            db.session.commit()
            return assessment
        except SQLAlchemyError:
            abort(500, message="Error creating assessment")

@blp.route("/<int:assessment_id>")
class AssessmentView(MethodView):
    @jwt_required()
    @blp.response(200, AssessmentSchema)
    def get(self, assessment_id):
        """Get a specific assessment"""
        assessment = Assessment.query.get_or_404(assessment_id)
        return assessment

    @jwt_required()
    @blp.arguments(AssessmentUpdateSchema)
    @blp.response(200, AssessmentSchema)
    def put(self, assessment_data, assessment_id):
        """Update an assessment (teacher only)"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        assessment = Assessment.query.get_or_404(assessment_id)

        if current_user.role == 'teacher' and assessment.class_.teacher_id != current_user.id:
            abort(403, message="You can only update your own assessments")
        elif current_user.role == 'student':
            abort(403, message="Students cannot update assessments")

        for key, value in assessment_data.items():
            setattr(assessment, key, value)

        try:
            db.session.commit()
            return assessment
        except SQLAlchemyError:
            abort(500, message="Error updating assessment")

    @jwt_required()
    def delete(self, assessment_id):
        """Delete an assessment (teacher only)"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        assessment = Assessment.query.get_or_404(assessment_id)

        if current_user.role == 'teacher' and assessment.class_.teacher_id != current_user.id:
            abort(403, message="You can only delete your own assessments")
        elif current_user.role == 'student':
            abort(403, message="Students cannot delete assessments")

        try:
            db.session.delete(assessment)
            db.session.commit()
            return {"message": "Assessment deleted"}
        except SQLAlchemyError:
            abort(500, message="Error deleting assessment")

@blp.route("/<int:assessment_id>/scores")
class AssessmentScores(MethodView):
    @jwt_required()
    @blp.response(200, ScoreSchema(many=True))
    def get(self, assessment_id):
        """Get all scores for an assessment"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        assessment = Assessment.query.get_or_404(assessment_id)

        if current_user.role == 'student':
            return Score.query.filter_by(
                assessment_id=assessment_id,
                student_id=current_user.id
            ).all()
        elif current_user.role == 'teacher' and assessment.class_.teacher_id != current_user.id:
            abort(403, message="You can only view scores for your classes")
        
        return Score.query.filter_by(assessment_id=assessment_id).all()

@blp.route("/<int:assessment_id>/completion-stats")
class AssessmentCompletionStats(MethodView):
    @jwt_required()
    def get(self, assessment_id):
        """Get completion statistics for an assessment"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        assessment = Assessment.query.get_or_404(assessment_id)

        # Verify permissions
        if current_user.role == 'teacher' and assessment.class_.teacher_id != current_user.id:
            abort(403, message="You can only view stats for your classes")
        elif current_user.role == 'student':
            abort(403, message="Students cannot view completion stats")

        # Get total number of students enrolled in the class
        total_students = db.session.query(db.func.count(Class.enrollments))\
            .filter(Class.id == assessment.class_id)\
            .scalar()

        # Get number of students who have submitted (have scores)
        completed_count = Score.query\
            .filter_by(assessment_id=assessment_id)\
            .count()

        # Calculate completion rate
        completion_rate = (completed_count / total_students * 100) if total_students > 0 else 0

        return {
            "total_students": total_students,
            "completed_count": completed_count,
            "pending_count": total_students - completed_count,
            "completion_rate": round(completion_rate, 2),
            "assessment_id": assessment_id,
            "assessment_title": assessment.title,
            "class_id": assessment.class_id,
            "due_date": assessment.date.isoformat()
        }
