import pytest
from flask_jwt_extended import create_access_token
from app.models.user import User
from app import db

@pytest.fixture
def admin_token(client):
    """Get admin token using the known admin credentials"""
    # Login as admin
    response = client.post('/api/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    assert response.status_code == 200
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
    teacher.password = 'password123'

    # Create student
    student = User(
        email='test.student@example.com',
        first_name='Test',
        last_name='Student',
        role='student'
    )
    student.password = 'password123'

    # Add users to database
    db.session.add(teacher)
    db.session.add(student)
    db.session.commit()

    yield {
        'teacher': teacher,
        'student': student
    }

    # Cleanup after tests
    User.query.filter(User.email.in_(['test.teacher@example.com', 'test.student@example.com'])).delete()
    db.session.commit()

def test_course_endpoints(client, admin_token, test_users):
    # Get test users
    teacher = test_users['teacher']
    student = test_users['student']

    # Create tokens
    teacher_token = create_access_token(identity=str(teacher.id))
    student_token = create_access_token(identity=str(student.id))
    
    # Test course creation (as admin)
    course_data = {
        "course_code": "CS101",
        "title": "Introduction to Computer Science",
        "description": "Basic programming concepts",
        "teacher_id": teacher.id
    }
    
    response = client.post(
        '/api/courses/',
        json=course_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    course_id = response.json['id']
    
    # Verify teacher assignment
    response = client.get(
        f'/api/courses/{course_id}',
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json['teacher_id'] == teacher.id
    assert response.json['teacher']['email'] == 'test.teacher@example.com'
    
    # Test get all courses (as teacher)
    response = client.get(
        '/api/courses/',
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    assert len(response.json) > 0
    assert response.json[0]['teacher_id'] == teacher.id
    
    # Test update course (as assigned teacher)
    update_data = {
        "title": "Updated CS101",
        "description": "Updated description"
    }
    response = client.put(
        f'/api/courses/{course_id}',
        json=update_data,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    assert response.json['title'] == "Updated CS101"
    
    # Test student enrollment
    response = client.post(
        f'/api/courses/{course_id}/enroll',
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 201
    
    # Verify student enrollment
    response = client.get(
        f'/api/courses/{course_id}',
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    assert any(s['id'] == student.id for s in response.json['students'])
    
    # Test student unenrollment
    response = client.delete(
        f'/api/courses/{course_id}/enroll',
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    
    # Verify student was unenrolled
    response = client.get(
        f'/api/courses/{course_id}',
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    assert not any(s['id'] == student.id for s in response.json['students'])
    
    # Test course deletion (as admin)
    response = client.delete(
        f'/api/courses/{course_id}',
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200

def test_course_permissions(client, admin_token, test_users):
    student = test_users['student']
    teacher = test_users['teacher']
    
    # Create tokens
    student_token = create_access_token(identity=str(student.id))
    teacher_token = create_access_token(identity=str(teacher.id))
    
    # Test course creation as student (should fail)
    course_data = {
        "course_code": "CS102",
        "title": "Test Course",
        "description": "Test Description",
        "teacher_id": teacher.id
    }
    response = client.post(
        '/api/courses/',
        json=course_data,
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 403
    
    # Test course creation as teacher (should fail - only admin can create)
    response = client.post(
        '/api/courses/',
        json=course_data,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 403

def test_invalid_teacher_assignment(client, admin_token, test_users):
    # Try to create course with non-existent teacher
    course_data = {
        "course_code": "CS103",
        "title": "Test Course",
        "description": "Test Description",
        "teacher_id": 99999  # Non-existent teacher ID
    }
    response = client.post(
        '/api/courses/',
        json=course_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404

    # Try to create course with student as teacher
    student = test_users['student']
    course_data['teacher_id'] = student.id
    response = client.post(
        '/api/courses/',
        json=course_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400
