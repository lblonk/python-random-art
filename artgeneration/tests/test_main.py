from nprandomart import generate
from nprandomart.randomart import operators

def test_generate():
    art = generate(k=5)
    assert type(art) in operators

def test_randomness():
    art1 = generate(k=5)
    art2 = generate(k=5)
    assert not str(art1) == str(art2)  # admittedly; not a very thorough test
