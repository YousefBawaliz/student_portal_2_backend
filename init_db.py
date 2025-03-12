from app import create_app, db
from app.models.user import User

def init_database():
    app = create_app('development')
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@example.com').first()
        if admin:
            print("Admin user already exists")
            return

        # Create admin user
        admin = User(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            role='admin',
            theme_preference='light'
        )
        admin.password = 'admin123'  # This will be hashed automatically

        # Add to database
        db.session.add(admin)
        db.session.commit()
        print("Database initialized and admin user created successfully")

if __name__ == '__main__':
    init_database()