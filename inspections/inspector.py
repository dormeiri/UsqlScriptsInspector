from functools import reduce
import os
from os import path
import csv

from inspections import state
from inspections.state import State


class BaseStatement:
    def get_key(self):
        raise NotImplementedError("")

    def check_line(self, line):
        raise NotImplementedError("")

    def __eq__(self, other):
        return self.get_key() == other.get_key()

    def __hash__(self):
        return hash(self.get_key())

    def __str__(self):
        return self.get_key()

    def __lt__(self, other):
        return self.get_key() < other.get_key()


class Statement(BaseStatement):
    def __init__(self, key, prefix):
        self.key = key
        self.__prefix = prefix


    def get_key(self):
        return self.key

    def check_line(self, line):
        return line.strip().startswith(self.__prefix)


class Annotation(BaseStatement):
    def __init__(self, value):
        self.value = value


    def get_key(self):
        return self.value

    def check_line(self, line):
        return line.strip() == self.value


class Inspector:
    def __init__(self, statements):
        self.__states_lists = {
            State.ANNOTATION: [],
            State.STATEMENT: statements
        }

        self.__results = []


    @property
    def annotations(self):
        return list(self.__states_lists[State.ANNOTATION])


    def inspect(self, paths):
        """Check for statemenets and annotations in files at 'paths' and updates 'self.__results'"""

        paths = list(paths)  # Because we will iterate over the paths twice
        
        # First step
        self.__find_annotations(paths)  

        # Second steps
        for p in paths:
            with open(p) as file:
                self.__inspect_file(file)

    def to_csv(self, output_path):
        """Output 'self.__results' to .csv file"""

        os.makedirs(path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', newline='') as csv_file:
            columns = InspectionResult.csv_columns(self.__get_keys_vector())

            writer = csv.DictWriter(csv_file, fieldnames=columns)
            writer.writeheader()

            for result in self.__results:
                writer.writerow(result.todict())
    

    def __find_annotations(self, paths):
        # Update 'self.__annotations'
        for p in paths:
            with open(p) as file:
                self.__find_annotations_in_file(file)

        # Remove duplicates
        self.__states_lists[State.ANNOTATION] = sorted(set(self.__states_lists[State.ANNOTATION]))  

    def __find_annotations_in_file(self, file):
        curr_state = State.STATEMENT
        for line in file:
            # Check state
            last_state = curr_state
            curr_state = state.get_state(line, curr_state)

            if last_state == State.ANNOTATION:
                if last_state == curr_state:  # Is in block
                    a = Annotation(line.strip())
                    self.__states_lists[State.ANNOTATION].append(a)
                else:  # Was in State.ANNOTATION block
                    break
            

    def __inspect_file(self, file):
        result = InspectionResult(
            self.__get_keys_vector(), 
            self.__get_result_vector(file), 
            path.abspath(file.name)
        )

        self.__results.append(result)


    def __get_keys_vector(self):
        """Get statements keys as a vector, use it only after self.annotation is loaded"""

        return reduce(
            lambda s1, s2: s1 + [s.get_key() for s in self.__states_lists[s2]], 
            State, 
            []
        )

    def __get_result_vector(self, file):
        """Get statements values of file as a vector, use it only after self.annotation is loaded"""

        curr_state = State.STATEMENT

        not_found = {
            State.STATEMENT: list(self.__states_lists[State.STATEMENT]),
            State.ANNOTATION: list(self.__states_lists[State.ANNOTATION])
        }

        for line in file:
            last_state = curr_state
            curr_state = state.get_state(line, curr_state)

            if last_state == curr_state:  # Is in block
                self.__update_not_found(lambda x: x.check_line(line), not_found[curr_state])
            
                if self.__is_found_all(not_found.values()):
                    break

        return reduce(
            lambda s1, s2: s1 + self.__get_result_subvector(s2, not_found),
            State,
            []
        )


    def __get_result_subvector(self, of_state, not_found):
        return [s not in not_found[of_state] for s in self.__states_lists[of_state]]

    @staticmethod
    def __update_not_found(func, not_found): 
        for s in filter(func, not_found):
            not_found.remove(s)

    @staticmethod
    def __is_found_all(not_found_lists): all(map(lambda l: len(l) == 0, not_found_lists))


class InspectionResult:
    def __init__(self, keys_vector, result_vector, script_path):
        self.__values = dict(zip(keys_vector, result_vector))
        self.__script_path = script_path

        if script_path is not None:
            self.__script_name = path.basename(script_path)
            self.__script_name = self.__script_name[:self.__script_name.rindex('.')]
        else:
            self.__script_name = None

        self.__additional_values = {
            'Script Name' : self.__script_name,
            'Path' : self.__script_path,
            'Is Annotated' : any(result_vector)
        }


    def todict(self):
        result = dict(self.__additional_values)
        result.update(self.__values)

        return result


    @staticmethod
    def csv_columns(keys_vector):
        return InspectionResult.__create_empty(keys_vector).todict().keys()

    @staticmethod
    def __create_empty(keys_vector):
    	return InspectionResult(keys_vector, [None] * len(keys_vector), None)