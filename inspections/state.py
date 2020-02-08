from enum import Enum


__ANNOTATION_BLOCK_START = 'ANNOTATIONS:'
__ANNOTATION_BLOCK_END = '*/'


class State(Enum):
    STATEMENT = 0
    ANNOTATION = 1


def get_state(line, current_state):
    if __is_annotation_state(line, current_state):
        return State.ANNOTATION
    else:
        return State.STATEMENT

def __is_annotation_state(line, current_state):
    if __is_annotation_block_end(line):
        return False
    else: 
        return current_state == State.ANNOTATION or __is_annotation_block_start(line)

def __is_annotation_block_start(line): return line.strip() == __ANNOTATION_BLOCK_START

def __is_annotation_block_end(line): return line.strip() == __ANNOTATION_BLOCK_END 