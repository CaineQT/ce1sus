# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 23, 2014
"""
import cherrypy
import os
from os.path import exists

from ce1sus.controllers.login import LoginController
from ce1sus.views.web.common.base import BaseView
from ce1sus.controllers.base import ControllerException
from cherrypy.lib.auth import basic_auth


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class IndexView(BaseView):

  def __init__(self, config):
    BaseView.__init__(self, config)
    self.login_controller = LoginController(config)

  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def index(self):
    # check if basic auth. set
    do_basicauth = self.config.get('ce1sus', 'usebasicauth', False)
    if do_basicauth:
      basic_auth = cherrypy.request.wsgi_environ.get('REMOTE_USER', None)
      if basic_auth:
        username = cherrypy.request.wsgi_environ.get('REMOTE_USER', None)
        if username:
          try:
            user = self.login_controller.get_user_by_username(username)
            if user:
              self.login_controller.update_last_login(user)
              self.put_user_to_session(user)
          except ControllerException:
            pass

    # check if basic auth is enabled an if the user is set
    # only for fetching the first page
    return open(os.path.join(cherrypy.config.get("tools.staticdir.root"), u'index.html'))


  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  @cherrypy.tools.json_out()
  def welcome_message(self):
    if self.user_authenticated():
      changelog_file = 'CHANGELOG'
      if exists(changelog_file):
        file_obj = open(changelog_file, 'r')
        result = ""
        counter = 0
        for line in file_obj:
          if 'Release' in line:
            counter = counter + 1
          if counter == 2:
            break
          if counter > 0:
            result = u'{0}\n{1}'.format(result, line)
        return result
      else:
        return u'No new messages'
    else:
      return u'Login'
