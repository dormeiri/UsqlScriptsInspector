import os
from os import path


USQL_EXTENSION = '.usql'


def get_scripts_paths(dir):
    for root, _, files in os.walk(dir):
        for file in files:
            if file.endswith(USQL_EXTENSION):
                yield path.join(root, file)