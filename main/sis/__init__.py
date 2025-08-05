from flask import Flask
from flaskext.mysql import MySQL
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Flask application
application = Flask(__name__)


# Configure application

application.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
application.config["MYSQL_DATABASE_HOST"] = os.getenv("MYSQL_DATABASE_HOST")
application.config["MYSQL_DATABASE_USER"] = os.getenv("MYSQL_DATABASE_USER")
application.config["MYSQL_DATABASE_PASSWORD"] = os.getenv("MYSQL_DATABASE_PASSWORD")
application.config["MYSQL_DATABASE_DB"] = os.getenv("MYSQL_DATABASE_DB")
print("Connecting as:", application.config["MYSQL_DATABASE_USER"])
print("Password:", application.config["MYSQL_DATABASE_PASSWORD"])

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