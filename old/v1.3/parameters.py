#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

#############################################################################
class Parameters:
    def __init__(self, app_name, cli_arguments, code_arguments):
        home_path = Path('~').expanduser()
        app_path = Path(home_path, '.{0:s}'.format(app_name)) 
        parameters_file_path = Path(app_path, 'parameters.json') 
        if not app_path.exists(): 
            # there is no app directory
            app_path.mkdir(parents=True)
        if cli_arguments is None:
            cli_arguments = {}
        if code_arguments is None:
            code_arguments = {}
        parameters = {**cli_arguments, **code_arguments}
        with parameters_file_path.open('w') as target:
            json.dump(parameters, target)
        self.__dict__ = parameters
