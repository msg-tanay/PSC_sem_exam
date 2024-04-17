import socket
# import json
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

def parse_form_data(data):
    form_data = {}
    for item in data.split('&'):
        key, value = item.split('=')
        key = unquote(key)
        value = unquote(value)
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

def login_user(data):
    # Parse form data
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
    
def handle_request(request):
    lines = request.split('\r\n')
    method, path, headers, body = parse_request(lines)
    
    if method == 'GET':
        if path == '/':
            return response_200(read_index_page())
        elif path == '/login.html':
            return response_200(login_user())
        else:
            return response_404()
    elif method == 'POST':
        if path == '/login':
            return login_user(body)
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