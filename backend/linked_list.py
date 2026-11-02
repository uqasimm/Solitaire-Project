class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def append(self, data):
        new_node = Node(data)

        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

        self.length += 1

    def remove_last(self):
        if self.is_empty():
            return None

        removed_data = self.tail.data

        if self.head == self.tail:
            self.head = None
            self.tail = None

        else:
            current = self.head

            while current.next != self.tail:
                current = current.next

            current.next = None
            self.tail = current

        self.length -= 1
        return removed_data

    def peek_last(self):
        if self.is_empty():
            return None

        return self.tail.data

    def is_empty(self):
        return self.head is None

    def size(self):
        return self.length

    def display(self):
        current = self.head
        while current is not None:
            print(current.data)
            current = current.next

    def get_items(self):
        items = []
        current = self.head

        while current is not None:
            items.append(current.data)
            current = current.next

        return items

    def remove_from(self, index):
        if index < 0 or index >= self.length:
            return []

        current = self.head
        removed_cards = []

        for i in range(index):
            current = current.next

        while current is not None:
            removed_cards.append(current.data)
            current = current.next

        if index == 0:
            self.head = None
            self.tail = None
        else:
            current = self.head

            for i in range(index - 1):
                current = current.next

            current.next = None
            self.tail = current

        self.length = index

        return removed_cards
