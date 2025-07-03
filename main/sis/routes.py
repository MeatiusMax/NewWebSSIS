from flask import Blueprint
from sis.controllers import (
    students, add_student, update_student, delete_student, search_students,change_profile_pic,
    courses, add_course, update_course, delete_course, search_courses,
    colleges, add_college, update_college, delete_college, search_colleges
)

student_bp = Blueprint('student_routes', __name__)

student_bp.route("/students", methods=["POST", "GET"])(students)
student_bp.route("/", methods=["POST", "GET"])(students)
student_bp.route("/addstudent", methods=["POST", "GET"])(add_student)
student_bp.route("/update/<id_number>", methods=["POST", "GET"])(update_student)
student_bp.route("/delete/<id_number>", methods=["POST", "GET"])(delete_student)
student_bp.route("/search", methods=["GET"])(search_students)
student_bp.route("/change_profile_pic/<id_number>", methods=["POST", "GET"])(change_profile_pic)

course_bp = Blueprint('course_routes', __name__)

course_bp.route("/courses")(courses)
course_bp.route("/addcourse", methods=["POST", "GET"])(add_course)
course_bp.route("/updatecourse/<course_code>", methods=["POST", "GET"])(update_course)
course_bp.route("/deletecourse/<course_code>", methods=["POST", "GET"])(delete_course)
course_bp.route("/course_search", methods=["GET"])(search_courses)

college_bp = Blueprint('college_routes', __name__)

college_bp.route("/colleges")(colleges)
college_bp.route("/addcollege", methods=["POST", "GET"])(add_college)
college_bp.route("/updatecollege/<college_code>", methods=["POST", "GET"])(update_college)
college_bp.route("/deletecollege/<college_code>", methods=["POST", "GET"])(delete_college)
college_bp.route("/college_search", methods=["GET"])(search_colleges)

