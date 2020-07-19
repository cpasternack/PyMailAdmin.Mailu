import flask


authentication = flask.Blueprint('authentication', __name__, template_folder='templates')


from pymailadmin.authentication.views import *
