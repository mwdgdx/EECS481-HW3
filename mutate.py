"""
This file demonstrates a basic workflow for creating mutants. First, 
we collect a list of nodes we want to mutate, then we modify
those nodes one at a time to create mutants. There are a couple things
you should change before using this for HW3: 

1) Add a command line interface
2) Add code for writing mutants back to python source code
3) Add code to turn add nodes into multiply nodes

See lines marked with TODO
"""

import sys
import ast
import astor
import random
# import hidden  # TODO: delete this line before submitting to the autograder
import copy


def get_command_args():
    if len(sys.argv) != 3:
        print("Wrong number of command line arguments")
        sys.exit(1)
    return (str(sys.argv[1]), int(sys.argv[2]))

def main():
    # We want "randomness", but we also want it to do the same thing
    # every time (determistic execution).
    random.seed(2873465893)

    (file_to_read, num_mutants) = get_command_args()
    with open(file_to_read, 'r') as f:
        program = ast.parse(f.read())

    # Walk through the AST and collect all Add operations
    collector = AddCollector()
    collector.visit(program)

    # We want to choose which mutations we apply randomly. There are multiple
    # ways to do this. I like shuffling them and then taking a slice.
    print("nodes to choose from: ", collector.binops_to_visit)
    random.shuffle(collector.binops_to_visit)

    to_mutate = collector.binops_to_visit[:num_mutants]

    # Here we make only apply one mutation operator per mutant since the
    # coupling effect tells us that complex faults are correlated with simple
    # faults. You may need to change this to get full points on the autograder
    for (i, node_id) in enumerate(to_mutate):
        # Start with a fresh copy of the syntax tree for each mutant.
        with open(file_to_read, 'r') as f:
            program = ast.parse(f.read())

        # Create our mutant by walking the AST
        mutant = AddMutator(node_id).visit(program)

        # TODO: Add code here to write the mutant out to a file.
        # hidden.fixme_write_to_file(i, mutant)
        result = astor.to_source(mutant)
        out_file_name = str(i) + '.py'
        with open(out_file_name, 'w') as f:
            f.write(result)


# Find all the Add nodes in the program and record them.
class AddCollector(ast.NodeVisitor):
    def __init__(self):
        self.binop_count = 0
        self.function_count = 0
        self.binops_to_visit = []
        self.compare_count = 0

    # For demonstration purposes: count how many functions there are,
    # then make sure to continue visiting the children.
    def visit_FunctionDef(self, node):
        # Calls visit on all the children.
        self.generic_visit(node)
        self.function_count += 1

    # This function will get called on every BinOp node in the tree.
    def visit_BinOp(self, node):
        self.generic_visit(node)
        self.binop_count += 1
        # check that we are indeed looking at an Add node since this
        # is what we care about
        if isinstance(node.op, ast.Add):
            # record which node we're looking at by using the counter we
            # increment each time we visit a BinOp. This uniquely identifies
            # Add nodes since the AST is traversed deterministically using the
            # visitor pattern
            self.binops_to_visit.append(self.binop_count)
    
    def visit_Compare(self, node):
        self.generic_visit(node)
        self.compare_count += 1
        if isinstance(node.ops[0], ast.Eq):
            self.binops_to_visit.append(self.compare_count)

class AddMutator(ast.NodeTransformer):
    def __init__(self, count_of_node_to_mutate):
        self.count_of_node_to_mutate = count_of_node_to_mutate
        self.binop_count = 0
        self.compare_count = 0

    def opposite(self, node):
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Add):
                node.op = ast.Sub()
            elif isinstance(node.op, ast.Sub):
                node.op = ast.Add()
            elif isinstance(node.op, ast.Mult):
                node.op = ast.Div()
            elif isinstance(node.op, ast.Div):
                node.op = ast.Mult()
        elif isinstance(node, ast.Compare):
            if isinstance(node.ops[0], ast.Eq):
                node.ops[0] = ast.NotEq()
            elif isinstance(node.ops[0], ast.NotEq):
                node.ops[0] = ast.Eq()
            elif isinstance(node.ops[0], ast.Lt):
                node.ops[0] = ast.GtE()
            elif isinstance(node.ops[0], ast.LtE):
                node.ops[0] = ast.Gt()
            elif isinstance(node.ops[0], ast.Gt):
                node.ops[0] = ast.LtE()
            elif isinstance(node.ops[0], ast.GtE):
                node.ops[0] = ast.Lt()
        return node

    def visit_BinOp(self, node):
        self.generic_visit(node)
        self.binop_count += 1

        # Check if this is the node we want to alter. We can accomplish this by
        # keeping track of a counter, which we increment every time encounter
        # a BinOp. Since the traversal through the AST is deterministic using the visitor
        # pattern (IT IS NOT DETERMINISTIC IF YOU USE ast.walk), we can identify AST nodes
        # uniquely by the value of the counter
        if (self.binop_count == self.count_of_node_to_mutate):
            # We make sure to use deepcopy so that we preserve all extra
            # information we don't explicitly modify
            new_node = copy.deepcopy(node)

            # TODO: You are responsible for figuring out how to modify this node
            # such that it turns into a multiply. Hint: it only took me one line.
            # There are other ways to do this as well (e.g. creating the
            # node directly from a constructor)
            # hidden.fixme_change_to_multiply_node(new_node)
            new_node = self.opposite(new_node)
            # returning our new node will overwrite the node we were given on entry
            # to this class method
            return new_node
        else:
            # If we're not looking at an add node we want to change, don't modify
            # this node whatsoever
            return node


    def visit_Compare(self, node):
        self.generic_visit(node)
        self.compare_count += 1
        if (self.compare_count == self.count_of_node_to_mutate):
           new_node = copy.deepcopy(node)
           new_node = self.opposite(new_node)
           return new_node
        else:
            return node



if __name__ == '__main__':
    main()
