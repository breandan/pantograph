import gast as ast, beniget, pydot, os, inspect, readline
from PIL import Image
from io import BytesIO


class Capture(ast.NodeVisitor):
    def __init__(self, parsed, par_names):
        self.duc = beniget.DefUseChains()
        self.duc.visit(parsed)
        self.udc = beniget.UseDefChains(self.duc)
        self.params = {k: v for (k, v) in self.udc.chains.items() if hasattr(k, 'id') and k.id in par_names and v}
        self.graph = pydot.Dot(graph_type='digraph')
        self.node_to_dot_node = {}
        self.src_to_target = set()
        self.visited = set()
        for param_node in self.params.keys():
            self.visit(param_node)

    def add_edge_if_nonexistient(self, source, target):
        if (source, target) not in self.src_to_target:
            self.graph.add_edge(pydot.Edge(source, target))

    def get_or_create_dot_node(self, node):
        if node in self.node_to_dot_node:
            return self.node_to_dot_node[node]
        else:
            new_node = pydot.Node(node.id) if hasattr(node, 'id') else pydot.Node(str(node))
            self.node_to_dot_node[node] = new_node
            self.graph.add_node(new_node)
            return new_node

    def visit(self, node):
        if node in self.visited:
            return

        pdsource = self.get_or_create_dot_node(node)
        self.visited.add(node)
        users = self.udc.chains[node][0].users()
        if not users:
            return

        pdtargets = [self.get_or_create_dot_node(x) for x in users]
        for pdtarget in pdtargets:
            self.add_edge_if_nonexistient(pdsource, pdtarget)

        for user in users:
            self.visit(user.node)


class PGraph:
    def __init__(self, *par_values):
        # Check Jupyter notebook input cache
        jupyter_cache = (stack.frame.f_locals['_ih'] for stack in inspect.stack() if '_ih' in stack.frame.f_locals)
        self.src = next(jupyter_cache, None)
        if self.src is not None:
            self.src = '\n'.join(self.src)

        # Check REPL history
        if self.src is None:
            self.src = [str(readline.get_history_item(i + 1)) for i in range(readline.get_current_history_length())]
        # Check Python file
        if self.src is None or not self.src:
            self.src = self.__get_caller_src()

        par_names = self.__get_caller_params()
        parsed = ast.parse(self.src)
        capture = Capture(parsed, par_names)
        self.graph = capture.graph

    def __get_caller_src(self):
        frames = inspect.getouterframes(inspect.currentframe())
        return ''.join(inspect.findsource(frames[2][0])[0])

    def __get_caller_params(self):
        s = next(stack.code_context[0] for stack in inspect.stack()
                 if stack.code_context is not None and
                 'PGraph' in stack.code_context[0])

        return list(map(str.strip, s[s.find('(') + 1:s.find(')')].split(',')))

    def show(self):
        Image.open(BytesIO(self.graph.create_png())).show()

    def _repr_html_(self):
        return self.graph.create_svg().decode('utf-8')


# z = 'hello '
# y = ' me '
# a = z + y + ' again'
# q = PGraph(a, z, y)
# print(q.src)
#
# q.show()
# print('goodbye')
