import socket
import json
# from passlib.context import CryptContext
import psycopg2
from urllib.parse import unquote

# Database connection details
db_host = 'localhost'
db_name = 'lms'
db_user = 'postgres'
db_password = 'awedftyh'

# Initialize password hasher
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

current_user_id = 0

def response_500(message):
    return f'HTTP/1.1 500 Internal Server Error\r\nContent-Type: application/json\r\n\r\n{{"error": "{message}"}}\r\n'

def parse_request(request):
    lines = request.split('\n')
    method, path, *_ = lines[0].split(' ')
    headers = {}
    for line in lines[1:]:
        if not line.strip():
            break
        key, value = line.split(': ', 1)
        headers[key] = value.strip()
    body = lines[-1]
    return method, path, headers, body

def response_404():
    return 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<html><body>Invalid request.</body></html>\r\n'

def response_200(data):
    return f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{data}\r\n'

def read_index_page():
    with open("index.html", "r") as file:
        return file.read()

# def parse_form_data(data):
#     form_data = {}
#     for item in data.split('&'):
#         key, value = item.split('=')
#         key = unquote(key)
#         value = unquote(value)
#         form_data[key] = value.replace('+', ' ')
#     return form_data

def parse_form_data(data):
    form_data = {}
    if data:
        for item in data.split('&'):
            key_value_pair = item.split('=')
            if len(key_value_pair) == 2:
                key = unquote(key_value_pair[0])
                value = unquote(key_value_pair[1])
                form_data[key] = value.replace('+', ' ')
    return form_data


def response_400(message):
    return f'HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\n\r\n{{"error": "{message}"}}\r\n'

def read_student_dashboard():
    with open("student_dashboard.html", "r") as file:
        return file.read()

def read_teacher_dashboard():
    with open("teacher_dashboard.html", "r") as file:
        return file.read()

def response_401(message):
    return f'HTTP/1.1 401 Unauthorized\r\nContent-Type: application/json\r\n\r\n{{"error": "{message}"}}\r\n'

def create_course(body):
    # Parse form data
    # print("--------------1-----------------")
    form_data = parse_form_data(body)

    # Extract form fields
    name = form_data.get('course-name')
    description = form_data.get('course-description')
    teacher_id = current_user_id
    print(name, description, teacher_id)
    # print("--------------2-----------------")
    try:
        # Connect to the database
        conn = psycopg2.connect(host=db_host, dbname=db_name, user=db_user, password=db_password, port=5433)
        cursor = conn.cursor()
        # print("--------------3-----------------")
        # Insert the new course into the database using a parameterized query
        cursor.execute("INSERT INTO courses (name, description, teacher_id) VALUES (%s, %s, %s)", (name, description, teacher_id))
        # print("--------------4-----------------")
        # Commit the transaction and close the database connection
        conn.commit()
        cursor.close()
        conn.close()

        return response_200('Course created successfully')
    except psycopg2.Error as e:
        return response_500(str(e))

def enroll_in_course(body):
    # Parse form data
    form_data = parse_form_data(body)

    # Extract form fields
    course_id = form_data.get('course_id')
    student_id = current_user_id

    try:
        # Connect to the database
        conn = psycopg2.connect(host=db_host, dbname=db_name, user=db_user, password=db_password, port=5433)
        cursor = conn.cursor()

        # Insert the new enrollment into the database using a parameterized query
        cursor.execute("INSERT INTO course_enrollments (course_id, student_id) VALUES (%s, %s)", (course_id, student_id))

        # Commit the transaction and close the database connection
        conn.commit()
        cursor.close()
        conn.close()

        return response_200('Enrolled in course successfully')
    except psycopg2.Error as e:
        return response_500(str(e))

def drop_course(body):
    # Parse form data
    form_data = parse_form_data(body)

    # Extract form fields
    course_id = form_data.get('course_id')
    student_id = current_user_id

    try:
        # Connect to the database
        conn = psycopg2.connect(host=db_host, dbname=db_name, user=db_user, password=db_password, port=5433)
        cursor = conn.cursor()

        # Delete the enrollment from the database using a parameterized query
        cursor.execute("DELETE FROM course_enrollments WHERE course_id = %s AND student_id = %s", (course_id, student_id))

        # Commit the transaction and close the database connection
        conn.commit()
        cursor.close()
        conn.close()

        return response_200('Dropped course successfully')
    except psycopg2.Error as e:
        return response_500(str(e))

def login_user(data):
    # Parse form data
    global current_user_id
    form_data = parse_form_data(data)

    # Extract form fields
    username = form_data.get('username')
    password = form_data.get('password')
    role = form_data.get('role')

    try:
        # Connect to the database
        conn = psycopg2.connect(host=db_host, dbname=db_name, user=db_user, password=db_password, port=5433)
        cursor = conn.cursor()

        # Retrieve user data from the database using a parameterized query
        cursor.execute("SELECT id, password FROM users WHERE username = %s AND role = %s", (username, role))
        user_data = cursor.fetchone()

        if user_data is not None:
            current_user_id = user_data[0]
            retrieved_password = user_data[1]
            # Verify the password
            if password==retrieved_password:
                # Close the database connection
                cursor.close()
                conn.close()
                # Determine the role and redirect accordingly
                if role == 'student':
                    return response_200(read_student_dashboard())
                elif role == 'teacher':
                    return response_200(read_teacher_dashboard())
             # Return a HTML response with a JavaScript alert
            else:
                return response_200('<html><body><script>alert("Invalid username or password"); window.location="/login.html";</script></body></html>')
        # Close the database connection
        cursor.close()
    except psycopg2.Error as e:
        return response_500(str(e))
    
def get_courses():
    try:
        # Connect to the database
        conn = psycopg2.connect(host=db_host, dbname=db_name, user=db_user, password=db_password, port=5433)
        cursor = conn.cursor()

        # Execute the query to fetch courses
        cursor.execute("SELECT * FROM courses")

        # Fetch all rows from the result set
        courses = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Convert the courses to a list of dictionaries
        course_list = []
        for course in courses:
            course_dict = {
                'id': course[0],
                'name': course[1],
                'description': course[2]
            }
            course_list.append(course_dict)

        # Return the list of courses as a JSON response
        return response_200(json.dumps(course_list))
    except psycopg2.Error as e:
        return response_500(str(e))

    
def handle_request(request):
    method, path, headers, body = parse_request(request)
    if method == 'GET':
        if path == '/':
            return response_200(read_index_page())
        elif path == '/login.html':
            return response_200(login_user())
        elif path == '/get_courses':
            return get_courses()
        else:
            return response_404()
    elif method == 'POST':
        if path == '/login':
            return login_user(body)
        if path == '/create':
            return create_course(body)
        elif path == '/enroll':
            return enroll_in_course(body)
        elif path == '/drop_course':
            return drop_course(body)
        else:
            return response_404()
    else:
        return response_400('Method not supported')

def main():
    host = '127.0.0.1'
    port = 4545

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()

    print(f"Server listening on http://{host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")
        request = client_socket.recv(1024).decode()
        print(request)
        response = handle_request(request)
        client_socket.send(response.encode())
        client_socket.close()

if __name__ == "__main__":
    main()