from marshmallow import Schema, fields, validate

class CourseSchema(Schema):
    id = fields.Int(dump_only=True)
    course_code = fields.Str(required=True, validate=validate.Length(min=2, max=20))
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str()
    teacher_id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    is_active = fields.Boolean()
    
    # Nested relationships
    teacher = fields.Nested('UserSchema', only=('id', 'first_name', 'last_name'))
    students = fields.Nested('UserSchema', many=True, only=('id', 'first_name', 'last_name'))

class CourseCreateSchema(Schema):
    course_code = fields.Str(required=True, validate=validate.Length(min=2, max=20))
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str()
    teacher_id = fields.Int()  # Optional, defaults to current user if not provided

class CourseUpdateSchema(Schema):
    title = fields.Str(validate=validate.Length(min=1, max=100))
    description = fields.Str()
    is_active = fields.Boolean()

class CourseEnrollmentSchema(Schema):
    id = fields.Int(dump_only=True)
    student_id = fields.Int(dump_only=True)
    course_id = fields.Int(dump_only=True)
    enrollment_date = fields.DateTime(dump_only=True)
    status = fields.Str(dump_only=True)
