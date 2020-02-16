from nprandomart import generate, get_art, get_image
from nprandomart.randomart import operators, Operator
from pathlib import Path
this_dir = Path(__file__).parent

# core tests
def test_generate():
    art = generate(k=5)
    assert isinstance(art, Operator)
    assert type(art) in operators

def test_randomness():
    art1 = generate(k=100)
    art2 = generate(k=100)
    assert not str(art1) == str(art2)  # admittedly; not a very thorough test of randomness

def test_get_art():
    art = get_art(10,20)
    assert isinstance(art, Operator)


# tree-visualisation tests
from nprandomart.treevisualisation import plot_tree_with_images, tree_as_ascii, get_tree_with_operator_images

def test_ascii():
    art = generate(k=5)
    s = tree_as_ascii(art)
    assert isinstance(s,str)

def test_plot():
    arity = 12
    art = get_art(min_arity=arity, max_arity=arity + 1)
    get_image(art) #so that thumbnails are added
    tree = get_tree_with_operator_images(art)
    fig = plot_tree_with_images(tree)
    # plt.savefig('fig.png', bbox_inches='tight')