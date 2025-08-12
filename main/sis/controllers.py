from flask import render_template, url_for, flash, redirect, request
from sis.forms import StudentForm, SearchForm, CourseForm, CourseSearchForm, CollegeForm, CollegeSearchForm
from sis.model import Student, Course, College


def students():
    page = request.args.get('page', 1, type=int)
    students_data = Student.get_all(page=page)
    form = SearchForm()
    return render_template(
        "students.html",
        title="Students",
        students=students_data[0],
        total_students=students_data[1],
        total_pages=students_data[2],
        current_page=page,
        form=form
    )


def add_student():
    form = StudentForm()
    form.course.choices = Course.get_course_codes()
    if request.method == "POST" and form.validate_on_submit():
        student = Student(
            id_number=form.id_number.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            course=form.course.data,
            year_level=form.year_level.data,
            gender=form.gender.data,
            profile_image=None
        )
        student.create()
        flash(f"Student {form.id_number.data} has been added successfully.", "success")
        return redirect (url_for("student_routes.change_profile_pic", id_number=form.id_number.data))
    return render_template("addstudent.html", title="Add a Student", legend="Add a Student", form=form)


def update_student(id_number):
    student_data = Student.get_by_id(id_number)
    if not student_data:
        flash("Student not found.", "danger")
        return redirect(url_for("student_routes.students"))
    form = StudentForm()
    form.course.choices = Course.get_course_codes()
    if form.validate_on_submit():
        profile_image_url = student_data[6]
        if form.profile_image.data:
            if student_data[6]:
                Student.delete_profile_image(student_data[6])
            profile_image_url = Student.upload_profile_image(form.profile_image.data)
        student = Student(
            id_number=form.id_number.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            course=form.course.data,
            year_level=form.year_level.data,
            gender=form.gender.data,
            profile_image=profile_image_url
        )
        student.update(original_id_number=id_number)
        flash(f"Student {id_number}'s records have been updated successfully.", "success")
        return redirect(url_for("student_routes.students"))
    elif request.method == "GET":
        form.id_number.data = student_data[0]
        form.first_name.data = student_data[1]
        form.last_name.data = student_data[2]
        form.course.data = student_data[3]
        form.year_level.data = student_data[4]
        form.gender.data = student_data[5]
    return render_template(
        "addstudent.html", title="Update Student Records", 
        legend="Update", form=form, is_update=True,student=student_data
    )


def delete_student(id_number):
    Student.delete(id_number)
    flash(f"Student {id_number}'s records have been deleted successfully.", "danger")
    return redirect(url_for("student_routes.students"))


def search_students():
    form = SearchForm()
    current_page = request.args.get('page', 1, type=int)
    search_value = request.args.get('this')
    search_by = request.args.get('search_by')
    if search_value and search_by:
        students_data = Student.search(search_by=search_by, search_value=search_value, page=current_page)
    else:
        students_data = [[], 0, 0]
    return render_template("students.html", title="Students", students=students_data[0],
                           form=form, current_page=current_page, total_pages=students_data[2],
                           search_value=search_value, search_by=search_by)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_MB=2

def allowed_file(filename):
    '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    return redirect ('student_routes.change_profile_pic')


def change_profile_pic(id_number):
    student = Student.get_by_id(id_number)
    if request.method == "POST":
        profile_image = request.files.get("profile_image")
        if profile_image and allowed_file(profile_image.filename):
            profile_image.stream.seek(0, 2)
            file_size = profile_image.stream.tell()
            profile_image.stream.seek(0) 
            if file_size > MAX_FILE_MB * 1024 * 1024:
                flash(f"File must be smaller than {MAX_FILE_MB} MB.", "danger")
                return redirect('student_routes.change_profile_pic')
            image_url = Student.upload_profile_image(profile_image)
            connection, cursor = Student.get_db_connection()
            cursor.execute(
                "UPDATE Student SET profile_image = %s WHERE id_number = %s",
                (image_url, id_number)
            )
            connection.commit()
            Student.close_connection(connection, cursor)
            flash(f"Profile picture updated successfully.", "success")
        else:
            flash("Invalid file type. Only JPG, JPEG, and PNG are allowed.", "danger")

        add_update = request.args.get("add","update")
        if add_update == "update":
            return redirect(url_for('student_routes.update_student', id_number = id_number))
        else:
            return redirect( url_for('student_routes.students'))    
    return render_template(
        "change_profile_pic.html", title="Change Profile Picture", student=student
    )

