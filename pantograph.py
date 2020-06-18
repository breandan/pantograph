import gast as ast, beniget, pydot, os, inspect, readline
from PIL import Image
from io import BytesIO


class PCapture(ast.NodeVisitor):
    def __init__(self, parsed, par_names):
        self.def_use = beniget.DefUseChains()
        self.def_use.visit(parsed)
        self.use_def = beniget.UseDefChains(self.def_use)
        self.params = {k: v for (k, v) in self.use_def.chains.items() if hasattr(k, 'id') and k.id in par_names and v}
        self.graph = pydot.Dot(graph_type='digraph')
        self.node_to_dot_node = {}
        self.src_to_target = set()
        self.already_visited = set()
        for param_node in self.params.keys():
            self.visit(param_node)

    def add_edge_if_nonexistent(self, source, target):
        if (source, target) not in self.src_to_target:
            self.graph.add_edge(pydot.Edge(source, target))
            self.src_to_target.add((source, target))

    def get_or_create_dot_node(self, node):
        if node in self.node_to_dot_node:
            return self.node_to_dot_node[node]
        else:
            new_node = pydot.Node(node.id) if hasattr(node, 'id') else pydot.Node(str(node))
            self.node_to_dot_node[node] = new_node
            self.graph.add_node(new_node)
            return new_node

    def visit(self, node):
        if node in self.already_visited:
            return

        dot_source = self.get_or_create_dot_node(node)
        self.already_visited.add(node)
        users = self.use_def.chains[node][0].users()
        if not users:
            return

        dot_targets = [self.get_or_create_dot_node(x) for x in users]
        for dot_target in dot_targets:
            self.add_edge_if_nonexistent(dot_source, dot_target)

        for user in users:
            self.visit(user.node)


class PGraph:
    def __init__(self, *par_values):
        # Check Jupyter notebook input cache
        self.src = self.recover_source()
        par_names = self.__get_caller_params()
        parsed = ast.parse(self.src)
        capture = PCapture(parsed, par_names)
        self.graph = capture.graph

    def recover_source(self):
        jupyter_cache = (stack.frame.f_locals['_ih'] for stack in inspect.stack() if '_ih' in stack.frame.f_locals)
        src = next(jupyter_cache, None)
        if src is not None:
            src = '\n'.join(src)
        # Check REPL history
        if src is None:
            src = [str(readline.get_history_item(i + 1)) for i in range(readline.get_current_history_length())]
        # Check Python file
        if src is None or not src:
            src = self.__get_caller_src()
        return src

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
