import requests
import json
import time
from datetime import datetime
import uuid

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

def cleanup_test_courses():
    """Helper function to clean up test courses"""
    print("\nCleaning up test courses...")
    headers = {"Authorization": f"Bearer {get_admin_token()}"}
    
    # First, let's see what courses exist
    response = requests.get(f"{BASE_URL}/courses/", headers=headers)
    if response.status_code == 200:
        courses = response.json()
        print(f"Found {len(courses)} courses")
        for course in courses:
            print(f"Found course: {course['course_code']} (ID: {course['id']})")
            if course['course_code'].startswith('T'):  # Only delete our test courses
                delete_response = requests.delete(
                    f"{BASE_URL}/courses/{course['id']}", 
                    headers=headers
                )
                print(f"Deleted course {course['course_code']}: {delete_response.status_code}")
    else:
        print(f"Failed to get courses: {response.status_code}")

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
        # Clean up any leftover test courses first
        cleanup_test_courses()
        
        # Get admin token
        access_token = get_admin_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # First, let's check what courses exist
        list_response = requests.get(f"{BASE_URL}/courses/", headers=headers)
        print("\nExisting courses before creation:")
        print(json.dumps(list_response.json(), indent=2))
        
        # Create new course
        print("\n1. Creating new course...")
        create_url = f"{BASE_URL}/courses/"
        
        max_attempts = 3
        course_id = None
        
        for attempt in range(max_attempts):
            course_code = get_unique_course_code()
            course_data = {
                "course_code": course_code,
                "title": f"Test Course {datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "description": "This is a test course"
            }
            
            print(f"\nAttempt {attempt + 1}: Creating course with data:")
            print(json.dumps(course_data, indent=2))
            
            create_response = requests.post(create_url, json=course_data, headers=headers)
            print(f"Create course status: {create_response.status_code}")
            print(f"Create course response: {json.dumps(create_response.json(), indent=2)}")
            
            if create_response.status_code == 201:
                course_id = create_response.json()['id']
                print(f"Successfully created course with ID: {course_id}")
                break
            
            if attempt < max_attempts - 1:
                print(f"Retrying course creation... (attempt {attempt + 2} of {max_attempts})")
                time.sleep(1)  # Add a small delay between attempts
            else:
                raise Exception(f"Failed to create course after {max_attempts} attempts")
        
        if not course_id:
            raise Exception("Failed to get course ID after creation")
        
        # 2. Get all courses
        print("\n2. Getting all courses...")
        list_response = requests.get(f"{BASE_URL}/courses/", headers=headers)
        print(f"List courses status: {list_response.status_code}")
        print(f"List courses response: {json.dumps(list_response.json(), indent=2)}")
        assert list_response.status_code == 200
        
        # 3. Get specific course
        print(f"\n3. Getting course with ID {course_id}...")
        get_response = requests.get(f"{BASE_URL}/courses/{course_id}", headers=headers)
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
            headers=headers
        )
        print(f"Update course status: {update_response.status_code}")
        print(f"Update course response: {json.dumps(update_response.json(), indent=2)}")
        assert update_response.status_code == 200
        
        # 5. Delete course
        print("\n5. Deleting course...")
        delete_response = requests.delete(
            f"{BASE_URL}/courses/{course_id}",
            headers=headers
        )
        print(f"Delete course status: {delete_response.status_code}")
        print(f"Delete course response: {delete_response.text}")
        assert delete_response.status_code == 200
        
        # 6. Verify deletion
        print("\n6. Verifying course deletion...")
        verify_response = requests.get(f"{BASE_URL}/courses/{course_id}", headers=headers)
        print(f"Verify delete status: {verify_response.status_code}")
        assert verify_response.status_code == 404
        
    except Exception as e:
        print(f"\nError during test: {str(e)}")
        print(f"Full error details: {type(e).__name__}: {str(e)}")
        raise
    finally:
        # Clean up after tests
        cleanup_test_courses()

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

if __name__ == "__main__":
    print("\nStarting API tests...")
    try:
        test_auth_flow()
        print("\nAuth flow tests passed!")
        
        test_courses_flow()
        print("\nCourse flow tests passed!")
        
        test_classes_flow()
        print("\nClass flow tests passed!")
        
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nTests failed: {str(e)}")
        print("Test execution stopped due to error.")
