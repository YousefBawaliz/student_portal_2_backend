from marshmallow import Schema, fields, validate

class ClassSchema(Schema):
    id = fields.Int(dump_only=True)
    course_id = fields.Int(required=True)
    teacher_id = fields.Int(required=True)
    section_number = fields.Str(required=True, validate=validate.Length(min=1, max=10))
    semester = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    year = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Nested relationships
    teacher = fields.Nested('UserSchema', only=('id', 'first_name', 'last_name'))
    course = fields.Nested('CourseSchema', only=('id', 'course_code', 'title'))

class ClassCreateSchema(Schema):
    course_id = fields.Int(required=True)
    teacher_id = fields.Int(required=True)
    section_number = fields.Str(required=True, validate=validate.Length(min=1, max=10))
    semester = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    year = fields.Int(required=True)

class ClassUpdateSchema(Schema):
    teacher_id = fields.Int()
    section_number = fields.Str(validate=validate.Length(min=1, max=10))
    semester = fields.Str(validate=validate.Length(min=1, max=20))
    year = fields.Int()

class ClassEnrollmentSchema(Schema):
    id = fields.Int(dump_only=True)
    student_id = fields.Int(dump_only=True)
    class_id = fields.Int(required=True)
    enrollment_date = fields.DateTime(dump_only=True)
    status = fields.Str(dump_only=True)
    
    # Nested relationships
    student = fields.Nested('UserSchema', only=('id', 'first_name', 'last_name'))
    class_ = fields.Nested('ClassSchema', only=('id', 'section_number', 'course'))