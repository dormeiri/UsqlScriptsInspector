import shutil
import os
from os import path
from datetime import datetime

from inspections.inspector import Inspector, Statement
import usql_scripts

OUTPUT_FOLDER = 'output'
OUTPUT_PATH = f'{OUTPUT_FOLDER}\\{{}}.csv'
OUTPUT_PATH_DATETIME_FORMAT = '%Y%m%d%H%M%S'


def main():
    statements_list = (
        Statement('Environment', 'DECLARE EXTERNAL @Environment'),
        Statement('WindowEndParam', 'DECLARE EXTERNAL @WindowEndParam'),
        Statement('WindowStartParam', 'DECLARE EXTERNAL @WindowStartParam'),
        Statement('OfDate', 'DECLARE @OfDate')
    )

    inspector = Inspector(statements_list)
	
    print('Insert U-SQL project directory path:')
    inspector.inspect(usql_scripts.get_scripts_paths(input()))
	
    output_path = get_output_path()	
    inspector.to_csv(output_path)

    print(f'Inspection results file created at "{output_path}"')

def get_output_path():
    now_str = datetime.utcnow().strftime(OUTPUT_PATH_DATETIME_FORMAT)
    return path.abspath(OUTPUT_PATH.format(now_str))

if __name__ == '__main__':
    main()
