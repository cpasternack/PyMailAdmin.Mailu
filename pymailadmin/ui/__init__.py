from flask import Blueprint


ui = Blueprint('ui', __name__, static_folder='static', template_folder='templates')

from pymailadmin.ui.views import *
