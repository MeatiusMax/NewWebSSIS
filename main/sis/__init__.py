from flask import Flask
from flaskext.mysql import MySQL

# Initialize Flask application
application = Flask(__name__)


# Configure application
application.config["SECRET_KEY"] = "12345"
application.config["MYSQL_DATABASE_HOST"] = "localhost"
application.config["MYSQL_DATABASE_USER"] = "root"
application.config["MYSQL_DATABASE_PASSWORD"] = ""
application.config["MYSQL_DATABASE_DB"] = "flask"

# Initialize MySQL
my_sql = MySQL()
my_sql.init_app(application)

# Register blueprints
from sis.routes import student_bp
from sis.routes import course_bp
from sis.routes import college_bp
application.register_blueprint(student_bp)
application.register_blueprint(course_bp)
application.register_blueprint(college_bp)