import yaml
import os
from graphviz import Digraph
from uuid import uuid4


class Block:
    def __init__(self, graph_name, label):
        self.graph_name = graph_name
        self.name = str(uuid4())
        self.label = label

        self.subblocks = []
        self.subgraph_name = 'cluster-' + str(uuid4())

        self.parallel = False
    
    def append(self, label):
        block = Block(self.subgraph_name, label)
        self.subblocks.append(block)
        return block
    
    def last(self):
        if self.subblocks:
            if self.parallel:
                res = []
                for block in self.subblocks:
                    res += block.last()
                return res
            else:
                return self.subblocks[-1].last()
        return [self]

    def draw(self, dot):
        dot.node(self.name, self.label)
        prev = [self]
        with dot.subgraph(name=self.subgraph_name) as c:
            for block in self.subblocks:
                block.draw(c)
                for b in prev:
                    dot.edge(b.name, block.name)
                if not self.parallel:
                    prev = block.last()


def load(root, data, filepath):
    dirpath = '/'.join(filepath.split('/')[:-1]) + '/'

    for key in data.keys():
        if key == '_parallel':
            root.parallel = data[key]
        if key == 'call>':
            fpath = dirpath + data[key]
            if not fpath.endswith('.dig'):
                fpath += '.dig'
            if os.path.exists(fpath):
                with open(fpath) as f:
                    data = yaml.load(f, Loader=yaml.FullLoader)
                    load(root, data, fpath)
            else:
                print('warn ' + fpath + ' does not exist.')
        if not key.startswith('+'):
            continue
        block = root.append(key)
        load(block, data[key], filepath)


def main():
    filepath = os.getcwd() + '/hoge.dig'

    dot = Digraph(format='png')
    root = Block('root', 'root')

    with open(filepath) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        load(root, data, filepath)

    root.draw(dot)
    dot.render('out')


if __name__ == '__main__':
    main()

