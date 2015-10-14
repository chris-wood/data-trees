import sys
import argparse
import networkx as nx

SIZE_LIMIT = 128

class Node(object):
    def __init__(self, name):
        self.name = name
        self.limit = SIZE_LIMIT
        self.size = 0
        self.nodes = []

    def insert_node(self, node):
        if self.size < self.limit:
            self.nodes.append(node)
            self.size += 8 # a byte per link, change later if needed
            return True
        else:
            return False

    def display(self, out, prefix = "  ", indents = 0):
        print >> out, (prefix * indents) + self.name
        for node in self.nodes:
            node.display(out, prefix, indents + 1)

class Leaf(Node):
    def __init__(self, name):
        self.name = name
        self.data = []
        self.size = 0
        self.limit = SIZE_LIMIT

    def add_data(self, data):
        if self.size + len(data) < self.limit:
            self.data.append(data)
            self.size += len(data)
            return True
        else:
            return False

    def display(self, out, prefix = "  ", indents = 0):
        print >> out, (prefix * indents) + self.name + ":"
        for data in self.data:
            print >> out, (prefix * (indents + 1)), data

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

def build_skewed_tree(chunker):
    index = 0
    node_index = 0

    node = Leaf("/leaf/%d" % (index))
    root = None

    for chunk in chunker:
        success = node.add_data(chunk)
        if not success:
            if root == None:
                root = Node("/node/%d" % (node_index))

            success = root.insert_node(node)
            if not success:
                new_parent = Node("/node/%d" % (node_index))
                new_parent.insert_node(root)
                root = new_parent

            index += 1
            node = Leaf("/leaf/%d" % (index))

    return root

def build_flat_tree(chunker):
    index = 0
    node_index = 0

    node = Leaf("/leaf/%d" % (index))
    root = None

    for chunk in chunker:
        pass

    return root

def main(argv):

    desc = '''
Play around with different data tree construction strategies.
'''

    parser = argparse.ArgumentParser(prog='trees', formatter_class=argparse.RawDescriptionHelpFormatter, description=desc)
    parser.add_argument('-n', action="store", default=256, required=False, help="Size of sequential data stream")
    args = parser.parse_args()

    n = args.n
    data = [x for x in range(0, n)]

    chunker = Chunker(32, data)

    # Skewed tree display
    root = build_skewed_tree(chunker)
    if root:
        root.display(sys.stdout)

    root = build_flat_tree(chunker)
    if root:
        root.display(sys.stdout)

if __name__ == "__main__":
    main(sys.argv)
