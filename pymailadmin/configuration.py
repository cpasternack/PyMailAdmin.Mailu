import os

from socrate import system

class AppConfigManager(dict):
  """ AppConfigManager
      Default configuration manager class that uses os.environ
      and socrate to get/set/resolve variables, then stores
      values into a dictionary
  """

  FLASK_CONFIG={
    'DEBUG':'False',
    'DEBUG_WSGI':'False',
    'RUN_PORT':5080,
    'INITIAL_ADMIN_ACCOUNT':'pymailadmin',
    'INITIAL_ADMIN_DOMAIN':'mail.mailu.io',
    'INITIAL_ADMIN_PW':'pymailadmin',
    'LOGLEVEL':'info',
    'RESOLVER_ATTEMPTS': '5',
    'RESOLVER_TIMEOUT_MIN': '2'
    'RESOLVER_TIMEOUT_MAX': '5'
  }
  APP_CONFIG={
    'BABEL_DEFAULT_LOCALE':'en',
    'BABEL_DEFAULT_TIMEZONE':'UTC',
    'BOOTSTRAP_SERVE_LOCAL':'True',
    'DOMAIN_REGISTRATION': 'False',
    'PASSWORD_SCHEME':'BLF-CRYPT',
    'RECAPTCHA_PRIVATE_KEY':'',
    'RECAPTCHA_PUBLIC_KEY':'',
    'SITENAME':'PyMailAdmin',
    'TEMPLATES_AUTO_RELOAD':'True',
    'WEBSITE':'https://mail.mailu.io',
    'WEB_ADMIN':'/admin',
    'WEB_AUTH':'/authentication',
    'WEB_WEBMAIL':'/webmail'    
  }
  NET={
    'ADMIN': '',
    'AV': '',
    'IMAP': '',
    'LMTP': '',
    'POP3': '',
    'POSTGRES': '',
    'PROXY': '',
    'REDIS': '',
    'SMTP': '',
    'SPAM': '',
    'STATS': '',
    'WEBDAV': '',
    'WEBMAIL': ''
  }
  HOST={
    'ADMIN': 'mail_pymailadmin_1',
    'AV': 'mail_antivirus_1',
    'IMAP': 'mail_imap_1',
    'LMTP': 'mail_imap_1',
    'POP3': 'mail_imap_1',
    'POSTGRES': 'mail_postgres_1',
    'PROXY': 'mail_proxy_1',
    'REDIS': 'mail_redis_1',
    'SMTP': 'mail_smtp_1',
    'SPAM': 'mail_spam_1',
    'STATS': 'mail_stats_1',
    'WEBDAV': 'mail_webdav_1',
    'WEBMAIL': 'mail_webmail_1'
  }
  PORT={
    'IMAP_PLAIN': '143',
    'IMAP_TLS': '993',
    'POP3_PLAIN': '110',
    'POP3_TLS': '995',
    'SMTP_AUTH': '465',
    'SMTP_PLAIN': '25',
    'SMTP_TLS': '587',
    'SPAM': '',
    'STATS': '',
    'WEBDAV': '',
    'WEBMAIL_IMAP_PLAIN': '10143',
    'WEBMAIL_IMAP_TLS': '10993',
    'WEBMAIL_SMTP_PLAIN':'10025',
    'WEBMAIL_SMTP_TLS': '10587'
  }

  def __init__(self):
    """ initialise class object"""
    
    self.configApp = dict()
  
  def get_host_address(self, name):
    """ resolve addresses from internal dictionary
        or socrate system resolver
    """
    
    if name in self.NET:
      return self.NET[name]
    else:
      return system.resolve_address(self.HOST['{}'.format(name)])

  def resolve_hosts(self):
    """ resolve the names of service host servers
        by: hostname, pre-populated lookup
        (uses socrate, tencity back-off timing)
    """
  
    for key, value in HOST.items():
      if self.NET[key] == "" or self.NET[key] is None:
        self.configApp['{}_ADDRESS'].format(key) \
          = self.get_host_address(value)
      else:
        self.configApp['{}_ADDRESS'].format(key) \
          = self.NET[key]
  
  @staticmethod
  def get_shell_var(prefix, key):
    """ get kvp from os environment """

    if prefix+'_{}'.format(key) in os.environ:
      return os.environ.get(prefix+'_{}'.format(key))
    else:
      return "" 

  def init_framework_config(self):
    """ Initialise flask app variables from environment
        or default values

        NOTE: The prefix 'FLASK' from shell values
        is not used internally!

    """
    
    for key in FLASK_CONFIG.items():
      if self.FLASK_CONFIG[key] == "" or self.FLASK_CONFIG[key] is None:
        self.configApp['{}'].format(key) = AppConfigManager.get_shell_var('FLASK', key)  
      else:
        self.configApp['{}'].format(key) = AppConfigManager.get_shell_var(key)

  def init_app_config(self):
    """ Initialise web application configuration from
        environment or default values
    """
  
    for key in APP_CONFIG.items():
      if self.APP_CONFIG[key] == "" or self.APP_CONFIG[key] is None:
        self.configApp['APP_{}'].format(key) = AppConfigManager.get_shell_var('APP', key)  
      else:
        self.configApp['APP_{}'].format(key) = AppConfigManager.get_shell_var(key)
  
  def init_network_config(self):
    """ Initialise web application configuration from
        environment or default values
        
        NOTE: The prefix 'PORTS' from the shell values gets
        swapped around for internal use. ex: $PORTS_IMAP_PLAIN
        becomes configApp['IMAP_PLAIN_PORT'] for readability.
        'HOST_' DOES NOT
      
        TODO: harmonise across code
    """
  
    for key in HOST.items():
      if self.HOST[key] == "" or self.HOST[key] is None:
        self.configApp['HOST_{}'].format(key) = AppConfigManager.get_shell_var('HOST', key)  
      else:
        self.configApp['HOST_{}'].format(key) = AppConfigManager.get_shell_var(key)

    for key in NET.items():
      if self.NET[key] == "" or self.NET[key] is None:
        self.configApp['{}_ADDRESS'].format(key) = AppConfigManager.get_shell_var('NET', key)  
      else:
        self.configApp['{}_ADDRESS'].format(key) = AppConfigManager.get_shell_var(key)
    
    for key in PORT.items():
      if self.PORT[key] == "" or self.PORT[key] is None:
        self.configApp['{}_PORT'].format(key) = AppConfigManager.get_shell_var('PORT', key)  
      else:
        self.configApp['{}_PORT'].format(key) = AppConfigManager.get_shell_var(key)


  def init_app(self, app):
    """ Initialise flask application configuration
        1) update the configuration dictionary with application configuration
        2) configure variables from os shell variables (if set)
        3) resolve app; mail; redis, etc. hostnames
        4) update the application
    """

    # 1
    self.configApp.update(app.configApp)
    # 2 
    self.init_framework_config()
    self.init_app_config()
    self.init_network_config()
    # 3
    self.resolve_hosts()
    # 4
    app.configApp = self

  def setdefault(self, key, value):
    if key not in self.configApp:
        self.configApp[key] = value
    return self.configApp[key]

  def get(self, *args):
    return self.configApp.get(*args)

  def keys(self):
    return self.configApp.keys()

  def __getitem__(self, key):
    return self.configApp.get(key)

  def __setitem__(self, key, value):
    self.configApp[key] = value

  def __contains__(self, key):
    return key in self.configApp

