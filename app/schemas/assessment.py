from marshmallow import Schema, fields, validate
from datetime import datetime

class AssessmentSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    type = fields.Str(required=True, validate=validate.OneOf(['quiz', 'assignment', 'exam']))
    class_id = fields.Int(required=True)
    date = fields.DateTime(required=True)
    description = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    created_by = fields.Int(dump_only=True)

    # Nested relationships
    class_ = fields.Nested('ClassSchema', only=('id', 'section_number', 'course'))
    creator = fields.Nested('UserSchema', only=('id', 'first_name', 'last_name'))

class AssessmentCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    type = fields.Str(required=True, validate=validate.OneOf(['quiz', 'assignment', 'exam']))
    class_id = fields.Int(required=True)
    date = fields.DateTime(required=True)
    description = fields.Str()

class AssessmentUpdateSchema(Schema):
    title = fields.Str(validate=validate.Length(min=1, max=100))
    type = fields.Str(validate=validate.OneOf(['quiz', 'assignment', 'exam']))
    date = fields.DateTime()
    description = fields.Str()

class ScoreSchema(Schema):
    id = fields.Int(dump_only=True)
    student_id = fields.Int(required=True)
    assessment_id = fields.Int(required=True)
    score_value = fields.Float(required=True)
    submission_date = fields.DateTime(dump_only=True)
    feedback = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Nested relationships
    student = fields.Nested('UserSchema', only=('id', 'first_name', 'last_name'))
    assessment = fields.Nested('AssessmentSchema', only=('id', 'title', 'type'))

class ScoreUpdateSchema(Schema):
    score_value = fields.Float()
    feedback = fields.Str()
