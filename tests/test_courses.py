import pytest
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.models.course import Course
from app import db

@pytest.fixture
def admin_token(client, app):
    """Get admin token using the test admin credentials"""
    print("\n--- Getting admin token ---")
    
    # Use the admin credentials that are created in conftest.py
    login_data = {
        'email': 'test.admin@example.com',
        'password': 'testadmin123'
    }
    print(f"Attempting login with: {login_data}")
    
    response = client.post('/api/auth/login', json=login_data)
    print(f"Login response status: {response.status_code}")
    print(f"Login response data: {response.get_json()}")
    
    if response.status_code != 200:
        # Debug: Check if admin exists
        with app.app_context():
            admin = User.query.filter_by(email='test.admin@example.com').first()
            print(f"Admin exists in DB: {admin is not None}")
            if admin:
                print(f"Admin ID: {admin.id}")
                print(f"Admin role: {admin.role}")
                print(f"Can verify password: {admin.verify_password('testadmin123')}")
        raise Exception(f"Failed to get admin token. Status: {response.status_code}, Response: {response.get_json()}")
    
    return response.json['access_token']

@pytest.fixture
def test_users(client):
    """Create test users: teacher and student"""
    # First clean up any existing test users
    User.query.filter(User.email.in_(['test.teacher@example.com', 'test.student@example.com'])).delete()
    db.session.commit()

    # Create teacher
    teacher = User(
        email='test.teacher@example.com',
        first_name='Test',
        last_name='Teacher',
        role='teacher'
    )
    teacher.set_password('password123')  # Use set_password instead of direct assignment

    # Create student
    student = User(
        email='test.student@example.com',
        first_name='Test',
        last_name='Student',
        role='student'
    )
    student.set_password('password123')  # Use set_password instead of direct assignment

    db.session.add_all([teacher, student])
    db.session.commit()

    yield {
        'teacher': teacher,
        'student': student
    }

    # Cleanup
    User.query.filter(User.email.in_(['test.teacher@example.com', 'test.student@example.com'])).delete()
    db.session.commit()

@pytest.fixture
def test_course(client, admin_token):
    """Create a test course"""
    course_data = {
        "course_code": "TEST101",
        "title": "Test Course",
        "description": "Test Description"
    }
    
    response = client.post(
        '/api/courses/',
        json=course_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    course_id = response.json['id']
    
    yield response.json
    
    # Cleanup
    Course.query.filter_by(id=course_id).delete()
    db.session.commit()

def test_create_course(client, admin_token):
    """Test course creation"""
    course_data = {
        "course_code": "CS101",
        "title": "Introduction to Computer Science",
        "description": "Basic programming concepts"
    }
    
    response = client.post(
        '/api/courses/',
        json=course_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    assert response.json['course_code'] == "CS101"
    
    # Verify course was created
    course = Course.query.filter_by(course_code="CS101").first()
    assert course is not None
    assert course.title == "Introduction to Computer Science"

def test_get_courses(client, admin_token, test_users, test_course):
    """Test getting courses with different user roles"""
    teacher_token = create_access_token(identity=str(test_users['teacher'].id))
    student_token = create_access_token(identity=str(test_users['student'].id))
    
    # Test as admin
    response = client.get(
        '/api/courses/',
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert len(response.json) > 0
    
    # Test as teacher
    response = client.get(
        '/api/courses/',
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    
    # Test as student
    response = client.get(
        '/api/courses/',
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200

def test_update_course(client, admin_token, test_course):
    """Test course update"""
    update_data = {
        "title": "Updated Course Title",
        "description": "Updated description"
    }
    
    response = client.put(
        f'/api/courses/{test_course["id"]}',
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json['title'] == "Updated Course Title"

def test_delete_course(client, admin_token, test_course):
    """Test course deletion"""
    response = client.delete(
        f'/api/courses/{test_course["id"]}',
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200

def test_course_permissions(client, test_users):
    """Test course permissions for different user roles"""
    teacher_token = create_access_token(identity=str(test_users['teacher'].id))
    student_token = create_access_token(identity=str(test_users['student'].id))
    
    course_data = {
        "course_code": "CS102",
        "title": "Test Course",
        "description": "Test Description"
    }
    
    # Test course creation as non-admin users
    for token in [teacher_token, student_token]:
        response = client.post(
            '/api/courses/',
            json=course_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403
