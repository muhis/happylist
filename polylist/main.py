# Run with: python app.py
from dataclasses import dataclass
from polylist.common import mk_list_item_input
from polylist.lists import ListItem, TODO_LIST, PolyList
from fasthtml.common import (AX, Button, Card, CheckboxX, Div, Footer, Form, Group, Main, H1,H2, Aside, Img,
                             Hidden, Input, Li, Titled, Ul, fast_app, Nav, Strong, A, Title, Style, Script, Link,
                             fill_dataclass, fill_form, serve, H3)
from starlette.staticfiles import StaticFiles
from polylist.emoji_from_todo import get_emoji_for_todo
import randomname

id_curr = 'current-todo'
id_list = 'todo-list'
def tid(id): return f'todo-{id}'


def generate_share_script():
    return Script("""
    var reply_click = function (listName) {
        if (navigator.share) {
            navigator.share({
                title: listName,
                text: listName + '@Polylist',
                url: window.location.href
            })
        }
    }
    """)


def mk_navigation_bar(note_name: str):
    polylist_elemet = H2("Polylist/")
    share_button = Img(
        src="polylist/static/share-android.svg",
        alt="Share",
        cls="share-svg",
        onclick=f"reply_click('{note_name}')",
        role="button",
    )
    note_name_element = H3(f"{note_name} ", share_button)
    note_title_element = Aside(polylist_elemet, note_name_element)
    
    poly_list_title = Ul(Li(H3(f"{note_name}")), Li(H2("@Polylist"), hx_get="/", hx_target="body"))
    add_new_note_button = Li(A(H3("+", cls="contrast"), href=f"/{randomname.generate()}", cls="secondary outline"))
    about_button = Li(A(H3("About", href="#")))

    nav_bar_items = Ul(add_new_note_button, about_button)

    nav_bar = Nav(note_title_element, nav_bar_items)
    return nav_bar


app, rt = fast_app()
app.mount("/static", StaticFiles(directory="polylist/static"), name="static")


@app.get("/{note_name:str}")
async def get_todos(req, note_name: str):
    share_script = generate_share_script()
    nav_bar = mk_navigation_bar(note_name=note_name)
    
    poly_list = PolyList.get_by_name(note_name)
    
    return Title("Polylist"), Main(nav_bar, poly_list, share_script, cls="container")



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