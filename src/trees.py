import sys
import networkx as nx

class Node(object):
    def __init__(self, name, limit):
        self.name = name
        self.limit = limit
        self.nodes = []

    def insert_node(self, node):
        if len(self.nodes) < self.limit:
            self.nodes.append(node)
            return True
        else:
            return False

class Leaf(Node):
    def __init__(self, name, data):
        self.data = data   

class Chunker(object):
    def __init__(self, chunksize, data):
        self.chunksize = chunksize
        self.data = data
        self.limit = len(data)
        self.index = 0

    def __iter__(self):
        while self.index < self.limit:
            yield self.data[self.index:(self.index + self.chunksize)]
            self.index += self.chunksize

def main(argv):
    n = int(argv[1])
    data = [x for x in range(0, n)]

    chunker = Chunker(10, data)
    for chunk in chunker:
        print chunk

if __name__ == "__main__":
    main(sys.argv)
