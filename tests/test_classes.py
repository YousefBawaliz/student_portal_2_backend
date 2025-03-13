import pytest
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.models.class_ import Class
from app.models.class_enrollment import ClassEnrollment
from app import db

@pytest.fixture
def test_class(client, admin_token, test_course, test_users):
    """Create a test class"""
    class_data = {
        "course_id": test_course['id'],
        "teacher_id": test_users['teacher'].id,
        "section_number": "001",
        "semester": "Fall",
        "year": 2023
    }
    
    response = client.post(
        '/api/classes/',
        json=class_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    class_id = response.json['id']
    
    yield response.json
    
    # Cleanup
    Class.query.filter_by(id=class_id).delete()
    db.session.commit()

def test_create_class(client, admin_token, test_course, test_users):
    """Test class creation"""
    class_data = {
        "course_id": test_course['id'],
        "teacher_id": test_users['teacher'].id,
        "section_number": "002",
        "semester": "Spring",
        "year": 2024
    }
    
    response = client.post(
        '/api/classes/',
        json=class_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    assert response.json['section_number'] == "002"
    
    # Cleanup
    Class.query.filter_by(id=response.json['id']).delete()
    db.session.commit()

def test_get_classes(client, admin_token, test_users, test_class):
    """Test getting classes with different user roles"""
    teacher_token = create_access_token(identity=str(test_users['teacher'].id))
    student_token = create_access_token(identity=str(test_users['student'].id))
    
    # Test as admin
    response = client.get(
        '/api/classes/',
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert len(response.json) > 0
    
    # Test as teacher
    response = client.get(
        '/api/classes/',
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    
    # Test as student
    response = client.get(
        '/api/classes/',
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200

def test_class_enrollment(client, test_users, test_class):
    """Test class enrollment functionality"""
    student_token = create_access_token(identity=str(test_users['student'].id))
    
    # Test enrollment
    response = client.post(
        f'/api/classes/{test_class["id"]}/enroll',
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 201
    
    # Verify enrollment
    enrollment = ClassEnrollment.query.filter_by(
        student_id=test_users['student'].id,
        class_id=test_class['id']
    ).first()
    assert enrollment is not None
    
    # Test unenrollment
    response = client.delete(
        f'/api/classes/{test_class["id"]}/enroll',
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    
    # Verify unenrollment
    enrollment = ClassEnrollment.query.filter_by(
        student_id=test_users['student'].id,
        class_id=test_class['id']
    ).first()
    assert enrollment is None

def test_class_permissions(client, test_users, test_course):
    """Test class permissions for different user roles"""
    teacher_token = create_access_token(identity=str(test_users['teacher'].id))
    student_token = create_access_token(identity=str(test_users['student'].id))
    
    class_data = {
        "course_id": test_course['id'],
        "teacher_id": test_users['teacher'].id,
        "section_number": "003",
        "semester": "Fall",
        "year": 2023
    }
    
    # Test class creation as non-admin users
    for token in [teacher_token, student_token]:
        response = client.post(
            '/api/classes/',
            json=class_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403

def test_duplicate_enrollment(client, test_users, test_class):
    """Test duplicate enrollment prevention"""
    student_token = create_access_token(identity=str(test_users['student'].id))
    
    # First enrollment
    response = client.post(
        f'/api/classes/{test_class["id"]}/enroll',
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 201
    
    # Attempt duplicate enrollment
    response = client.post(
        f'/api/classes/{test_class["id"]}/enroll',
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 409
    
    # Cleanup
    ClassEnrollment.query.filter_by(
        student_id=test_users['student'].id,
        class_id=test_class['id']
    ).delete()
    db.session.commit()