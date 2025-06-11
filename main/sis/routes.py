from flask import render_template, url_for, request, redirect, flash
from sis.forms import CourseSearchForm, SearchForm, StudentForm, CourseForm, CollegeSearchForm, CollegeForm
from sis import application
from sis.model import Student, Course, College

@application.route("/students", methods=["POST", "GET"])
@application.route("/", methods=["POST", "GET"])
def students():
    page = request.args.get('page', 1, type=int)
    students, total_students, total_pages = Student.get_all(page=page)
    form = SearchForm()

    return render_template(
        "students.html", 
        title="Students", 
        students=students, 
        form=form, 
        total_students=total_students,
        total_pages=total_pages, 
        current_page=page
    )

@application.route("/addstudent", methods=["POST", "GET"])
def addstudent():
    form = StudentForm()
    form.course.choices = Course.get_course_codes()

    if request.method == "POST" and form.validate_on_submit():
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
        
        student.create()
        flash(f"Student {form.id_number.data} has been added successfully.", "success")
        return redirect(url_for("students"))

    return render_template("addstudent.html", title="Add a Student", legend="Add a Student", form=form)

@application.route("/update/<id_number>", methods=["POST", "GET"])
def update(id_number):
    student_data = Student.get_by_id(id_number)
    if not student_data:
        flash("Student not found.", "danger")
        return redirect(url_for("students"))
        
    form = StudentForm()
    form.course.choices = Course.get_course_codes()

    if form.validate_on_submit():
        profile_image_url = student_data[6]
        if form.profile_image.data:
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
        return redirect(url_for("students"))

    elif request.method == "GET":
        form.id_number.data = student_data[0]
        form.first_name.data = student_data[1]
        form.last_name.data = student_data[2]
        form.course.data = student_data[3]
        form.year_level.data = student_data[4]
        form.gender.data = student_data[5]

    return render_template(
        "addstudent.html", title="Update Student Records", legend="Update", form=form, is_update=True)

@application.route("/delete/<id_number>", methods=["POST", "GET"])
def delete(id_number):
    Student.delete(id_number)
    flash(f"Student {id_number}'s records have been deleted successfully.", "danger")
    return redirect(url_for("students"))

@application.route("/search", methods=["GET"])
def search():
    form = SearchForm()
    
    current_page = request.args.get('page', 1, type=int)
    search_value = request.args.get('this')
    search_by = request.args.get('search_by')

    if search_value and search_by:
        students, total_students, total_pages = Student.search(
            search_by=search_by, 
            search_value=search_value,
            page=current_page
        )
    else:
        students, total_students, total_pages = [], 0, 0

    return render_template("students.html", title="Students", 
                           students=students, form=form, 
                           current_page=current_page, total_pages=total_pages, 
                           search_value=search_value, search_by=search_by)

@application.route("/courses")
def courses():
    courses = Course.get_all()
    form = CourseSearchForm()

    return render_template("courses.html", title="Courses", 
                            courses=courses, form=form)

@application.route("/addcourse", methods=["POST", "GET"])
def addcourse():
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
        return redirect(url_for("courses"))

    return render_template("addcourse.html", title="Add a Course", 
                            legend="Add a Course", form=form)

@application.route("/updatecourse/<course_code>", methods=["POST", "GET"])
def update_a_course(course_code):
    course_data = Course.get_by_code(course_code)
    if not course_data:
        flash("Course not found.", "danger")
        return redirect(url_for("courses"))
        
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
        return redirect(url_for("courses"))

    elif request.method == "GET":
        form.course_code.data = course_data[0]
        form.course_name.data = course_data[1]
        form.college.data = course_data[2]
        form.add.label.text = "Update"

    return render_template("addcourse.html", title="Update Course Records", 
                           legend="Update Course Records", form=form, is_update=True)

@application.route("/deletecourse/<course_code>", methods=["POST", "GET"])
def delete_a_course(course_code):
    Course.delete(course_code)
    flash(f"Course {course_code} has been deleted successfully.", "danger")
    return redirect(url_for("courses"))

@application.route("/course_search", methods=["GET"])
def course_search():
    form = CourseSearchForm()
    
    search_value = request.args.get('this')
    search_by = request.args.get('search_by')

    if search_value and search_by:
        courses = Course.search(search_by=search_by, search_value=search_value)
    else:
        courses = []

    return render_template("courses.html", title="Courses", 
                            courses=courses, form=form)

@application.route("/colleges")
def colleges():
    colleges = College.get_all()
    form = CollegeSearchForm()

    return render_template("colleges.html", title="Colleges", 
                            colleges=colleges, form=form)

@application.route("/addcollege", methods=["POST", "GET"])
def addcollege():
    form = CollegeForm()

    if request.method == "POST" and form.validate_on_submit():
        college = College(
            college_code=form.college_code.data,
            college_name=form.college_name.data
        )
        
        college.create()
        flash(f"College {form.college_code.data} has been added successfully.", "success")
        return redirect(url_for("colleges"))

    return render_template("addcollege.html", title="Add a College", 
                            legend="Add a College", form=form)

@application.route("/updatecollege/<college_code>", methods=["POST", "GET"])
def update_a_college(college_code):
    college_data = College.get_by_code(college_code)
    if not college_data:
        flash("College not found.", "danger")
        return redirect(url_for("colleges"))
        
    form = CollegeForm()

    if form.validate_on_submit():
        college = College(
            college_code=form.college_code.data,
            college_name=form.college_name.data
        )
        
        college.update(original_code=college_code)
        flash(f"College {form.college_code.data}'s records have been updated successfully.", "success")
        return redirect(url_for("colleges"))

    elif request.method == "GET":
        form.college_code.data = college_data[0]
        form.college_name.data = college_data[1]
        form.add.label.text = "Update"

    return render_template("addcollege.html", title="Update College Records", 
                           legend="Update College Records", form=form, is_update=True)

@application.route("/deletecollege/<college_code>", methods=["POST", "GET"])
def delete_a_college(college_code):
    College.delete(college_code)
    flash(f"College {college_code} has been deleted successfully.", "danger")
    return redirect(url_for("colleges"))

@application.route("/college_search", methods=["GET"])
def college_search():
    form = CollegeSearchForm()
    
    search_value = request.args.get('this')
    search_by = request.args.get('search_by')

    if search_value and search_by:
        colleges = College.search(search_by=search_by, search_value=search_value)
    else:
        colleges = []

    return render_template("colleges.html", title="Colleges", 
                            colleges=colleges, form=form)

@application.route("/change_profile_pic/<id_number>", methods=["POST", "GET"])
def change_profile_pic(id_number):
    student = Student.get_by_id(id_number)

    if not student:
        flash("Student not found!", "danger")
        return redirect(url_for("students"))

    if request.method == "POST":
        profile_image = request.files.get("profile_image")
        
        if profile_image:
            image_url = Student.upload_profile_image(profile_image)
            
            student_obj = Student(id_number=id_number, profile_image=image_url)
            
            connection, cursor = Student.get_db_connection()
            cursor.execute(
                "UPDATE Student SET profile_image = %s WHERE id_number = %s",
                (image_url, id_number)
            )
            connection.commit()
            Student.close_connection(connection, cursor)
            
            flash(f"Profile picture for student {id_number} updated successfully.", "success")
        else:
            flash("No image selected for upload.", "warning")
            
        return redirect(url_for("students"))

    return render_template(
        "change_profile_pic.html", title="Change Profile Picture", student=student
    )