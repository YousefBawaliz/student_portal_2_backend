import pytest
from app import create_app, db
from app.models.user import User

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app('testing')
    
    # Create the database and tables
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def test_users(app):
    """Create test users."""
    with app.app_context():
        # Create admin user
        admin = User(
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        admin.password = 'admin123'

        # Create teacher user
        teacher = User(
            email='teacher@test.com',
            first_name='Teacher',
            last_name='User',
            role='teacher'
        )
        teacher.password = 'teacher123'

        # Create student user
        student = User(
            email='student@test.com',
            first_name='Student',
            last_name='User',
            role='student'
        )
        student.password = 'student123'

        db.session.add_all([admin, teacher, student])
        db.session.commit()

        return {'admin': admin, 'teacher': teacher, 'student': student}

@pytest.fixture
def admin_token(client, test_users):
    """Get admin JWT token."""
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'admin123'
    })
    return response.get_json()['access_token']

@pytest.fixture
def teacher_token(client, test_users):
    """Get teacher JWT token."""
    response = client.post('/api/auth/login', json={
        'email': 'teacher@test.com',
        'password': 'teacher123'
    })
    return response.get_json()['access_token']

@pytest.fixture
def student_token(client, test_users):
    """Get student JWT token."""
    response = client.post('/api/auth/login', json={
        'email': 'student@test.com',
        'password': 'student123'
    })
    return response.get_json()['access_token']
