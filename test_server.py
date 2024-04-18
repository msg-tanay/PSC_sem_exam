import unittest
from unittest.mock import patch, MagicMock
import server
import psycopg2

class TestServer(unittest.TestCase):

    @patch('server.psycopg2.connect')
    def test_create_course(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        server.create_course('course-name=Test&course-description=Description')
        mock_cursor.execute.assert_called_once_with("INSERT INTO courses (name, description, teacher_id) VALUES (%s, %s, %s)", ('Test', 'Description', 0))

    @patch('server.psycopg2.connect')
    def test_enroll_in_course(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        server.enroll_in_course('course_id=1')
        mock_cursor.execute.assert_called_once_with("INSERT INTO course_enrollments (course_id, student_id) VALUES (%s, %s)", ('1', 0))

    @patch('server.psycopg2.connect')
    def test_drop_course(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        server.drop_course('course_id=1')
        mock_cursor.execute.assert_called_once_with("DELETE FROM course_enrollments WHERE course_id = %s AND student_id = %s", ('1', 0))

    @patch('server.psycopg2.connect')
    def test_login_user(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = [1, 'password']
        server.login_user('username=user&password=password&role=student')
        mock_cursor.execute.assert_called_once_with("SELECT id, password FROM users WHERE username = %s AND role = %s", ('user', 'student'))

    @patch('server.psycopg2.connect')
    def test_get_courses(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [(1, 'Test', 'Description')]
        server.get_courses()
        mock_cursor.execute.assert_called_once_with("SELECT * FROM courses")

    @patch('server.open', new_callable=MagicMock)
    def test_read_index_page(self, mock_open):
        mock_open.return_value.__enter__.return_value.read.return_value = 'Test'
        result = server.read_index_page()
        self.assertEqual(result, 'Test')

    @patch('server.open', new_callable=MagicMock)
    def test_read_student_dashboard(self, mock_open):
        mock_open.return_value.__enter__.return_value.read.return_value = 'Test'
        result = server.read_student_dashboard()
        self.assertEqual(result, 'Test')

    @patch('server.open', new_callable=MagicMock)
    def test_read_teacher_dashboard(self, mock_open):
        mock_open.return_value.__enter__.return_value.read.return_value = 'Test'
        result = server.read_teacher_dashboard()
        self.assertEqual(result, 'Test')

    def test_parse_form_data(self):
        result = server.parse_form_data('key1=value1&key2=value2')
        self.assertEqual(result, {'key1': 'value1', 'key2': 'value2'})

    def test_parse_request(self):
        result = server.parse_request('GET / HTTP/1.1\nHost: localhost:8000\n\n')
        self.assertEqual(result, ('GET', '/', {'Host': 'localhost:8000'}, ''))

if __name__ == '__main__':
    unittest.main()