from app import create_app, db
from app.models.user import User

def init_database():
    app = create_app('development')
    with app.app_context():
        # Drop all tables
        print("Dropping all tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating all tables...")
        db.create_all()
        
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@example.com').first()
        if admin:
            print("Admin user already exists")
            return

        # Create admin user
        print("Creating admin user...")
        admin = User(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            role='admin',
            theme_preference='light'
        )
        admin.password = 'admin123'  # This will be hashed automatically
        
        # Create test teacher
        print("Creating test teacher...")
        teacher = User(
            email='teacher@example.com',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            theme_preference='light'
        )
        teacher.password = 'teacher123'
        
        # Create test student
        print("Creating test student...")
        student = User(
            email='student@example.com',
            first_name='Test',
            last_name='Student',
            role='student',
            theme_preference='light'
        )
        student.password = 'student123'
        
        # Add users to database
        db.session.add(admin)
        db.session.add(teacher)
        db.session.add(student)
        db.session.commit()
        print("Database initialized and users created successfully")

if __name__ == '__main__':
    print("Starting database initialization...")
    init_database()    
    print("Database initialization completed!")
