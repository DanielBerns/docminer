#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from datetime import datetime


#############################################################################
class Parameters:
    def __init__(self, app_name):
        home = Path('~').expanduser()
        app_at_home = Path(home, '.{0:s}'.format(app_name)) 
        parameters_file = Path(app_at_home, 'parameters.json') 
        default_store = {'default_store': True, 
                         'datetime_now': str(datetime.now()),
                         'home_url': str(home),
                         'app_at_home_url': str(app_at_home),
                         'parameters_file_url': str(parameters_file)
                         }
        if app_at_home.exists(): 
            # app_at_home directory exists
            if parameters_file.exists(): 
                # There a is file with the expected filename
                with parameters_file.open('r') as source:
                    # read the json file
                    store = json.load(source)
                    # we expect a dictionary
                    assert(type(store) == dict)
                    # you must check keys and values
            else:
                store = default_store
        else:
            # there is no app_at_home directory
            app_at_home.mkdir(parents=True)
            # default parameters
            store = default_store
        # construct the arguments parser and parse the arguments
        argument_parser = self.get_argument_parser()
        if argument_parser is not None:
            # there are arguments to parse
            args = vars(argument_parser.parse_args())
            store = {**store, **args}
        self.__dict__ = store
        self.save()

    def __get_item__(self, key):
        return self.__dict__[key]
    
    def __set_item__(self, key, value):
        self.__dict__[key] = value
    
    def save(self):
        parameters_file = Path(self.parameters_file_url)
        with parameters_file.open('w') as target:
            json.dump(self.__dict__, target)

    def build_argument_parser(self):
        """Build the object ArgumentParser from the argparse library
        """
        return argparse.ArgumentParser()

    def get_argument_parser(self):
        """Return None if there is no cli
        """
        return None
