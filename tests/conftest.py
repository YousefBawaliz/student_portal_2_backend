
import pytest
from app import create_app, db
from app.models.user import User

@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    app = create_app('testing')
    return app

@pytest.fixture(scope='function')
def client_with_db(app):
    """Create test client with a fresh database."""
    with app.app_context():
        print("\n--- Setting up test database ---")
        db.drop_all()  # Ensure we start fresh
        db.create_all()
        print("Database tables created")
        
        # Create test admin user
        admin = User(
            email='test.admin@example.com',
            first_name='Test',
            last_name='Admin',
            role='admin'
        )
        admin.set_password('testadmin123')
        db.session.add(admin)
        
        try:
            db.session.commit()
            # Verify the admin was created
            created_admin = User.query.filter_by(email='test.admin@example.com').first()
            print(f"Created admin user: {created_admin.email}")
            print(f"Admin role: {created_admin.role}")
            print(f"Admin ID: {created_admin.id}")
        except Exception as e:
            print(f"Error creating admin user: {str(e)}")
            db.session.rollback()
            raise e
    
    yield app.test_client()
    
    # Cleanup
    with app.app_context():
        print("\n--- Cleaning up test database ---")
        db.session.remove()
        db.drop_all()
        print("Database cleaned up")

@pytest.fixture
def client(client_with_db):
    """Alias for client_with_db"""
    return client_with_db
