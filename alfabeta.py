#!/usr/bin/env python3
# Searches for the Python interpreter in the whole PATH. However, some Unices may not have the env command, so you may need to hardcode /usr/bin/python3 as the interpreter path.
from enum import Enum
from collections import deque

from pprint import pprint

class Player(Enum):
    MAX = 1
    MIN = 2

class Node:
    "Node of the game-state tree"

    def __init__(self, name, player: Player, parent):
        self.name = name
        self.player = player
        self.parent = parent    # for debugging
        self.alpha = float("-Infinity")
        self.beta = float("Infinity")
        self.move_to = None
        self.alfabeta = 0    # alfabeta function result for this node
        self.children = []
        self.child_count = 0
        # self.parent = parent

class TerminalNode(Node):
    "End node containing the game result value"

    def __init__(self, name, player: Player, parent: Node, game_result):
        super(TerminalNode, self).__init__(name, player, parent)
        self.value = game_result
        self.visited = False
        del self.children #, self.child_count ?
        del self.child_count
        del self.move_to
        #todo del player


def alfabeta(node: Node, alpha=float('-inf'), beta=float('inf')):
    if isinstance(node, TerminalNode):
        node.visited = True
        return node.value
    if node.player == Player.MAX:
        node.beta = beta
        node.move_to = node.children[0]
        for child in node.children:
            #alpha = max(alpha, alfabeta(child, alpha, beta))
            ab = alfabeta(child, alpha, beta)
            if ab > alpha:
                node.move_to = child
                alpha = ab
            elif ab > getattr(node.move_to, 'alfabeta', getattr(node.move_to, 'value', 0)):
                node.move_to = child

            node.alpha = alpha
            if alpha >= beta:
                node.alfabeta = beta
                return beta
        node.alfabeta = alpha
        return alpha
    if node.player == Player.MIN:
        node.alpha = alpha
        node.move_to = node.children[0]
        for child in node.children:
            #beta = min(beta, alfabeta(child, alpha, beta))
            ab = alfabeta(child, alpha, beta)
            if ab < beta:
                node.move_to = child
                beta = ab

            node.beta = beta
            if alpha >= beta:
                node.alfabeta = alpha
                return alpha
        node.alfabeta = beta
        return beta

def game_result_generator_left_to_right():
    #yield from (4, 5, 6, 8, 6, 4, 4, 6, 8, 6, 3, 4, 7)
    yield from (4, 5, 3, 4, 6, 8, 1, 2, 3, 4, 4, 7, 5)

def node_child_count_generator_bfs_order():
    yield from (3, 3, 2, 2, "terminals", 2, 1, 3, 2, 2, 2, 1)
    # add 0s for terminal nodes?

def node_name_generator_bfs_order():
    yield from ('S', 
        'SL', 'SM', 'SR', 
        'SLL', 'SLM', 'SLR', 'SML', 'SMR', 'SRL', 'SRR',
        'SLLL', 'SLLR', 'SLML', 'SLRL', 'SLRM', 'SLRR', 'SMLL', 'SMLR', 'SMRL', 'SMRR', 'SRLL', 'SRLR', 'SRRL'
    )

node_name_bfs_order_gen_iter = node_name_generator_bfs_order()

def add_children_nodes(parent: Node, count: int, player: Player):
    for i in range(count):
        parent.children.append(Node(next(node_name_bfs_order_gen_iter), player, parent))
    assert len(parent.children) == count
    parent.child_count = count

def add_terminal_children_nodes(parent: Node, count: int, player: Player):
    for i in range(count):
        parent.children.append(TerminalNode(next(node_name_bfs_order_gen_iter), player, parent, next(add_terminal_children_nodes.game_result_gen_iter)))
    #assert len(parent.children) == count
    parent.child_count = count
add_terminal_children_nodes.game_result_gen_iter = game_result_generator_left_to_right()


def build_sample_game_tree():
    MAX = Player.MAX
    MIN = Player.MIN
    alter_player = lambda player: MAX if player == MIN else MIN

    root = Node(next(node_name_bfs_order_gen_iter), MAX, parent=None)

    nodes_to_visit = [root] # BFS-style
    player = MIN
    children_visited = 0
    parent_node_index = 0
    visited_node_index = 0

    def add_nonterminal_nodes(parent, count, player):
        add_children_nodes(parent, count, player)
        nodes_to_visit.extend(parent.children)  # check closure slots?

    add_children_nodes_op = add_nonterminal_nodes

    root_child_count_gen_iter = node_child_count_generator_bfs_order()
    add_children_nodes_op(root, next(root_child_count_gen_iter), player)
    player = alter_player(player)

    parent = root

    for child_count in root_child_count_gen_iter:
        if child_count == "terminals":
            add_children_nodes_op = add_terminal_children_nodes
            continue

        visited_node_index += 1
        node = nodes_to_visit[visited_node_index]

        add_children_nodes_op(node, child_count, player)
        
        children_visited += 1
        if children_visited == parent.child_count:
            player = alter_player(player)
            parent_node_index += 1
            parent = nodes_to_visit[parent_node_index]
            children_visited = 0

    return root
    

def bfs_traverse(root, op):
    nodes_to_visit = deque([root])
    while len(nodes_to_visit):
        node = nodes_to_visit.popleft()
        if hasattr(node, "children"):
            nodes_to_visit.extend(node.children)
        op(node)


def print_node(node, end='\n'):
    if isinstance(node, TerminalNode):
        print("Terminal node, name = {}, parent = {}, player = {}, value = {}".format(node.name, node.parent.name, node.player, node.value), end=end)
    else:
        print("Node, name = {}, parent = {}, player = {}, child_count = {}".format(node.name, node.parent.name if node.parent else 'None', node.player, node.child_count), end=end)

def print_alfabeta_node(node):
    print_node(node, end='')
    if type(node) is Node:  #hasattr(node, "alfabeta"):
        print(", alfabeta = {}, move = {}, a = {}, b = {}".format(node.alfabeta, node.move_to.name if node.move_to else 'unknown', node.alpha, node.beta))
    elif isinstance(node, TerminalNode):
        print(", visited = {}".format(node.visited))
    else:
        print(", alfabeta not executed, a = {}, b = {}".format(node.alpha, node.beta))


if __name__ == "__main__":
    game_tree_root = build_sample_game_tree()
    bfs_traverse(game_tree_root, print_node)
    alfabeta_result = alfabeta(game_tree_root)
    print("Result:", alfabeta_result)
    bfs_traverse(game_tree_root, print_alfabeta_node)
