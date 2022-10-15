import math
from operator import indexOf

def sci_note_conv(in_num):
    """converts the input string into an integer, or returns false on fail"""
    if not in_num.isnumeric() and not ('E' in in_num and in_num[0] != 'E' and in_num[len(in_num)-1] != 'E'):
        return False
    if 'E' in in_num: # create valid integer from scientific notation
        in_num = int(in_num[0:indexOf(in_num, 'E')]) * math.pow(10, int(in_num[indexOf(in_num, 'E')+1:]))
        return in_num
    return False