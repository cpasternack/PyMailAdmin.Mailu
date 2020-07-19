from pymailadmin import models
from flask import current_app as app

import re
import urllib
import ipaddress
import socket
import tenacity
# import external_auth

""" Authentication "External" is handled by separate script
    "login" is depricated as a SASL option
"""

SUPPORTED_AUTH_METHODS = ["none", "plain", "external"]


PROTOCOL_STATUSES = {
  "authentication": ("Authentication credentials invalid", {
    "imap": "AUTHENTICATIONFAILED",
    "smtp": "535 5.7.8",
    "pop3": "-ERR Authentication failed"
  }),
}


def handle_authentication(headers):
  """ Handle an HTTP nginx authentication request
      See: http://nginx.org/en/docs/mail/ngx_mail_auth_http_module.html#protocol

      method: none, protocol: smtp inbound mail should be the only option
      for no authentication
  """
  
  client_ip = headers["Client-Ip"]
  auth_method = headers["Auth-Method"]
  auth_password = headers["Auth-Password"]
  auth_protocol = headers["Auth-Protocol"]
  auth_user = headers["Auth-User"]

  # Incoming mail, no authentication
  if auth_method == "none" and auth_protocol == "smtp":
    server, port = get_server(headers["Auth-Protocol"], False)
    return {
      "Auth-Status": "OK",
      "Auth-Server": server,
      "Auth-Port": port
    }
  elif auth_method == "plain":
    """ plain authentication:
        1) parse identifying headers
        2) query db for username (user email)
        3) query user password (encrypted-hash)
        4) query user permissions
        5) return code, server,fail-or-wait
    """
    is_authenticated = False
    request_username, request_password, request_ip = parse_credentials(headers)
    mail_user = models.User.query.get(request_username)

    """ If models.User.query returns an object that is not (None)
        check all mail_user tokens for existing session with user password (encrypted)
        then check that the client is requesting an enabled mail protocol
    """
    if mail_user:
      for token in mail_user.tokens:
        if (token.check_password(request_password) and
          (not token.ip or token.ip == request_ip)):
            is_authenticated = True
        if mail_user.check_password(request_password):
          is_authenticated = True
        if is_authenticated:
          if auth_protocol == "imap" and not mail_user.enable_imap:
            is_authenticated = False
          elif auth_protocol == "pop3" and not mail_user.enable_pop:
            is_authenticated = False

    if is_authenticated and mail_user.enabled:
      """ user is now authenticated and is enabled for the 
          requested protocol, so return to client:
          1) auth-status
          2) server
          3) port

          NOTE: originally this was copy+pasted from
          the "none" auth section, where the server would
          assume that the user was authenticated. This 
          was a security bug that is now considered fixed
      """
      server, port = get_server(auth_protocol, True)
      return {
        "Auth-Status": "OK",
        "Auth-Server": server,
        "Auth-Port": port
      }
    else:
      request_status, request_code = get_status(auth_protocol, "authentication")
      return {
        "Auth-Status": request_status,
        "Auth-Error-Code": request_code,
        "Auth-Wait": 0
      }
  elif auth_method == "external":
    is_authenticated = False
    is_authenticated = handle_external(headers)    
    server, port = get_server(auth_protocol, True)
    if is_authenticated:
      return {
        "Auth-Status": "OK",
        "Auth-Server": server,
        "Auth-Port": port
      }
    else:
      request_status, request_code = get_status(auth_protocol, "authentication")
      return {
        "Auth-Status": request_status,
        "Auth-Error-Code": request_code,
        "Auth-Wait": 0
      }
  else:
    # Unexpected
    return {}

def parse_credentials(headers):
  """ According to RFC2616 section 3.7.1 and PEP 3333, HTTP headers should
      be ASCII and are generally considered ISO8859-1. However when passing
      the password, nginx does not transcode the input UTF string, thus
      we need to manually decode.
  """
  
  raw_user_email = urllib.parse.unquote(headers["Auth-User"])
  user_email = raw_user_email.encode("iso8859-1").decode("utf8")
  raw_password = urllib.parse.unquote(headers["Auth-Pass"])
  password = raw_password.encode("iso8859-1").decode("utf8")
  ip = urllib.parse.unquote(headers["Client-Ip"])
  
  return user_email, password, ip


def handle_external(headers):
  """ Handle an HTTPS external authentication request
      https://tools.ietf.org/html/rfc4422
  """
  
  # process headers
  # call external authentication daemon/connector script

  # Not implemented
  return {}

def get_status(protocol, status):
  """ Return the proper error code depending on the protocol
  """
  
  status, codes = PROTOCOL_STATUSES[status]
  return status, codes[protocol]

