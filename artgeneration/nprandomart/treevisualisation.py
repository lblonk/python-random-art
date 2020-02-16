"""
functionality to visualise the art object, which is a tree of operators
"""

import ete3
from itertools import chain
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
from math import floor
from ete3 import Tree, NodeStyle

plt.style.use("dark_background")  # because the webapp background is black


def get_tree_with_operator_images(art):
    """
    return an ete3 tree where an image representing the output of an
    operator has been added to each node
    """

    t = Tree()

    def repr(op, node):
        if op.arity == 0:
            ch = node.add_child(name=str(op))
            ch.image = op.img
        else:
            ch = node.add_child(name=str(op))
            ch.image = op.img
            for k, v in vars(op).items():
                if k in ['e', 'e1', 'e2', 'level']:
                    repr(v, ch)

        return node

    t = repr(art, t)

    return t


def plot_tree_with_images(tree):
    """
    This function is modified version of Francois Serra's script:
    https://gist.github.com/fransua/da703c3d2ba121903c0de5e976838b71
    :param tree: ete3 tree
    :return:
    """

    figsize = 25
    fig = plt.figure(figsize=(figsize, figsize))
    number_of_branches = tree.get_farthest_node()[1]
    number_of_leaves = len(list(tree.iter_leaves()))

    plt_xmin, plt_ymin = 0.1, 0.1
    plt_width = 0.07 * number_of_branches  # plt_width =  0.55
    plt_height = 0.04 * number_of_leaves  # plt_height = 0.8

    main_axes = fig.add_axes([plt_xmin, plt_ymin, plt_width, plt_height])

    coords = plot_tree(tree, axes=main_axes)

    xmin, xmax = main_axes.get_xlim()
    ymin, ymax = main_axes.get_ylim()

    for node in coords:
        x, y = coords[node]
        xcax = x
        ycax = y
        xax, yax = to_coord(xcax, ycax, xmin, xmax, ymin, ymax,
                            plt_xmin, plt_ymin, plt_width, plt_height)

        node_axes = fig.add_axes([xax - 0.025, yax - 0.025, 0.05, 0.05])
        node_axes.set_xticks([])
        node_axes.set_yticks([])

        img = np.stack(node.image, axis=2)
        node_axes.imshow(img)  # to show only r/g/b use: imshow(img[:,:,0],cmap='Reds')
        node_axes.text(node_axes.get_xlim()[1] / 2,
                       0.,
                       node.name.replace(')(', ')\n('),
                       size=6, va='bottom', ha='center', c='white')

    return fig


def plot_tree(tree, axes):
    """
    This function is modified version of Francois Serra's script:
    https://gist.github.com/fransua/da703c3d2ba121903c0de5e976838b71

    Plots a ete3.Tree object using matplotlib.
    :param tree: ete Tree object
    :returns: a dictionary of node objects with their coordinates
    """

    def __draw_edge(c, x):
        h = node_pos[c]
        hlinec.append(((x, h), (x + c.dist, h)))
        hlines.append(cstyle)
        return (x + c.dist, h)

    vlinec = []
    vlines = []
    hlinec = []
    hlines = []
    nodes = []
    nodex = []
    nodey = []

    # make lines white
    nstyle = NodeStyle()
    nstyle["hz_line_color"] = "white"
    nstyle["vt_line_color"] = "white"
    for n in tree.traverse():
        n.set_style(nstyle)

    coords = {}
    node_pos = dict((n2, i) for i, n2 in enumerate(tree.get_leaves()[::-1]))
    node_list = tree.iter_descendants(strategy='postorder')
    node_list = chain(node_list, [tree])

    # draw tree
    for n in node_list:
        style = n._get_style()
        x = sum(n2.dist for n2 in n.iter_ancestors()) + n.dist
        if n.is_leaf():
            y = node_pos[n]
        else:
            y = np.mean([node_pos[n2] for n2 in n.children])
            node_pos[n] = y

            # draw vertical line
            vlinec.append(((x, node_pos[n.children[0]]), (x, node_pos[n.children[-1]])))
            vlines.append(style)

            # draw horizontal lines
            for child in n.children:
                cstyle = child._get_style()
                coords[child] = __draw_edge(child, x)
        nodes.append(style)
        nodex.append(x)
        nodey.append(y)

    lstyles = ['-', '--', ':']
    hline_col = LineCollection(hlinec, colors=[l['hz_line_color'] for l in hlines],
                               linestyle=[lstyles[l['hz_line_type']] for l in hlines],
                               linewidth=[(l['hz_line_width'] + 1.) / 2 for l in hlines])
    vline_col = LineCollection(vlinec, colors=[l['vt_line_color'] for l in vlines],
                               linestyle=[lstyles[l['vt_line_type']] for l in vlines],
                               linewidth=[(l['vt_line_width'] + 1.) / 2 for l in vlines])

    axes.add_collection(hline_col)
    axes.add_collection(vline_col)

    # scale line TODO: eliminate this (now still needed to keep spot right size when saving as image)
    xmin, xmax = axes.get_xlim()
    ymin, ymax = axes.get_ylim()
    diffy = ymax - ymin
    dist = round_sig((xmax - xmin) / 5, sig=1)
    ymin -= diffy / 100.
    axes.plot([xmin, xmin + dist], [ymin, ymin], color='k')
    axes.plot([xmin, xmin], [ymin - diffy / 200., ymin + diffy / 200.], color='k')
    axes.plot([xmin + dist, xmin + dist], [ymin - diffy / 200., ymin + diffy / 200.],
              color='k')

    axes.set_axis_off()

    return coords


def round_sig(x, sig=2):
    return round(x, sig - int(floor(np.log10(abs(x)))) - 1)


def to_coord(x, y, xmin, xmax, ymin, ymax, plt_xmin, plt_ymin, plt_width, plt_height):
    x = (x - xmin) / (xmax - xmin) * plt_width + plt_xmin
    y = (y - ymin) / (ymax - ymin) * plt_height + plt_ymin
    return x, y

def tree_as_ascii(art):
    """
    return a ascii art (string) showing the structure of the expression tree (an alternative to plotting)
    :param art:
    :return: str
    """

    t = ete3.Tree()
    img = t.add_child(name="R,G,B = F(X,Y) :")

    def repr(op, t):
        if op.arity == 0:
            t.add_child(name='--'+str(op))
        else:
            ch = t.add_child(name='--'+ str(op))
            for k, v in vars(op).items():
                if k in ['e','e1','e2','level']:
                    repr(v, ch)

    repr(art, img)

    return t.get_ascii(show_internal=True,compact=False)

if __name__ == '__main__':
    from nprandomart import get_art, get_image

    arity = 60
    art = get_art(min_arity=arity, max_arity=arity + 1)
    get_image(art)
    tree = get_tree_with_operator_images(art)
    fig = plot_tree_with_images(tree)
    plt.savefig('fig.png', bbox_inches='tight')
