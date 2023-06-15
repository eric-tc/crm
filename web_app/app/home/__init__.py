from flask import Blueprint

home = Blueprint("home", __name__)

db_blueprint = Blueprint('db_blueprint', "database_blueprint")

from . import views
