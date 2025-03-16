from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.models.score import Score
from app.models.user import User
from app.models.assessment import Assessment
from app.schemas.assessment import ScoreSchema, ScoreUpdateSchema
from app import db

blp = Blueprint("scores", "scores", description="Operations on scores")

@blp.route("/")
class ScoreList(MethodView):
    @jwt_required()
    @blp.arguments(ScoreSchema)
    @blp.response(201, ScoreSchema)
    def post(self, score_data):
        """Create a new score (teacher only)"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        assessment = Assessment.query.get_or_404(score_data['assessment_id'])
        
        if current_user.role not in ['teacher', 'admin']:
            abort(403, message="Only teachers can create scores")
            
        if current_user.role == 'teacher' and assessment.class_.teacher_id != current_user.id:
            abort(403, message="You can only create scores for your classes")

        score = Score(
            student_id=score_data['student_id'],
            assessment_id=score_data['assessment_id'],
            score_value=score_data['score_value'],
            feedback=score_data.get('feedback')
        )
        
        try:
            db.session.add(score)
            db.session.commit()
            return score
        except IntegrityError:
            abort(409, message="Score already exists for this student and assessment")
        except SQLAlchemyError:
            abort(500, message="Error creating score")

@blp.route("/<int:score_id>")
class ScoreView(MethodView):
    @jwt_required()
    @blp.response(200, ScoreSchema)
    def get(self, score_id):
        """Get a specific score"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        score = Score.query.get_or_404(score_id)
        
        if current_user.role == 'student' and score.student_id != current_user.id:
            abort(403, message="You can only view your own scores")
        elif current_user.role == 'teacher' and score.assessment.class_.teacher_id != current_user.id:
            abort(403, message="You can only view scores for your classes")
            
        return score

    @jwt_required()
    @blp.arguments(ScoreUpdateSchema)  # Changed from ScoreSchema to ScoreUpdateSchema
    @blp.response(200, ScoreSchema)
    def put(self, score_data, score_id):
        """Update a score (teacher only)"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        score = Score.query.get_or_404(score_id)
        
        if current_user.role not in ['teacher', 'admin']:
            abort(403, message="Only teachers can update scores")
            
        if current_user.role == 'teacher' and score.assessment.class_.teacher_id != current_user.id:
            abort(403, message="You can only update scores for your classes")

        for key, value in score_data.items():
            setattr(score, key, value)

        try:
            db.session.commit()
            return score
        except SQLAlchemyError:
            abort(500, message="Error updating score")

    @jwt_required()
    def delete(self, score_id):
        """Delete a score (teacher only)"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        score = Score.query.get_or_404(score_id)
        
        if current_user.role not in ['teacher', 'admin']:
            abort(403, message="Only teachers can delete scores")
            
        if current_user.role == 'teacher' and score.assessment.class_.teacher_id != current_user.id:
            abort(403, message="You can only delete scores for your classes")

        try:
            db.session.delete(score)
            db.session.commit()
            return {"message": "Score deleted"}
        except SQLAlchemyError:
            abort(500, message="Error deleting score")

@blp.route("/student/<int:student_id>")
class StudentScores(MethodView):
    @jwt_required()
    @blp.response(200, ScoreSchema(many=True))
    def get(self, student_id):
        """Get all scores for a student"""
        current_user = User.query.get_or_404(int(get_jwt_identity()))
        
        if current_user.role == 'student' and current_user.id != student_id:
            abort(403, message="You can only view your own scores")
            
        if current_user.role == 'teacher':
            # Teachers can only view scores for students in their classes
            return Score.query.join(Score.assessment)\
                .join(Assessment.class_)\
                .filter(Score.student_id == student_id)\
                .filter_by(teacher_id=current_user.id)\
                .all()
                
        return Score.query.filter_by(student_id=student_id).all()

@blp.route("/student/<int:student_id>/assessment")
class StudentAssessmentScore(MethodView):
    @jwt_required()
    @blp.response(200, ScoreSchema)
    def get(self, student_id):
        """Get a student's score by assessment title"""
        assessment_title = request.args.get('title')
        if not assessment_title:
            abort(400, message="Assessment title is required")

        current_user = User.query.get_or_404(int(get_jwt_identity()))
        
        # Check permissions
        if current_user.role == 'student' and current_user.id != student_id:
            abort(403, message="You can only view your own scores")

        # Query the score joining with assessment to filter by title
        score = Score.query\
            .join(Score.assessment)\
            .filter(
                Score.student_id == student_id,
                Assessment.title == assessment_title
            ).first()
            
        if not score:
            abort(404, message="Score not found for this assessment")

        # For teachers, verify they teach this class
        if current_user.role == 'teacher' and \
           score.assessment.class_.teacher_id != current_user.id:
            abort(403, message="You can only view scores for your classes")

        return score
