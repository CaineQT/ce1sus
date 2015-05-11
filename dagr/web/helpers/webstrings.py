# -*- coding: utf-8 -*-

"""
module in charge of string foo, since cherrypy sends more parameters

Created Aug, 2013
"""
__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import dagr.helpers.strings as strings
from base64 import b64encode


# pylint: disable=W0613
def plaintext2html(context, text, tabstop=4, make_br=True, remove_if_escaped=False):
  """
  Converts plain text string to html
  """
  stringText = strings.plaintext2html(text, tabstop, make_br, remove_if_escaped)

  return stringText


def base64(context, text):
  message = text.encode('utf-8', 'replace')
  return b64encode(message)