from sis import my_sql
from math import ceil
import cloudinary
import cloudinary.uploader
import os
from urllib.parse import urlparse

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

class BaseModel:
    """Base model class with common database operations."""
    
    @staticmethod
    def get_db_connection():
        """Create and return a database connection."""
        connection = my_sql.connect()
        cursor = connection.cursor()
        return connection, cursor
    
    @staticmethod
    def close_connection(connection, cursor):
        """Close the database connection."""
        cursor.close()
        connection.close()


class Student(BaseModel):
    """Model class for Student entity."""
    
    def __init__(self, id_number=None, first_name=None, last_name=None, 
                 course=None, year_level=None, gender=None, profile_image=None):
        self.id_number = id_number
        self.first_name = first_name
        self.last_name = last_name
        self.course = course
        self.year_level = year_level
        self.gender = gender
        self.profile_image = profile_image
    
    @classmethod
    def get_all(cls, page=1, per_page=12):
        """Get all students with pagination."""
        connection, cursor = cls.get_db_connection()
        
        offset = (page - 1) * per_page

        cursor.execute("""
            SELECT 
                s.id_number, 
                s.first_name, 
                s.last_name, 
                CONCAT(s.course, ' - ', c.course_name) AS course_full,
                s.year_level, 
                s.gender, 
                s.profile_image
            FROM Student s
            JOIN Course c ON s.course = c.course_code
            ORDER BY s.last_name
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        students = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM Student")
        result = cursor.fetchone()
        total_students = result[0] if result else 0
        
        cls.close_connection(connection, cursor)
        
        total_pages = ceil(total_students / per_page)
        
        return students, total_students, total_pages

    
    @classmethod
    def get_by_id(cls, id_number):
        """Get a student by ID."""
        connection, cursor = cls.get_db_connection()
        
        cursor.execute("SELECT * FROM Student WHERE id_number = %s", (id_number,))
        student = cursor.fetchone()
        
        cls.close_connection(connection, cursor)
        return student
    
    @classmethod
    def search(cls, search_by, search_value, page=1, per_page=10):
        """Search for students by various fields."""
        connection, cursor = cls.get_db_connection()
        
        pairs = {
            "ID Number": "id_number",
            "First name": "first_name",
            "Last name": "last_name",
            "Course": "course",
            "Year Level": "year_level",
            "Gender": "gender"
        }
        
        offset = (page - 1) * per_page
        field = pairs.get(search_by)
        if not field:
            return [], 0, 0
            
        cursor.execute(f"""
            SELECT 
            s.id_number, 
            s.first_name, 
            s.last_name, 
            CONCAT(s.course, ' - ', c.course_name) AS course_full,
            s.year_level, 
            s.gender, 
            s.profile_image
        FROM Student s
        JOIN Course c ON s.course = c.course_code
        WHERE {field} LIKE %s
        ORDER BY s.last_name
        LIMIT %s OFFSET %s
        """,
                      (f'%{search_value}%', per_page, offset))
        students = cursor.fetchall()
        
        cursor.execute(f"SELECT COUNT(*) FROM Student WHERE {field} LIKE %s", 
                      (f'%{search_value}%',))
        total_students = cursor.fetchone()[0]
        
        cls.close_connection(connection, cursor)
        
        total_pages = ceil(total_students / per_page)
        return students, total_students, total_pages
    
    def create(self):
        """Insert a new student into the database."""
        connection, cursor = self.get_db_connection()
        cursor.execute(
            """
            INSERT INTO Student (id_number, first_name, last_name, course, year_level, gender, profile_image) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (self.id_number, self.first_name, self.last_name, self.course, self.year_level, self.gender, self.profile_image)
            )
        connection.commit()
        self.close_connection(connection, cursor)
        return self.id_number


    def update(self, original_id_number):
        """Update an existing student by their original ID."""
        connection, cursor = self.get_db_connection()
        cursor.execute(
            """
            UPDATE Student 
            SET id_number = %s, first_name = %s, last_name = %s, course = %s, 
                year_level = %s, gender = %s, profile_image = %s 
            WHERE id_number = %s
            """,
            (self.id_number, self.first_name, self.last_name, self.course, self.year_level, self.gender, self.profile_image, original_id_number)
            )
        connection.commit()
        self.close_connection(connection, cursor)
        return self.id_number
    
    @classmethod
    def delete(cls, id_number):
        """Delete a student and their profile image from Cloudinary and the database."""
        connection, cursor = cls.get_db_connection()
        try:
            cursor.execute("SELECT profile_image FROM Student WHERE id_number = %s", (id_number,))
            result = cursor.fetchone()
            if result and result[0]:
                image_url = result[0]
                cls.delete_profile_image(image_url) 


            cursor.execute("DELETE FROM Student WHERE id_number = %s", (id_number,))
            connection.commit()
        finally:
            cls.close_connection(connection, cursor)
            return True
    
    @classmethod
    def upload_profile_image(cls, file):
        """Upload a profile image to Cloudinary and return the URL."""
        if not file:
            return None
            
        upload_result = cloudinary.uploader.upload(file, folder="students")
        return upload_result.get("url")
    
    @classmethod
    def delete_profile_image(cls, image_url):
        """Delete a profile image from Cloudinary."""
        if not image_url:
            return
        public_id = os.path.splitext(os.path.basename(urlparse(image_url).path))[0]
        cloudinary.uploader.destroy(f"students/{public_id}")


