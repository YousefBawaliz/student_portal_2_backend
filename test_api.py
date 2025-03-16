import requests
import json
import time
from datetime import datetime, timedelta
import uuid
import random

BASE_URL = "http://127.0.0.1:5000/api"

def get_admin_token():
    """Helper function to get admin token"""
    login_url = f"{BASE_URL}/auth/login"
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    print(f"\nAttempting login with: {json.dumps(login_data, indent=2)}")
    login_response = requests.post(login_url, json=login_data)
    print(f"Login Status: {login_response.status_code}")
    print(f"Login Response: {json.dumps(login_response.json(), indent=2)}")
    
    if login_response.status_code != 200:
        raise Exception(f"Failed to get admin token. Status: {login_response.status_code}, Response: {login_response.json()}")
    
    return login_response.json()['access_token']

def get_unique_course_code():
    """Generate a unique course code that fits within the 20-char limit"""
    timestamp = datetime.now().strftime('%H%M%S')  # 6 chars
    unique_id = str(uuid.uuid4())[:4]  # 4 chars
    return f"T{timestamp}{unique_id}"  # Total: 11 chars (T + 6 + 4)

def get_unique_section_number():
    """Generate a unique section number"""
    timestamp = datetime.now().strftime('%H%M%S')
    unique_id = str(uuid.uuid4())[:2]
    return f"T{timestamp}{unique_id}"

def cleanup_test_courses(admin_headers):
    """Clean up test courses with retry mechanism"""
    max_retries = 3
    retry_delay = 1  # seconds
    
    courses_response = requests.get(f"{BASE_URL}/courses/", headers=admin_headers)
    if courses_response.status_code == 200:
        for course in courses_response.json():
            if course['course_code'].startswith('T'):
                for attempt in range(max_retries):
                    delete_response = requests.delete(
                        f"{BASE_URL}/courses/{course['id']}", 
                        headers=admin_headers
                    )
                    if delete_response.status_code == 200:
                        break
                    time.sleep(retry_delay)

def cleanup_test_classes():
    """Helper function to clean up test classes"""
    print("\nCleaning up test classes...")
    headers = {"Authorization": f"Bearer {get_admin_token()}"}
    
    response = requests.get(f"{BASE_URL}/classes/", headers=headers)
    if response.status_code == 200:
        classes = response.json()
        print(f"Found {len(classes)} classes")
        for class_ in classes:
            if class_['section_number'].startswith('T'):  # Only delete our test classes
                delete_response = requests.delete(
                    f"{BASE_URL}/classes/{class_['id']}", 
                    headers=headers
                )
                print(f"Deleted class {class_['section_number']}: {delete_response.status_code}")
    else:
        print(f"Note: No classes found or endpoint not available (status: {response.status_code})")

