# -*- coding: utf-8 -*-

"""
Debugging module

Created: Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import logging
from framework.helpers.config import Configuration
from framework.helpers.string import isNotNull
from logging.handlers import RotatingFileHandler

class Log(object):
  """Log class"""
  instance = None

  def __init__(self, configFile=None):
    if configFile:
      self.__config = Configuration(configFile, 'Logger')
      self.__doLog = self.__config.get('log')
      self.logLvl = getattr(logging, self.__config.get('level').upper())
    else:
      self.__doLog = True
      self.logLvl = logging.INFO
    if self.__doLog:
      # create logger
      self.__logger = logging.getLogger('root')
      if configFile:
        self.__logger.setLevel(self.logLvl)
        self.logFileSize = self.__config.get('size')
        self.nbrOfBackups = self.__config.get('backups')
        self.logToConsole = self.__config.get('logconsole')
        self.logfile = self.__config.get('logfile')
      else:
        self.logFileSize = 100000
        self.nbrOfBackups = 2
        self.logToConsole = True
        self.logfile = ''
      # create formatter
      stringFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
      datefmt = '%m/%d/%Y %I:%M:%S %p'
      self.__formatter = logging.Formatter(fmt=stringFormat, datefmt=datefmt)
      # create console Handler and set level to debug
      self.setConsoleHandler(self.__logger)
      self.setLogFile(self.__logger)
    Log.instance = self

  def setConsoleHandler(self, logger):
    """
    Sets the console handler with the parameters to the given logger
    """
    if self.logToConsole:
      consoleHandler = logging.StreamHandler()
      consoleHandler.setLevel(self.logLvl)
      consoleHandler.setFormatter(self.__formatter)
      logger.addHandler(consoleHandler)

  def setLogFile(self, logger):
    """
    Sets the file loggerwith the parameters to the given logger
    """
    if isNotNull(self.logfile):
      # Remove the default FileHandlers if present.
      logger.error_file = ""
      logger.access_file = ""
      maxBytes = getattr(logger, "rot_maxBytes", self.logFileSize)
      backupCount = getattr(logger, "rot_backupCount", self.nbrOfBackups)
      fileRotater = RotatingFileHandler(self.logfile, 'a', maxBytes,
                                        backupCount)
      fileRotater.setLevel(self.logLvl)
      fileRotater.setFormatter(self.__formatter)
      logger.addHandler(fileRotater)

  @classmethod
  def getInstance(cls):
    """
    Returns the instance of the logger
    """
    if Log.instance is None:
      Log.instance.getLogger('root').error('No configuration loaded')
      Log.instance = Log()
    return Log.instance

  @staticmethod
  def getLogger(className):
    """
    Returns the instance for of the logger for the given class

    :returns: Logger
    """
    if Log.instance is None:
      return Log.getInstance().getLogger(className)
    else:
      logger = logging.getLogger(className)
      logger.setLevel(Log.getInstance().logLvl)
      Log.getInstance().setConsoleHandler(logger)
      Log.getInstance().setLogFile(logger)
      return logger