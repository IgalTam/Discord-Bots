import math
from operator import indexOf

def sci_note_conv(in_num: str):
    """converts the input string into an integer, or returns false on fail"""
    if not in_num.isnumeric() and not ('E' in in_num and not in_num.startswith('E') and not in_num.endswith('E')) \
        and in_num.count('.') > 1:
        return False
    if 'E' in in_num: # create valid integer from scientific notation
        in_num = int(in_num[0:indexOf(in_num, 'E')]) * math.pow(10, int(in_num[indexOf(in_num, 'E')+1:]))
        return in_num
    return False