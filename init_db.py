from app import create_app, db
from app.models.user import User
from app.models.course import Course
from app.models.class_ import Class
from app.models.class_enrollment import ClassEnrollment
from app.models.assessment import Assessment
from app.models.score import Score
from datetime import datetime, timedelta

def init_database():
    app = create_app('development')
    with app.app_context():
        # Drop all tables
        print("Dropping all tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating all tables...")
        db.create_all()
        
        # Create users
        print("Creating users...")
        admin = User(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            role='admin',
            theme_preference='light'
        )
        admin.password = 'admin123'
        
        teacher = User(
            email='teacher@example.com',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            theme_preference='light'
        )
        teacher.password = 'teacher123'
        
        student = User(
            email='student@example.com',
            first_name='Test',
            last_name='Student',
            role='student',
            theme_preference='light'
        )
        student.password = 'student123'
        
        # Add users to database
        db.session.add_all([admin, teacher, student])
        db.session.commit()
        
        # Create test courses
        print("Creating test courses...")
        course1 = Course(
            course_code="CS101",
            title="Introduction to Computer Science",
            description="Fundamental concepts of programming"
        )
        
        course2 = Course(
            course_code="CS102",
            title="Data Structures",
            description="Basic data structures and algorithms"
        )
        
        db.session.add_all([course1, course2])
        db.session.commit()
        
        # Create test classes
        print("Creating test classes...")
        class1 = Class(
            course_id=course1.id,
            teacher_id=teacher.id,
            section_number="A101",
            semester="Fall",
            year=2024
        )
        
        class2 = Class(
            course_id=course2.id,
            teacher_id=teacher.id,
            section_number="B201",
            semester="Fall",
            year=2024
        )
        
        db.session.add_all([class1, class2])
        db.session.commit()
        
        # Create class enrollments
        print("Creating test enrollments...")
        enrollment1 = ClassEnrollment(
            student_id=student.id,
            class_id=class1.id,
            status='active'
        )
        
        enrollment2 = ClassEnrollment(
            student_id=student.id,
            class_id=class2.id,
            status='active'
        )
        
        db.session.add_all([enrollment1, enrollment2])
        db.session.commit()

        # Create test assessments
        print("Creating test assessments...")
        assessment1 = Assessment(
            title="Midterm Exam",
            type="exam",
            class_id=class1.id,
            date=datetime.now() + timedelta(days=7),
            created_by=teacher.id,
            description="Midterm examination covering chapters 1-5"
        )

        assessment2 = Assessment(
            title="Quiz 1",
            type="quiz",
            class_id=class1.id,
            date=datetime.now() + timedelta(days=2),
            created_by=teacher.id,
            description="Quick quiz on basic programming concepts"
        )

        assessment3 = Assessment(
            title="Data Structures Project",
            type="assignment",
            class_id=class2.id,
            date=datetime.now() + timedelta(days=14),
            created_by=teacher.id,
            description="Implementation of basic data structures"
        )

        db.session.add_all([assessment1, assessment2, assessment3])
        db.session.commit()

        # Create test scores
        print("Creating test scores...")
        score1 = Score(
            student_id=student.id,
            assessment_id=assessment1.id,
            score_value=85.5,
            feedback="Good work on the midterm",
            submission_date=datetime.now()
        )

        score2 = Score(
            student_id=student.id,
            assessment_id=assessment2.id,
            score_value=92.0,
            feedback="Excellent quiz performance",
            submission_date=datetime.now()
        )

        db.session.add_all([score1, score2])
        db.session.commit()
        
        print("\nTest Data Summary:")
        print(f"Users created: Admin ({admin.id}), Teacher ({teacher.id}), Student ({student.id})")
        print(f"Courses created: {course1.course_code}, {course2.course_code}")
        print(f"Classes created: Section {class1.section_number}, Section {class2.section_number}")
        print(f"Enrollments created for student in sections {class1.section_number} and {class2.section_number}")
        print(f"Assessments created: {assessment1.title}, {assessment2.title}, {assessment3.title}")
        print(f"Scores created: {score1.score_value} on {assessment1.title}, {score2.score_value} on {assessment2.title}")
        
        print("\nDatabase initialized and test data created successfully!")

if __name__ == '__main__':
    print("Starting database initialization...")
    init_database()    
    print("Database initialization completed!")
