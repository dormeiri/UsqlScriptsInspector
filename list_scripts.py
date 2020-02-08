from os import path
from usql_scripts import get_scripts_paths


def main():
    print('Insert U-SQL project directory path:')
    for p in get_scripts_paths(input()):
        print(path.basename(p))

if __name__ == "__main__":
    main()