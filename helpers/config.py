# -*- coding: UTF-8 -*-
import configparser
import os


temp_path = 'config/'  # os.path.dirname(os.path.abspath(__file__))
configFile = os.path.join(temp_path, "settings.ini")
Config = configparser.RawConfigParser()
Config.read(configFile)


def initConfigModel():
    Config.read(configFile)
    ModelConfig = configparser.ConfigParser()
    modelFile = os.path.join(temp_path, "model.ini")
    ModelConfig.read(modelFile)
    for s in ModelConfig.sections():
        if s not in Config.sections():
            Config.add_section(s)
            Config.write(open(configFile, 'w'))
        for o in ModelConfig.options(s):
            if o not in Config.options(s):
                value = ModelConfig.get(s, o)
                Config.set(s, o, value)
                Config.write(open(configFile, 'w'))