from inspections.inspector import Inspector
from usql_scripts import get_scripts_paths


def main():
    inspector = Inspector([])
	
    print('Insert U-SQL project directpry path:')
    inspector.inspect(get_scripts_paths(input()))

    for a in inspector.annotations:
	    print(a)


if __name__ == "__main__":
    main()