def test_auth_flow():
    print("\n=== Testing Auth Flow ===")
    
    # 1. Test invalid login
    print("\n1. Testing invalid login...")
    login_url = f"{BASE_URL}/auth/login"
    invalid_data = {
        "email": "wrong@example.com",
        "password": "wrongpass"
    }
    
    response = requests.post(login_url, json=invalid_data)
    print(f"Invalid login status: {response.status_code}")
    print(f"Invalid login response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 401
    
    # 2. Test valid login
    print("\n2. Testing valid login...")
    valid_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    response = requests.post(login_url, json=valid_data)
    print(f"Valid login status: {response.status_code}")
    print(f"Valid login response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    assert 'access_token' in response.json()
    
    # Store token for subsequent tests
    access_token = response.json()['access_token']
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 3. Test accessing protected endpoint
    print("\n3. Testing protected endpoint access...")
    me_url = f"{BASE_URL}/users/me"
    response = requests.get(me_url, headers=headers)
    print(f"Protected endpoint status: {response.status_code}")
    print(f"Protected endpoint response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200

def test_courses_flow():
    print("\n=== Testing Courses Flow ===")
    
    try:
        # Get admin token
        admin_token = get_admin_token()
        admin_headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }

        # Clean up existing test courses
        print("\nCleaning up test courses...")
        cleanup_test_courses(admin_headers)
        
        # Add delay after cleanup
        time.sleep(2)

        # 1. Create new course
        print("\n1. Creating new course...")
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        course_data = {
            "course_code": f"T{timestamp[:6]}{random.choice('abcdef0123456789')}",
            "title": f"Test Course {timestamp}",
            "description": "This is a test course"
        }
        
        # Add retry mechanism for course creation
        max_retries = 3
        retry_delay = 1
        create_response = None
        
        for attempt in range(max_retries):
            create_response = requests.post(
                f"{BASE_URL}/courses/",
                json=course_data,
                headers=admin_headers
            )
            if create_response.status_code == 201:
                break
            time.sleep(retry_delay)
            
        if create_response.status_code != 201:
            raise Exception(f"Failed to create course after {max_retries} attempts: {create_response.status_code}")
            
        course_id = create_response.json()['id']
        print(f"Created course with ID: {course_id}")

        # 2. Get all courses
        print("\n2. Getting all courses...")
        list_response = requests.get(f"{BASE_URL}/courses/", headers=admin_headers)
        print(f"List courses status: {list_response.status_code}")
        print(f"List courses response: {json.dumps(list_response.json(), indent=2)}")
        assert list_response.status_code == 200
        
        # 3. Get specific course
        print(f"\n3. Getting course with ID {course_id}...")
        get_response = requests.get(f"{BASE_URL}/courses/{course_id}", headers=admin_headers)
        print(f"Get course status: {get_response.status_code}")
        print(f"Get course response: {json.dumps(get_response.json(), indent=2)}")
        assert get_response.status_code == 200
        
        # 4. Update course
        print("\n4. Updating course...")
        update_data = {
            "title": "Updated Test Course",
            "description": "This is an updated test course"
        }
        update_response = requests.put(
            f"{BASE_URL}/courses/{course_id}",
            json=update_data,
            headers=admin_headers
        )
        print(f"Update course status: {update_response.status_code}")
        print(f"Update course response: {json.dumps(update_response.json(), indent=2)}")
        assert update_response.status_code == 200
        
        # 5. Delete course
        print("\n5. Deleting course...")
        delete_response = requests.delete(
            f"{BASE_URL}/courses/{course_id}",
            headers=admin_headers
        )
        print(f"Delete course status: {delete_response.status_code}")
        print(f"Delete course response: {delete_response.text}")
        assert delete_response.status_code == 200
        
        # 6. Verify deletion
        print("\n6. Verifying course deletion...")
        verify_response = requests.get(f"{BASE_URL}/courses/{course_id}", headers=admin_headers)
        print(f"Verify delete status: {verify_response.status_code}")
        assert verify_response.status_code == 404
        
    except Exception as e:
        print(f"\nError during test: {str(e)}")
        print(f"Full error details: {type(e).__name__}: {str(e)}")
        raise
    finally:
        # Clean up after tests
        cleanup_test_courses(admin_headers)

def test_classes_flow():
    print("\n=== Testing Classes Flow ===")
    
    try:
        # Clean up any leftover test classes first
        cleanup_test_classes()
        
        # Get admin token
        access_token = get_admin_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # First create a test course to associate with the class
        course_data = {
            "course_code": get_unique_course_code(),
            "title": "Test Course for Class",
            "description": "Test course description"
        }
        course_response = requests.post(f"{BASE_URL}/courses/", json=course_data, headers=headers)
        assert course_response.status_code == 201
        course_id = course_response.json()['id']
        
        # Get teacher credentials directly
        teacher_login = {
            "email": "teacher@example.com",
            "password": "teacher123"
        }
        teacher_response = requests.post(f"{BASE_URL}/auth/login", json=teacher_login)
        assert teacher_response.status_code == 200, "Failed to login as teacher"
        teacher_data = teacher_response.json()['user']
        teacher_id = teacher_data['id']
        
        # Create new class
        print("\n1. Creating new class...")
        create_url = f"{BASE_URL}/classes/"
        
        class_data = {
            "course_id": course_id,
            "teacher_id": teacher_id,
            "section_number": get_unique_section_number(),
            "semester": "Fall",
            "year": 2024
        }
        
        print(f"Attempting to create class with data:")
        print(json.dumps(class_data, indent=2))
        
        create_response = requests.post(create_url, json=class_data, headers=headers)
        print(f"Create class status: {create_response.status_code}")
        print(f"Create class response: {json.dumps(create_response.json(), indent=2) if create_response.status_code < 300 else create_response.text}")
        assert create_response.status_code == 201, f"Failed to create class: {create_response.text}"
        class_id = create_response.json()['id']
        
        # Get all classes
        print("\n2. Getting all classes...")
        list_response = requests.get(f"{BASE_URL}/classes/", headers=headers)
        print(f"List classes status: {list_response.status_code}")
        print(f"List classes response: {json.dumps(list_response.json(), indent=2)}")
        assert list_response.status_code == 200
        
        # Get specific class
        print(f"\n3. Getting class with ID {class_id}...")
        get_response = requests.get(f"{BASE_URL}/classes/{class_id}", headers=headers)
        print(f"Get class status: {get_response.status_code}")
        print(f"Get class response: {json.dumps(get_response.json(), indent=2)}")
        assert get_response.status_code == 200
        
        # Update class
        print("\n4. Updating class...")
        update_data = {
            "semester": "Spring",
            "year": 2025
        }
        update_response = requests.put(
            f"{BASE_URL}/classes/{class_id}",
            json=update_data,
            headers=headers
        )
        print(f"Update class status: {update_response.status_code}")
        print(f"Update class response: {json.dumps(update_response.json(), indent=2)}")
        assert update_response.status_code == 200
        
        # Test enrollment (as a student)
        print("\n5. Testing class enrollment...")
        # Get a student token
        student_login = {
            "email": "student@example.com",
            "password": "student123"
        }
        student_token_response = requests.post(f"{BASE_URL}/auth/login", json=student_login)
        student_token = student_token_response.json()['access_token']
        student_headers = {
            "Authorization": f"Bearer {student_token}",
            "Content-Type": "application/json"
        }
        
        # Enroll in class
        enroll_response = requests.post(
            f"{BASE_URL}/classes/{class_id}/enroll",
            headers=student_headers
        )
        print(f"Enroll status: {enroll_response.status_code}")
        print(f"Enroll response: {json.dumps(enroll_response.json(), indent=2)}")
        assert enroll_response.status_code == 201
        
        # Unenroll from class
        unenroll_response = requests.delete(
            f"{BASE_URL}/classes/{class_id}/enroll",
            headers=student_headers
        )
        print(f"Unenroll status: {unenroll_response.status_code}")
        assert unenroll_response.status_code == 200
        
        # Clean up - delete class and course
        print("\n6. Cleaning up...")
        requests.delete(f"{BASE_URL}/classes/{class_id}", headers=headers)
        requests.delete(f"{BASE_URL}/courses/{course_id}", headers=headers)
        
        print("\nClass flow tests completed successfully!")
        
    except Exception as e:
        print(f"\nError during test: {str(e)}")
        print(f"Full error details: {type(e).__name__}: {str(e)}")
        raise
    finally:
        # Clean up after tests
        cleanup_test_classes()

def test_assessments_flow():
    print("\n=== Testing Assessments Flow ===")
    
    try:
        # Get teacher token
        teacher_login = {
            "email": "teacher@example.com",
            "password": "teacher123"
        }
        teacher_response = requests.post(f"{BASE_URL}/auth/login", json=teacher_login)
        assert teacher_response.status_code == 200
        teacher_token = teacher_response.json()['access_token']
        teacher_headers = {
            "Authorization": f"Bearer {teacher_token}",
            "Content-Type": "application/json"
        }

        # 1. Create new assessment
        print("\n1. Creating new assessment...")
        assessment_data = {
            "class_id": 1,  # Assuming class_id 1 exists
            "title": f"Test Assessment {datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "type": "quiz",
            "date": (datetime.now() + timedelta(days=7)).isoformat()
        }

        create_response = requests.post(
            f"{BASE_URL}/assessments/",
            json=assessment_data,
            headers=teacher_headers
        )
        print(f"Create assessment status: {create_response.status_code}")
        print(f"Create assessment response: {json.dumps(create_response.json(), indent=2)}")
        assert create_response.status_code == 201
        assessment_id = create_response.json()['id']

        # 2. Get all assessments
        print("\n2. Getting all assessments...")
        list_response = requests.get(f"{BASE_URL}/assessments/", headers=teacher_headers)
        print(f"List assessments status: {list_response.status_code}")
        print(f"List assessments response: {json.dumps(list_response.json(), indent=2)}")
        assert list_response.status_code == 200

        # 3. Get specific assessment
        print(f"\n3. Getting assessment with ID {assessment_id}...")
        get_response = requests.get(
            f"{BASE_URL}/assessments/{assessment_id}",
            headers=teacher_headers
        )
        print(f"Get assessment status: {get_response.status_code}")
        print(f"Get assessment response: {json.dumps(get_response.json(), indent=2)}")
        assert get_response.status_code == 200

        # 4. Update assessment
        print("\n4. Updating assessment...")
        update_data = {
            "title": "Updated Test Assessment",
            "date": (datetime.now() + timedelta(days=14)).isoformat()
        }
        update_response = requests.put(
            f"{BASE_URL}/assessments/{assessment_id}",
            json=update_data,
            headers=teacher_headers
        )
        print(f"Update assessment status: {update_response.status_code}")
        print(f"Update assessment response: {json.dumps(update_response.json(), indent=2)}")
        assert update_response.status_code == 200

        # 5. Get assessment scores
        print("\n5. Getting assessment scores...")
        scores_response = requests.get(
            f"{BASE_URL}/assessments/{assessment_id}/scores",
            headers=teacher_headers
        )
        print(f"Get scores status: {scores_response.status_code}")
        print(f"Get scores response: {json.dumps(scores_response.json(), indent=2)}")
        assert scores_response.status_code == 200

        # 6. Delete assessment
        print("\n6. Deleting assessment...")
        delete_response = requests.delete(
            f"{BASE_URL}/assessments/{assessment_id}",
            headers=teacher_headers
        )
        print(f"Delete assessment status: {delete_response.status_code}")
        assert delete_response.status_code == 200

    except Exception as e:
        print(f"\nError during assessment test: {str(e)}")
        raise

def test_scores_flow():
    print("\n=== Testing Scores Flow ===")
    
    try:
        # Get teacher token
        teacher_login = {
            "email": "teacher@example.com",
            "password": "teacher123"
        }
        teacher_response = requests.post(f"{BASE_URL}/auth/login", json=teacher_login)
        assert teacher_response.status_code == 200
        teacher_token = teacher_response.json()['access_token']
        teacher_headers = {
            "Authorization": f"Bearer {teacher_token}",
            "Content-Type": "application/json"
        }

        # Get student ID (using student@example.com from init_db.py)
        student_login = {
            "email": "student@example.com",
            "password": "student123"
        }
        student_response = requests.post(f"{BASE_URL}/auth/login", json=student_login)
        student_id = student_response.json()['user']['id']

        # Get all existing scores for the student and delete them
        print("\nClearing existing scores...")
        existing_scores = requests.get(
            f"{BASE_URL}/scores/student/{student_id}",
            headers=teacher_headers
        )
        for score in existing_scores.json():
            requests.delete(
                f"{BASE_URL}/scores/{score['id']}",
                headers=teacher_headers
            )

        # 1. Create new score
        print("\n1. Creating new score...")
        score_data = {
            "student_id": student_id,
            "assessment_id": 3,  # Using assessment_id 3 (Data Structures Project) from init_db.py
            "score_value": 95.5,
            "feedback": "Excellent work!"
        }

        create_response = requests.post(
            f"{BASE_URL}/scores/",
            json=score_data,
            headers=teacher_headers
        )
        print(f"Create score status: {create_response.status_code}")
        print(f"Create score response: {json.dumps(create_response.json(), indent=2)}")
        assert create_response.status_code == 201
        score_id = create_response.json()['id']

        # 2. Get specific score
        print(f"\n2. Getting score with ID {score_id}...")
        get_response = requests.get(
            f"{BASE_URL}/scores/{score_id}",
            headers=teacher_headers
        )
        print(f"Get score status: {get_response.status_code}")
        print(f"Get score response: {json.dumps(get_response.json(), indent=2)}")
        assert get_response.status_code == 200

        # 3. Update score
        print("\n3. Updating score...")
        update_data = {
            "score_value": 97.0,
            "feedback": "Updated feedback - Outstanding performance!"
        }
        update_response = requests.put(
            f"{BASE_URL}/scores/{score_id}",
            json=update_data,
            headers=teacher_headers
        )
        print(f"Update score status: {update_response.status_code}")
        print(f"Update score response: {json.dumps(update_response.json(), indent=2)}")
        assert update_response.status_code == 200

        # 4. Get student scores
        print("\n4. Getting student scores...")
        student_scores_response = requests.get(
            f"{BASE_URL}/scores/student/{student_id}",
            headers=teacher_headers
        )
        print(f"Get student scores status: {student_scores_response.status_code}")
        print(f"Get student scores response: {json.dumps(student_scores_response.json(), indent=2)}")
        assert student_scores_response.status_code == 200

        # 5. Get student score by assessment title (using the assessment title we created the score for)
        print("\n5. Getting student score by assessment title...")
        title_response = requests.get(
            f"{BASE_URL}/scores/student/{student_id}/assessment",
            params={"title": "Data Structures Project"},  # Changed to match the assessment we created score for
            headers=teacher_headers
        )
        print(f"Get score by title status: {title_response.status_code}")
        print(f"Get score by title response: {json.dumps(title_response.json(), indent=2)}")
        assert title_response.status_code == 200

        # 6. Delete score
        print("\n6. Deleting score...")
        delete_response = requests.delete(
            f"{BASE_URL}/scores/{score_id}",
            headers=teacher_headers
        )
        print(f"Delete score status: {delete_response.status_code}")
        assert delete_response.status_code == 200

    except Exception as e:
        print(f"\nError during scores test: {str(e)}")
        raise

if __name__ == '__main__':
    test_auth_flow()
    test_courses_flow()
    test_classes_flow()
    test_assessments_flow()
    test_scores_flow()
