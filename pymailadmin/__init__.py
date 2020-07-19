import flask
import flask_bootstrap

from pymailadmin import utils, debug, models, manage, configuration


def create_app_from_config(configApp, configAuth, configMail):
  """ Create a new application based on the given configuration
      - initialises flask app as 'app'
      - adds flask cli management commands: manage.pymailadmin
      - uses bootstrap to load js and css: flask_bootstrap
      - initialises application configuration
      - initialises authentication configuration
      - initialises mail configuration
      - initialises utilities
        - models.db
        - utils.babel
        - utils.limiter
        - utils.login
        - utils.login.user_loader
        - utils.migrate
        - utils.proxy
      - initialises debugging
      - import views
  """

  # Initialise flask framework
  app = flask.Flask(__name__)
  app.cli.add_command(manage.pymailadmin)

  # Bootstrap is used for basic JS and CSS loading
  # TODO: remove this and use statically generated assets instead
  app.bootstrap = flask_bootstrap.Bootstrap(app)

  # Initialise application configuration
  configApp.init_app(app)

  # Initialise authentcation configuration
  configAuth.init_auth(app)

  # Initialise mail configuration
  configMail.init_mail(app)

  # Initialise utility; models
  models.db.init_app(app)
  utils.babel.init_app(app)
  utils.limiter.init_app(app)
  utils.login.init_app(app)
  utils.login.user_loader(models.User.get)
  utils.migrate.init_app(app, models.db)
  utils.proxy.init_app(app)
  
  # Initialize debugging tools
  if app.configApp.get("DEBUG"):
    debug.toolbar.init_app(app)
    if app.configApp.get("DEBUG_WSGI"):
      debug.profiler.init_app(app)

  # Inject the default variables in the Jinja parser
  # TODO: move this to blueprints when needed
  @app.context_processor
  def inject_defaults():
    """ Uses Jinja parser to set signup domain.
        SET VAR: configuration.configMail.MAIL_CONFIG[DOMAIN]
        FOR: app.configMail[MAIL_DOMAIN]
    """
    
    signup_domains = models.Domain.query.filter_by(signup_enabled=True).all()
    return dict(
      signup_domains=signup_domains,
      config=app.configMail
    )

  # Import views
  from pymailadmin import ui, authentication
  app.register_blueprint(ui.ui, url_prefix='/ui')
  app.register_blueprint(authentication.authentication, url_prefix='/authentication')

  return app

def create_app():
""" Main entrypoint into flask application.
    Creates 3 configuration objects:
    1) configuration.AppConfigManager()
    2) configuration.AuthConfigManager()
    3) configuration.MailConfigManager()
"""  

configApp = configuration.AppConfigManager()
  configAuth = configuration.AuthConfigManager()
  configMail = configuration.MailConfigManager()
  return create_app_from_config(configApp, configAuth, configMail)
