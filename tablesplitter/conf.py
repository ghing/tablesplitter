import os
import importlib

settings_module = os.environ.get('TABLESPLITTER_SETTINGS_MODULE')

class Settings(object):
    def __init__(self, settings_module):
        mod = importlib.import_module(settings_module)

        for setting in dir(mod):
            if setting.isupper():
                setting_value = getattr(mod, setting)
                setattr(self, setting, setting_value)

settings = Settings(settings_module)