class Course(BaseModel):
    """Model class for Course entity."""
    
    def __init__(self, course_code=None, course_name=None, college=None):
        self.course_code = course_code
        self.course_name = course_name
        self.college = college
    
    @classmethod
    def get_all(cls):
        """Get all courses."""
        connection, cursor = cls.get_db_connection()
        
        cursor.execute("SELECT * FROM Course")
        courses = cursor.fetchall()
        
        cls.close_connection(connection, cursor)
        return courses
    
    @classmethod
    def get_course_codes(cls):
        """Get all course codes for form choices."""
        connection, cursor = cls.get_db_connection()
        
        cursor.execute("SELECT course_code FROM Course")
        courses = cursor.fetchall()
        
        cls.close_connection(connection, cursor)
        return [course[0] for course in courses]
    
    @classmethod
    def get_by_code(cls, course_code):
        """Get a course by code."""
        connection, cursor = cls.get_db_connection()
        
        cursor.execute("SELECT * FROM Course WHERE course_code = %s", (course_code,))
        course = cursor.fetchone()
        
        cls.close_connection(connection, cursor)
        return course
    
    @classmethod
    def search(cls, search_by, search_value):
        """Search for courses by various fields."""
        connection, cursor = cls.get_db_connection()
        
        pairs = {
            "Course code": "course_code",
            "Course name": "course_name",
            "College": "college"
        }
        
        field = pairs.get(search_by)
        if not field:
            return []
            
        cursor.execute(f"SELECT * FROM Course WHERE {field} LIKE %s", 
                      (f'%{search_value}%',))
        courses = cursor.fetchall()
        
        cls.close_connection(connection, cursor)
        return courses
    
    def create(self):
        """Insert a new course into the database."""
        connection, cursor = self.get_db_connection()
        cursor.execute(
            "INSERT INTO Course (course_code, course_name, college) VALUES (%s, %s, %s)",
            (self.course_code, self.course_name, self.college),
                )
        connection.commit()
        self.close_connection(connection, cursor)
        return self.course_code

    def update(self, original_code):
        """Update an existing course by course code."""
        connection, cursor = self.get_db_connection()
        cursor.execute(
            """
            UPDATE Course 
            SET course_code = %s, course_name = %s, college = %s
            WHERE course_code = %s
            """,
            (self.course_code, self.course_name, self.college, original_code),
            )
        connection.commit()
        self.close_connection(connection, cursor)
        return self.course_code
    
    @classmethod
    def delete(cls, course_code):
        """Delete a course by code."""
        connection, cursor = cls.get_db_connection()
        
        cursor.execute("DELETE FROM Course WHERE course_code = %s", (course_code,))
        connection.commit()
        
        cls.close_connection(connection, cursor)
        return True


class College(BaseModel):
    """Model class for College entity."""
    
    def __init__(self, college_code=None, college_name=None):
        self.college_code = college_code
        self.college_name = college_name
    
    @classmethod
    def get_all(cls):
        """Get all colleges."""
        connection, cursor = cls.get_db_connection()
        
        cursor.execute("SELECT * FROM College")
        colleges = cursor.fetchall()
        
        cls.close_connection(connection, cursor)
        return colleges
    
    @classmethod
    def get_college_codes(cls):
        """Get all college codes for form choices."""
        connection, cursor = cls.get_db_connection()
        
        cursor.execute("SELECT college_code FROM College")
        colleges = cursor.fetchall()
        
        cls.close_connection(connection, cursor)
        return [college[0] for college in colleges]
    
    @classmethod
    def get_by_code(cls, college_code):
        """Get a college by code."""
        connection, cursor = cls.get_db_connection()
        
        cursor.execute("SELECT * FROM College WHERE college_code = %s", (college_code,))
        college = cursor.fetchone()
        
        cls.close_connection(connection, cursor)
        return college
    
    @classmethod
    def search(cls, search_by, search_value):
        """Search for colleges by various fields."""
        connection, cursor = cls.get_db_connection()
        
        pairs = {
            "College code": "college_code",
            "College name": "college_name"
        }
        
        field = pairs.get(search_by)
        if not field:
            return []
            
        cursor.execute(f"SELECT * FROM College WHERE {field} LIKE %s", 
                      (f'%{search_value}%',))
        colleges = cursor.fetchall()
        
        cls.close_connection(connection, cursor)
        return colleges
    
    def create(self):
        """Insert a new college into the database."""
        connection, cursor = self.get_db_connection()
        cursor.execute(
            "INSERT INTO College (college_code, college_name) VALUES (%s, %s)",
            (self.college_code, self.college_name),
                )
        connection.commit()
        self.close_connection(connection, cursor)
        return self.college_code

    def update(self, original_code):
        """Update an existing college by college code."""
        connection, cursor = self.get_db_connection()
        cursor.execute(
            """
            UPDATE College 
            SET college_code = %s, college_name = %s
            WHERE college_code = %s
            """,
            (self.college_code, self.college_name, original_code),
                )
        connection.commit()
        self.close_connection(connection, cursor)
        return self.college_code
    
    @classmethod
    def delete(cls, college_code):
        """Delete a college by code."""
        connection, cursor = cls.get_db_connection()
        
        cursor.execute("DELETE FROM College WHERE college_code = %s", (college_code,))
        connection.commit()
        
        cls.close_connection(connection, cursor)
        return True