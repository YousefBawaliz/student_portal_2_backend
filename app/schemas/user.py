from marshmallow import Schema, fields, validate

VALID_ROLES = ['admin', 'teacher', 'student']

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    role = fields.Str(validate=validate.OneOf(VALID_ROLES), load_default='student')
    theme_preference = fields.Str(validate=validate.OneOf(['light', 'dark']), load_default='light')
    profile_image = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class UserCreateSchema(Schema):
    """Schema for creating a new user"""
    email = fields.Email(required=True, description="User's email address")
    password = fields.Str(required=True, load_only=True,
                         validate=validate.Length(min=6),
                         description="User's password (min 6 characters)")
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    role = fields.Str(validate=validate.OneOf(VALID_ROLES), load_default='student')
    theme_preference = fields.Str(validate=validate.OneOf(['light', 'dark']), load_default='light')
    profile_image = fields.Str(required=False)

class UserUpdateSchema(Schema):
    """Schema for updating an existing user"""
    email = fields.Email()
    password = fields.Str(load_only=True, validate=validate.Length(min=6))
    first_name = fields.Str(validate=validate.Length(min=1, max=50))
    last_name = fields.Str(validate=validate.Length(min=1, max=50))
    role = fields.Str(validate=validate.OneOf(VALID_ROLES))
    theme_preference = fields.Str(validate=validate.OneOf(['light', 'dark']))
    profile_image = fields.Str()

class PaginationSchema(Schema):
    """Schema for pagination parameters"""
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(missing=20, validate=validate.Range(min=1, max=100))

class AuthSchema(Schema):
    """Schema for login credentials"""
    email = fields.Email(required=True, description="User's email address")
    password = fields.Str(required=True, load_only=True, 
                         validate=validate.Length(min=6),
                         description="User's password (min 6 characters)")

class TokenResponseSchema(Schema):
    """Schema for token response"""
    access_token = fields.Str(required=True, description="JWT access token")
    refresh_token = fields.Str(required=True, description="JWT refresh token")
    user = fields.Nested(UserSchema, description="User information")
