import sys
import argparse
import networkx as nx

SIZE_LIMIT = 32

class Node(object):
    def __init__(self, name):
        self.name = name
        self.limit = 2 # SIZE_LIMIT
        self.size = 0
        self.nodes = []
        self.parent = None
        self.sibling = None

    def insert_node(self, node):
        if self.size < self.limit:
            self.nodes.append(node)
            self.size += 1 # 8 # a byte per link, change later if needed
            return True
        else:
            return False

    def empty_clone(self, name):
        node = Node(name)
        for child in self.nodes:
            node.insert_node(child.empty_clone(name))
        return node

    def display(self, out, prefix = "  ", indents = 0):
        print >> out, (prefix * indents) + self.name + ":"
        for node in self.nodes:
            node.display(out, prefix, indents + 1)

class Leaf(Node):
    def __init__(self, name):
        self.name = name
        self.data = []
        self.size = 0
        self.limit = SIZE_LIMIT

    def add_data(self, data):
        if self.size + len(data) <= self.limit:
            self.data.append(data)
            self.size += len(data)
            return True
        else:
            return False

    def empty_clone(self, name):
        return Leaf(name)

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
    index += 1
    root = None

    for chunk in chunker:
        success = node.add_data(chunk)
        if not success:
            if root == None:
                root = Node("/node/%d" % (node_index))
                node_index += 1

            success = root.insert_node(node)
            if not success:
                new_parent = Node("/node/%d" % (node_index))
                node_index += 1
                new_parent.insert_node(root)
                new_parent.insert_node(node)
                root = new_parent

            node = Leaf("/leaf/%d" % (index))
            index += 1
            node.add_data(chunk)

    return root

def build_flat_tree(chunker):
    index = 0
    node_index = 0

    node = Leaf("/leaf/%d" % (index))
    index += 1
    root = None

    for chunk in chunker:
        success = node.add_data(chunk)
        if not success:
            if root == None:
                root = Node("/node/%d" % (node_index))
                node_index += 1

            # Attempt to insert into the parent until we fail
            target = root
            success = False
            while target != None
                success = target.insert_node(node)
                if not success:
                    if target.sibling == None:
                        target = target.parent
                    else:
                        target = target.sibling

            if not success:
                clone = root.empty_clone("/node/%d/" % (node_index))
                node_index += 1
    
                new_parent = Node("/node/%d" % (node_index))
                node_index += 1
                root.parent = new_parent
                clone.parent = new_parent
                root.sibling = clone
                new_parent.insert_node(root)
                new_parent.insert_node(clone)

                # navigate to left-most node in the clone
                target = clone
                root = clone
                while isinstance(target, Node):
                    root, target = target, target.nodes[0] # drill down to the left-most node
             

            node = Leaf("/leaf/%d" % (index))
            index += 1
            node.add_data(chunk)

    return root

def main(argv):

    desc = '''
Play around with different data tree construction strategies.
'''

    parser = argparse.ArgumentParser(prog='trees', formatter_class=argparse.RawDescriptionHelpFormatter, description=desc)
    parser.add_argument('-n', action="store", default=256, required=False, help="Size of sequential data stream")
    args = parser.parse_args()

    n = int(args.n)
    data = [x for x in range(0, n)]

    chunker = Chunker(32, data)

    # Skewed tree
    root = build_skewed_tree(chunker)
    if root:
        root.display(sys.stdout)

    # Flat tree
    root = build_flat_tree(chunker)
    if root:
        root.display(sys.stdout)

if __name__ == "__main__":
    main(sys.argv)
