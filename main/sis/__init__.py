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

# Import routes after initializing application
from sis import routes