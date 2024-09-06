from fasthtml.common import Input

def mk_list_item_input(**kw): return Input(id="new-title", name="title", placeholder="New Todo", **kw)