class MailConfigManager(dict):
  """ initialise mail configuration
  """

  MAIL_CONFIG={
    'AUTH_RATELIMIT':'10/minute;1000/hour',
    'AUTH_RATELIMIT_SUBNET':'True',
    'DEFAULT_ALIASES': 10,
    'DEFAULT_QUOTA': 1000000000,
    'DEFAULT_USERS': 10,
    'DOMAIN':'mailu.io',
    'DMARC_RUA':'None',
    'DMARC_RUF':'None',
    'DKIM_SELECTOR':'dkim',
    'DKIM_PATH':'/dkim/{domain}.{selector}.key',
    'HOSTNAMES':'mail.mailu.io,alternative.mailu.io',
    'POSTMASTER':'postmaster',
    'QUOTA_STORAGE_URL':'redis://{0}/1',
    'RATELIMIT_STORAGE_URL':'redis://{0}/2',
    'RECIPIENT_DELIMITER':'+',
    'SECRET_KEY':'changeMe',
    'SUBNET':'192.168.0.0/24',
    'SUBNET6':'None',
    'WELCOME':'True',
    'WELCOME_SUBJECT':'Welcome to mail@{DOMAIN}',
    'WELCOME_BODY':'If you are reading this, your mail is configured!'
  }
  STATS_CONFIG{
    'ENABLE':'False',
    'INSTANCE_ID_PATH':'/data/instance',
    'ENDPOINT':'0.{}.stats.{MAIL_CONFIG[DOMAIN]}'
  }
  
  def __init__(self):
    """ Initialise the application mail variables """

    self.configMail = dict()

  def init_mail_config(self):
    """ """
   
    for key in MAIL_CONFIG.items():
      if self.MAIL_CONFIG[key] == "" or self.MAIL_CONFIG[key] is None:
        self.configMail['MAIL_{}'].format(key) = AppConfigManager.get_shell_var('MAIL', key)  
      else:
        self.configMail['MAIL_{}'].format(key) = AppConfigManager.get_shell_var(key)

    self.configMail['MAIL_RATELIMIT_STORAGE_URL'] \
      = 'redis://{0}/2'.format(AppConfigManager.configApp['REDIS_ADDRESS'])
    self.configMail['MAIL_QUOTA_STORAGE_URL'] \
      = 'redis://{0}/1'.format(AppConfigManager.configApp['REDIS_ADDRESS'])

  def init_stats_config(self):
    """ """
  
    for key in STATS_CONFIG.items():
      if self.STATS_CONFIG[key] == "" or self.STATS_CONFIG[key] is None:
        self.configMail['STATS_{}'].format(key) = AppConfigManager.get_shell_var('STATS', key)  
      else:
        self.configAuth['STATS_{}'].format(key) = AppConfigManager.get_shell_var(key)


  def init_mail(self, app):
    """ """

    # 1
    self.configMail.update(app.configMail)
    # 2
    self.init_mail_config()
    self.init_stats_config()

  def setdefault(self, key, value):
    if key not in self.configMail:
        self.configMail[key] = value
    return self.configMail[key]

  def get(self, *args):
    return self.configMail.get(*args)

  def keys(self):
    return self.configMail.keys()

  def __getitem__(self, key):
    return self.configMail.get(key)

  def __setitem__(self, key, value):
    self.configMail[key] = value

  def __contains__(self, key):
    return key in self.configMail

