"""Starter code for Lab 3
CPE202

Igal Tamarkin
"""

from linked_list import Node


class QueueArray:
    """A queue using array-based implementation
    Attributes:
        capacity (int): the maximum number of items the queue can hold
        items (list): the array in which items are stored
        num_items (int): the number of items in the queue
        front (int): pointer towards the front index of the queue
        rear (int): pointer towards the back index of the queue
    """
    def __init__(self, capacity):
        # the maximum number of items that can be stored in queue
        self.capacity = capacity
        self.items = [None] * (self.capacity + 1)  # array whose size is the capacity
        self.num_items = 0  # number of items in array
        self.front = 0  # pointer to the front of queue
        self.rear = 0  # pointer to the rear of queue

    def __repr__(self):
        return "QueueArray(%d, %a, %d, %s, %s)" % (self.capacity, self.items,
                                                   self.num_items, self.front, self.rear)

    def is_empty(self):
        """returns true if the queue is empty
        Returns:
            boolean : true if empty, false otherwise
        """
        if self.num_items == 0:
            return True
        return False

    def is_full(self):
        """returns true if the queue is full
        Returns:
            boolean : true if full, false otherwise
        """
        #if self.front == (self.rear + 1) % len(self.items):
        if self.num_items == self.capacity:
            return True
        return False

    def enqueue(self, item):
        """appends an item to the back of the queue
        Args:
            item : the object to be enqueued
        Raises:
            IndexError if the queue is full
        """
        if self.is_full() is True:
            raise IndexError
        self.items[self.rear] = item
        self.num_items += 1
        self.rear = (self.rear + 1) % len(self.items)

    def dequeue(self):
        """removes an item from the front of the queue, then returns it
        Returns:
            item : the dequeued item
        Raises:
            IndexError if the queue is empty
        """
        if self.is_empty() is True:
            raise IndexError
        item = self.items[self.front]
        self.num_items -= 1
        self.front = (self.front % self.capacity) + 1
        return item

    #returns the number of items in the queue
    def size(self):
        """returns the number of items in the queue
        Returns:
              num_items : the number of items in the queue
        """
        return self.num_items

#You must have the same functionalities for the Linked List Implementation
class QueueLinked:
    """A queue using array-based implementation
        Attributes:
            capacity (int): the maximum number of items the queue can hold
            num_items (int): the number of items in the queue
            front (Node): pointer towards the front node of the queue
            rear (Node): pointer towards the back node of the queue
        """
    def __init__(self, capacity):
        #the maximum number of items that can be stored in queue
        self.capacity = capacity
        self.front = None #pointer to the front of queue
        self.rear = None #pointer to the rear of queue
        self.num_items = 0 #number of items in array

    def __repr__(self):
        return "QueueLinked(%d, %s, %s, %d)" % (self.capacity, self.front,
                                                self.rear, self.num_items)

    def __eq__(self, other):
        return isinstance(other, QueueLinked) \
            and self.capacity == other.capacity \
            and self.front == other.front \
            and self.rear == other.rear \
            and self.num_items == other.num_items

    def is_empty(self):
        """returns true if the queue is empty
        Returns:
            boolean : true if empty, false otherwise
        """
        if self.num_items == 0:
            return True
        return False

    def is_full(self):
        """returns true if the queue is full
        Returns:
            boolean : true if full, false otherwise
        """
        if self.num_items == self.capacity:
            return True
        return False

    def enqueue(self, item):
        """appends an item to the back of the queue
        Args:
            item : the object to be enqueued
        Raises:
            IndexError if the queue is full
        """
        if self.is_full() is True:
            raise IndexError
        if self.num_items == 0:
            self.rear = Node(item)
            self.front = self.rear
            self.num_items += 1
        else:
            insert = Node(item)
            self.rear.next = insert
            self.rear = insert
            self.num_items += 1

    def dequeue(self):
        """removes an item from the front of the queue, then returns it
        Returns:
            item : the dequeued item
        Raises:
            IndexError if the queue is empty
        """
        if self.is_empty() is True:
            raise IndexError
        self.num_items -= 1
        item = self.front
        self.front = self.front.next
        return item.val

    #returns the number of items in the queue
    def size(self):
        """returns the number of items in the queue
        Returns:
              num_items : the number of items in the queue
        """
        return self.num_items
