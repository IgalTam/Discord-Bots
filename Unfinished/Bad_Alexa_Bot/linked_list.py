# add your module doc integer, including your name, here.
"""LAB2
CPE 202
Igal Tamarkin
"""


class Node:
    """Linked List is one of None or Node
    Attributes:
        val (int): an item in the list
        next (Node): a link to the next item in the list (Linked List)
    """
    def __init__(self, val, next=None):
        self.val = val
        self.next = next

    def __repr__(self):
        return "Node(%d, %s)" % (self.val, self.next)

    def __eq__(self, other):
        return isinstance(other, Node)\
            and self.val == other.val\
            and self.next == other.next


def insert(lst, val, pos):
    """inserts the integer at the position pos in the linked list recursively.
    Args:
        lst (Node): the list
        val (int): the value to be inserted in the list
        pos (int): the position
    Returns:
        Node: the head of a LinkedList
    Raises:
        IndexError: when the position is out of bound ( > num_items).
    """
    if lst is None:
        return Node(val, None)
    if pos == 0:
        temp = lst
        lst = Node(val, temp)
        return lst
    head = lst
    return in_help(lst, head, val, pos)


def in_help(lst, head, val, pos):
    """inserts the integer at the position pos recursively, and
       returns the head node of the linked list
    Args:
        lst (Node): the list
        head (Node): points to the head of the node
        val (int): the value to be inserted
        pos (int): the current position within the list
    Returns:
        head: the head of the list
    Raises:
        IndexError: when the position is out of bound ( > num_items)
    """
    # print('next', lst.next, 'pos', pos)
    if pos > 1 and lst.next is None:
        raise IndexError
    if pos == 1:
        if lst.next is not None:
            temp = lst.next
            lst.next = Node(val, None)
            lst.next.next = temp
        elif lst.next is None:
            lst.next = Node(val, None)
        # print(head)
        return head
    return in_help(lst.next, head, val, pos - 1)


def get(lst, pos):
    """gets an item stored at the specified position recursively.
    Args:
        lst (Node): a head of linked list
        pos (int): the specified position
    Returns:
        int: the value of the item at the position pos.
    Raises:
        IndexError: when the position is out of bound ( >= num_items).
    """
    if lst is None or pos < 0:
        raise IndexError
    if pos == 0:
        return lst.val
    return get(lst.next, pos-1)


def search(lst, val):
    """searches for a specified value in a given list.
    Args:
        lst (Node): an object of Node (LinkedList)
        val (int): a value to search for
    Returns:
        int: the position where the value is stored in the list. It returns
             None if the value is not found.
    """
    if lst is None:
        return None
    if lst.val == val:
        return 0
    if search(lst.next, val) is None:
        return None
    ret = 1 + search(lst.next, val)
    if ret is None:
        return None
    return ret


def contains(lst, val):
    """checks if a specified value exists in a given list.
    This function calls search function.
    Args:
        lst (Node): the head of a LinkedList
        val (int): the item being checked for
    Returns:
        bool: True if the value is found or False if not.
    """
    found = search(lst, val)
    if found is None:
        return False
    if found is not None:
        return True


def remove(lst, val):
    """removes the first occurrence of a specified value in a given
       list recursively.
    Args:
        lst (Node): the head of a LinkedList
        val (int): a value to be removed
    Returns:
        Node: the head of the linked list with the first occurrence of
        the value removed.
    """
    if lst.next is None:
        return None
    if lst.val == val:
        return lst.next
    return Node(lst.val, remove(lst.next, val))


def pop(lst, pos):
    """removes the item at a specified position in a given list recursively
    Args:
        lst (Node): the head of a LinkedList
        pos (int): the position in the list where an item is removed
    Returns:
        Node: the head of the LinkedList with the item removed
        int: the removed item’s value.
    Raises:
        IndexError: when the position is out of bound ( >= num_items).
    """
    if pos == 0:
        temp = lst
        lst = lst.next
        return lst, temp.val
    head = lst
    return pop_help(lst, pos, head)


def pop_help(lst, pos, head):
    """removes the item at pos, then returns its value and the head of the
       list, recursively
    Args:
        lst (Node): the current node
        pos (int): the current position
        head (Node): the head of the LinkedList
    Returns:
        Node: the head of the LinkedList after removal
        int: the removed node's val
    Raises:
        IndexError: when the position is out of bound ( >= num_items)
    """
    if pos > 1 and lst is None:
        raise IndexError
    if pos == 1:
        temp = lst.next
        lst.next = lst.next.next
        return head, temp.val
    return pop_help(lst.next, pos - 1, head)


def size(lst):
    """returns the number of items stored in the LinkedList recursively.
    Args:
        lst (Node): the head of a LinkedList
    Returns:
        int: the number of items stored in the list
    """
    if lst is None:
        return 0
    return 1 + size(lst.next)

