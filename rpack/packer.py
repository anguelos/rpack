# coding: utf-8

import math

class Rect(object):
    def __init__(self, width, height, rel):
        self.width = width
        self.height = height
        self.rel = rel
        self.x = None
        self.y = None

class Node(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


def align_prev(nodes, node, i):
    prev = prev_node(nodes, node, i)
    if not prev:
        raise ValueError
    nodes.remove(node)

def align_next(nodes, node, i):
    next = next_node(nodes, node, i)
    if not next:
        raise ValueError
    node.y = next.y
    nodes.remove(next)

def next_node(nodes, node, i):
    n = i+1
    if n < len(nodes):
        return nodes[n]

def prev_node(nodes, node, i):
    n = i-1
    if n >= 0:
        return nodes[n]

def node_width(nodes, node, side_len, i):
    next = next_node(nodes, node, i)
    if next: return next.x - node.x
    return side_len - node.x


def apply_left(nodes, node, rect, top, width, rest, i):
    pn = prev_node(nodes, node, i)
    rect.x = node.x
    rect.y = node.y
    node.y += rect.height
    nodes.insert(i+1, Node(node.x+rect.width, rect.y))
    if pn and node.y == pn.y:
        align_prev(nodes, node, i)

def apply_right(nodes, node, rect, top, width, rest, i):
    nn = next_node(nodes, node, i)
    rect.x = node.x + rest
    rect.y = node.y
    new_node = Node(rect.x, rect.y+rect.height)
    nodes.insert(i+1, new_node)
    if nn and new_node.y == nn.y:
        align_next(nodes, new_node, i+1)

def simply_apply(nodes, node, rect, top, width, rest, i):
    pn = prev_node(nodes, node, i)
    nn = next_node(nodes, node, i)
    rect.x = node.x
    rect.y = node.y
    node.y += rect.height
    if nn and node.y == nn.y:
        align_next(nodes, node, i)
    if pn and node.y == pn.y:
        align_prev(nodes, node, i)


def apply_rect(nodes, node, rect, side_len, i):
    pn = prev_node(nodes, node, i)
    nn = next_node(nodes, node, i)
    width = node_width(nodes, node, side_len, i)
    rest = width - rect.width
    top = node.y + rect.height

    #if rest: apply_left(nodes, node, rect, top, width, rest, i)
    #else: simply_apply(nodes, node, rect, top, width, rest, i)
    pos = node.x + width / 2.0
    mid = side_len / 2.0
    if rest and pos > mid:
        apply_right(nodes, node, rect, top, width, rest, i)
    elif rest and pos <= mid:
        apply_left(nodes, node, rect, top, width, rest, i)
    else: simply_apply(nodes, node, rect, top, width, rest, i)

def align(nodes, node, i):
    pn = prev_node(nodes, node, i)
    nn = next_node(nodes, node, i)
    
    if pn and nn:
        if pn.y == nn.y:
            align_next(nodes, node, i)
            align_prev(nodes, node, i)
        elif nn.y < pn.y:
            align_next(nodes, node, i)
        else:
            align_prev(nodes, node, i)
    elif pn:
        align_prev(nodes, node, i)
    elif nn:
        align_next(nodes, node, i)
    else:
        raise ValueError


def get_nodes_compare_func(nodes, side_len):
    def compare_nodes(input):
        i, node = input
        # only node.y allowed atm
        # because align does not check
        # for smaller nn.y and pn.y
        # but it is possible, to make adjustments
        # about wich width to prefer

        #width = node_width(nodes, node, side_len, i)
        #cof = 1.0 / width
        #return node.y+cof # smallest y with biggest with
        #return node.y-cof # smallest y with smallest with
        return node.y # should make series of tests
    return compare_nodes

def rect_cmp1(rect):
    e = rect.width / float(rect.height)
    if rect.width > rect.height:
        e = rect.height / float(rect.width)
    s = 1.0 / (rect.width * rect.height)
    w = 1.0 / rect.width
    return w * e * s

def rect_cmp2(rect):
    e = (rect.width + rect.height) / float(rect.width * rect.height)
    return rect.width * -1.0 + e

def rect_cmp3(rect):
    size = float(rect.width * rect.height)
    e = (2 * rect.width + 2 * rect.height) / size
    s = 1 / size
    return -1.0 * (rect.width - e - s)


def pack(rects, side_len=None, rect_cmp=rect_cmp3):
    if not side_len:
        size = sum(rect.width * rect.height for rect in rects)
        side_len = math.ceil(size ** 0.5)
        aw = sum(rect.width for rect in rects) / float(len(rects))
        rest = side_len % aw
        side_len += int(aw - rest)

    nodes = [Node(0, 0)]
    nodes_cmp = get_nodes_compare_func(nodes, side_len)
    packed = []

    while rects:
        i, node = min(enumerate(nodes), key=nodes_cmp)
        nn = next_node(nodes, node, i)
        
        width = node_width(nodes, node, side_len, i)
        possible = filter(lambda r: width >= r.width, rects)
        
        if not possible: 
            align(nodes, node, i)
            continue

        #rect = min(possible, key=lambda r: width - r.width)
        rect = min(possible, key=rect_cmp)
        rects.remove(rect)
        packed.append(rect)
        apply_rect(nodes, node, rect, side_len, i)
    return packed


def get_enclosing_rect(rects):
    most_right = 0
    most_top = 0
    for rect in rects:
        right = rect.x + rect.width
        top = rect.y + rect.height
        if right > most_right:
            most_right = right
        if top > most_top:
            most_top = top
    return (int(most_right), int(most_top))


def coverage(rects):
    abs_size = sum(rect.width * rect.height for rect in rects)
    most_right, most_top = get_enclosing_rect(rects)
    frame_size = most_right * most_top
    return (abs_size / (frame_size / 100.0)), (most_right, most_top)