def extract_host_port(host_and_port, default_port):
  """ Depricated
      Host port is matched from config, or fail
  """

  host, _, port = re.match('^(.*)(:([0-9]*))?$', host_and_port).groups()
  return host, int(port) if port else default_port

def get_server(mail_protocol, user_is_authenticated=False):
  """ Method sets the server address and port for proxying
      mail via Nginx 
      
      if the user is authenticated, redirect to webmail ports
  """

  if mail_protocol == "imap":
    if user_is_authenticated:
      hostname, port = app.configApp['IMAP_ADDRESS'], app.configApp['WEBMAIL_IMAP_PLAIN_PORT']
    else:
      hostname, port = app.configApp['IMAP_ADDRESS'], app.configApp['IMAP_PLAIN_PORT']
  elif mail_protocol == "pop3":
    hostname, port = app.configApp['POP3_ADDRESS'], app.configApp['POP3_PLAIN_PORT']
  elif mail_protocol == "smtp":
    if user_is_authenticated:
      hostname, port = app.configApp['WEBMAIL_SMTP_ADDRESS'], app.configApp['WEBMAIL_SMTP_PLAIN_PORT']
    else:
      hostname, port = app.configApp['SMTP_ADDRESS'], app.configApp['SMTP_PLAIN_PORT']
  else:
    hostname, port = None, None
  try:
    # test if hostname is already resolved to an ip adddress
    ipaddress.ip_address(hostname)
  except:
    # hostname is not an ip address - so we need to resolve it
    hostname = resolve_hostname(hostname)
  return hostname, port


def get_starttls_server(mail_protocol, user_is_authenticated=False):
  """ Method sets the server address and port for proxying
      STARTTLS mail via nginx
      
      if the user is authenticated, redirect to TLS webmail
  """

  if mail_protocol == "imap":
    if user_isauthenticated:
      hostname, port = app.configApp['IMAP_ADDRESS'], app.configApp['IMAP_TLS_PORT']
    else:
      hostname, port = app.configApp['IMAP_ADDRESS'], app.configApp['IMAP_PLAIN_PORT']
  elif mail_protocol == "pop3":
    if user_is_authenticated:
      hostname, port = app.configApp['POP3_ADDRESS'], app.configApp['POP3_TLS_PORT']
    else:
      hostname, port = app.configApp['POP3_ADDRESS'], app.configApp['POP3_PLAIN_PORT']
  elif mail_protocol == "smtp":
    if user_is_authenticated:
      hostname, port = app.configApp['SMTP_ADDRESS'], app.configApp['SMTP_TLS_PORT']
    else:
      hostname, port = app.configApp['SMTP_ADDRESS'], app.configApp['SMTP_PLAIN_PORT']
  else:
    return None, None

  try:
    # test if hostname is already resolved to an ip adddress
    ipaddress.ip_address(hostname)
  except:
    # hostname is not an ip address - so we need to resolve it
    hostname = resolve_hostname(hostname)
  return hostname, port


def get_tls_server(mail_protocol, user_is_authenticated=False):
  """ Method sets the server address and port for proxying
      TLS mail via nginx
      
      authenticated users only
  """

  if mail_protocol == "imap":
    if user_is_authenticated:
      hostname, port = app.configApp['IMAP_ADDRESS'], app.configApp['IMAP_TLS_PORT']
    else:
      hostname, port = None, None
  elif mail_protocol == "pop3":
    if user_is_authenticated:
      hostname, port = app.configApp['POP3_ADDRESS'], app.configApp['POP3_TLS_PORT']
    else:
      hostname, port = None, None
  elif mail_protocol == "smtp":
    if user_is_authenticated:
      hostname, port = app.configApp['SMTP_ADDRESS'], app.configApp['SMTP_TLS_PORT']
    else:
      hostname, port = None, None
  try:
    # test if hostname is already resolved to an ip adddress
    ipaddress.ip_address(hostname)
  except:
    # hostname is not an ip address - so we need to resolve it
    hostname = resolve_hostname(hostname)
  return hostname, port


@tenacity.retry(stop=tenacity.stop_after_attempt(app.configApp['RESOLVER_ATTEMPTS']),
                wait=tenacity.wait_exponential(min=app.configApp['RESOLVER_TIMEOUT_MIN'],
                 max=app.configApp['RESOLVER_TIMEOUT_MAX']))
def resolve_hostname(hostname):
    """ This function uses system DNS to resolve a hostname.
        It is capable of retrying in case the host is not immediately available
        Wait time is expressed in seconds. Default is 5 attempts, 2s min, 5s max
    """

    return socket.gethostbyname(hostname)
