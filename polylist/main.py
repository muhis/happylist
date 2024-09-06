# Run with: python app.py
from dataclasses import dataclass
from polylist.common import mk_list_item_input
from polylist.lists import ListItem, TODO_LIST
from fasthtml.common import (AX, Button, Card, CheckboxX, Div, Footer, Form, Group, Main, H1,
                             Hidden, Input, Li, Titled, Ul, fast_app, Nav, Strong, A, Title,
                             fill_dataclass, fill_form, serve, H3)
from polylist.emoji_from_todo import get_emoji_for_todo
id_curr = 'current-todo'
id_list = 'todo-list'
def tid(id): return f'todo-{id}'


def mk_navigation_bar():
    poly_list_title = Ul(Li(H1("Polylist"), hx_get="/", hx_target="body"))
    add_new_note_button = Li(A(H3("+", cls="contrast"), href="#New", cls="secondary outline"))
    about_button = Li(A(H3("About", href="#")))

    nav_bar_items = Ul(add_new_note_button, about_button)

    nav_bar = Nav(poly_list_title, nav_bar_items)
    return nav_bar


app, rt = fast_app()

@app.get("/")
async def get_todos(req):
    nav_bar = mk_navigation_bar()
    add = Form(Group(mk_list_item_input(), Button("Add")),
               hx_post="/", target_id=id_list, hx_swap="beforeend")
    cards = Card(Ul(*TODO_LIST, id=id_list),
                footer=add)
    
    return Title("Polylist"), Main(nav_bar, cards, cls="container")



@app.post("/")
async def add_item(todo:ListItem):
    todo.id = len(TODO_LIST)+1
    await populate_emojies(todo)
    TODO_LIST.append(todo)
    return todo, mk_list_item_input(hx_swap_oob='true')


async def populate_emojies(todo: ListItem):
    emojies = await get_emoji_for_todo(todo.title)
    todo.title = f"{todo.title} - {emojies}"
    return todo

@app.post("/toggle/{id}")
async def toggle_todo(id: int):
    todo = find_todo(id)
    todo.done = not todo.done
    return todo


def clr_details(): return Div(hx_swap_oob='innerHTML', id=id_curr)
def find_todo(id): return next(o for o in TODO_LIST if o.id==id)

@app.get("/edit/{id}")
async def edit_item(id:int):
    todo = find_todo(id)
    group = Group(
        Input(id="title", name="title", value=todo.title),
        Button("Save", type="Submit")
    ) 
    edit_form = Form(
        group,
        hx_put=f"/update/{id}", 
        hx_target="closest li",
        hx_swap="innerHTML",
    )

    return edit_form


@app.put("/update/{id}")
async def update_item(id: int, todo: ListItem):
    existing_todo = find_todo(id)
    fill_dataclass(todo, existing_todo)
    return existing_todo

@app.put("/")
async def update(todo: ListItem):
    fill_dataclass(todo, find_todo(todo.id))
    return todo, clr_details()

@app.delete("/todos/{id}")
async def del_todo(id:int):
    TODO_LIST.remove(find_todo(id))
    return clr_details()

@app.get("/todos/{id}")
async def get_todo(id:int):
    todo = find_todo(id)
    btn = Button('delete', hx_delete=f'/todos/{todo.id}',
                 target_id=tid(todo.id), hx_swap="outerHTML")
    return Div(Div(todo.title), btn)


if __name__ == '__main__': serve(port=8080)