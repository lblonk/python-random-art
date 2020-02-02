import ete3

def tree_string(art):
    """
    return a ascii art (string) showing the structure of the expression tree
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
