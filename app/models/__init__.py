# /backend/app/models/__init__.py

# Import database instance
from app import db

# Import models to make them available when importing the package
from app.models.user import User
from app.models.course import Course
from app.models.class_ import Class
from app.models.class_enrollment import ClassEnrollment
# from app.models.module import Module
# from app.models.content import Content
# from app.models.announcement import Announcement
# from app.models.calendar_event import CalendarEvent

