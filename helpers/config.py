# -*- coding: UTF-8 -*-
import configparser
import os


temp_path = os.path.dirname(os.path.abspath(__file__))
configFile = os.path.join(temp_path, "config.ini")
Config = configparser.RawConfigParser()
Config.read(configFile)