def courses():
    courses_list = Course.get_all()
    form = CourseSearchForm()
    return render_template("courses.html", title="Courses", courses=courses_list, form=form)


def add_course():
    form = CourseForm()
    form.college.choices = College.get_college_codes()
    if request.method == "POST" and form.validate_on_submit():
        course = Course(
            course_code=form.course_code.data,
            course_name=form.course_name.data,
            college=form.college.data
        )
        course.create()
        flash(f"Course {form.course_code.data} has been added successfully.", "success")
        return redirect(url_for("course_routes.courses"))
    return render_template("addcourse.html", title="Add a Course", legend="Add a Course", form=form)


def update_course(course_code):
    course_data = Course.get_by_code(course_code)
    if not course_data:
        flash("Course not found.", "danger")
        return redirect(url_for("course_routes.courses"))
    form = CourseForm()
    form.college.choices = College.get_college_codes()
    if form.validate_on_submit():
        course = Course(
            course_code=form.course_code.data,
            course_name=form.course_name.data,
            college=form.college.data
        )
        course.update(original_code=course_code)
        flash(f"Course {form.course_code.data}'s records have been updated successfully.", "success")
        return redirect(url_for("course_routes.courses"))
    elif request.method == "GET":
        form.course_code.data = course_data[0]
        form.course_name.data = course_data[1]
        form.college.data = course_data[2]
        form.add.label.text = "Update"
    return render_template("addcourse.html", title="Update Course Records", legend="Update Course Records", form=form, is_update=True)


def delete_course(course_code):
    Course.delete(course_code)
    flash(f"Course {course_code} has been deleted successfully.", "danger")
    return redirect(url_for("course_routes.courses"))


def search_courses():
    form = CourseSearchForm()
    search_value = request.args.get('this')
    search_by = request.args.get('search_by')
    if search_value and search_by:
        courses_list = Course.search(search_by=search_by, search_value=search_value)
    else:
        courses_list = []
    return render_template("courses.html", title="Courses", courses=courses_list, form=form)

def colleges():
    colleges_list = College.get_all()
    form = CollegeSearchForm()
    return render_template("colleges.html", title="Colleges", colleges=colleges_list, form=form)


def add_college():
    form = CollegeForm()
    if request.method == "POST" and form.validate_on_submit():
        college = College(
            college_code=form.college_code.data,
            college_name=form.college_name.data
        )
        college.create()
        flash(f"College {form.college_code.data} has been added successfully.", "success")
        return redirect(url_for("college_routes.colleges"))
    return render_template("addcollege.html", title="Add a College", legend="Add a College", form=form)


def update_college(college_code):
    college_data = College.get_by_code(college_code)
    if not college_data:
        flash("College not found.", "danger")
        return redirect(url_for("college_routes.colleges"))
    form = CollegeForm()
    if form.validate_on_submit():
        college = College(
            college_code=form.college_code.data,
            college_name=form.college_name.data
        )
        college.update(original_code=college_code)
        flash(f"College {form.college_code.data}'s records have been updated successfully.", "success")
        return redirect(url_for("college_routes.colleges"))
    elif request.method == "GET":
        form.college_code.data = college_data[0]
        form.college_name.data = college_data[1]
        form.add.label.text = "Update"
    return render_template("addcollege.html", title="Update College Records", legend="Update College Records", form=form, is_update=True)


def delete_college(college_code):
    College.delete(college_code)
    flash(f"College {college_code} has been deleted successfully.", "danger")
    return redirect(url_for("college_routes.colleges"))


def search_colleges():
    form = CollegeSearchForm()
    search_value = request.args.get('this')
    search_by = request.args.get('search_by')
    if search_value and search_by:
        colleges_list = College.search(search_by=search_by, search_value=search_value)
    else:
        colleges_list = []
    return render_template("colleges.html", title="Colleges", colleges=colleges_list, form=form)