class AuthConfigManager(dict):
  """ initialise authentication server 
      configuration, including database
  """

  DB_TEMPLATE = {
    'postgresql': 'postgresql://{DB_USER}:{DB_PW}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
    'SQLALCHEMY_TRACK_MODIFICATIONS':'False'
  }
  
  DB_CONFIG = {
    'HOST': 'mail_postgres_1',
    'NAME': 'pymailadmin',
    'PORT': '5432',
    'PW': 'pymailadmin',
    'UPGRADE': 'False',
    'USER': 'pymailadmin',
  }
  def __init__(self):
  """ create empty dictionary to populate
  """

    self.configAuth = dict()

  def initAuth(self, app):
    """ loop over the environment variable starting with DB_
        if they aren't empty strings, add them to the configuration
        else use the default values in DB_CONFIG
    """

    for key in DB_CONFIG.items():
      if self.DB_CONFIG[key] == "" or self.DB_CONFIG[key] is None:
          self.configAuth['DB_{}'].format(key) = AppConfigManager.get_shell_var('DB', key)  
      else:
        self.configAuth['DB_{}'].format(key) = AppConfigManager.get_shell_var(key)

    # If we haven't set the sqlalchemy string in the os environment,
    # set it here with the postgres template
    if not os.environ.get('SQLALCHEMY_DATABASE_URI') == "" \
      or os.environ.get('SQLALCHEMY_DATABASE_URI') is None:
      template = self.DB_TEMPLATE[self.configAuth['postgresql']]
      self.configAuth['SQLALCHEMY_DATABASE_URI'] = template.format(**self.configAuth)
    
    if not os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS') == "" \
      and os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS') is not None:
      self.configAuth['SQLALCHEMY_TRACK_MODIFICATIONS'] \
        = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')

  def setdefault(self, key, value):
    if key not in self.configAuth:
      self.configAuth[key] = value
    return self.configAuth[key]

  def get(self, *args):
    return self.configAuth.get(*args)

  def keys(self):
    return self.configAuth.keys()

  def __getitem__(self, key):
    return self.configAuth.get(key)

  def __setitem__(self, key, value):
    self.configAuth[key] = value

  def __contains__(self, key):
    return key in self.configAuth
