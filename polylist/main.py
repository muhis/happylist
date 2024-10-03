# Run with: python app.py
from polylist.common import mk_list_item_input
from polylist.lists import ListItem, PolyList
from fasthtml.common import (AX, Button, Card, CheckboxX, Div, Footer, Form, Group, Main, H1,H2, Aside, Img, P,
                             Hidden, Input, Li, Titled, Ul, fast_app, Nav, Strong, A, Title, Style, Script, Link, Hgroup,
                             fill_dataclass, fill_form, serve, H3)
from polylist.emoji_from_todo import get_emoji_for_todo
from starlette.responses import RedirectResponse
from polylist import logging_backend
id_curr = 'current-todo'
id_list = 'todo-list'
def tid(id): return f'todo-{id}'


def generate_share_script():
    return Script("""
    var reply_click = function (listName) {
        if (navigator.share) {
            navigator.share({
                title: 'Sharing ' + listName + ' On Happyl.ist',
                text: 'I am sharing list ' + listName + ' with you on Happylist, you can now see or edit the list!',
                url: window.location.href
            })
        }
    }
    """)


def mk_navigation_bar():
    polylist_elemet = Li(H2(A("Happyl.ist", href=f"/", cls="contrast")))
    add_new_note_button = Li(A(H3("+", cls="contrast"), href=f"/new", cls="secondary outline"))
    about_button = Li(H3(A("About", href="/about")))

    nav_bar_items = Ul(add_new_note_button, about_button)

    nav_bar = Nav(polylist_elemet, nav_bar_items)
    return nav_bar


app, rt = fast_app()

@app.get("/")
async def index(req):
    new_note = PolyList.new_welcome_note()
    return RedirectResponse(url=f"/list/{new_note.name}")


@app.get("/list/{note_name:str}")
async def get_todos(req, note_name: str):
    share_script = generate_share_script()
    nav_bar = mk_navigation_bar()
    try:
        note = PolyList.get_by_name(note_name)
    except KeyError:
        note = make_404(note_name)

    return Title(f"Happyl.ist: {note_name}"), Main(nav_bar, note, share_script, cls="container")


def make_404(note_name: str):
    return Card(
        H1("404"),
        H2(f"List {note_name} not found, create a new one or"),
        A("Go back to home", href="/"),
    )

@app.get("/new")
async def new_list(req):
    note = PolyList.new()
    return RedirectResponse(url=f"/list/{note.name}")


@app.get("/about")
async def about(req):
    happy_list = PolyList.new_about_note()
    return RedirectResponse(url=f"/list/{happy_list.name}")

@app.post("/list/{name}")
async def add_item(title:str, name:str):
    poly_list = PolyList.get_by_name(name)
    _, id = poly_list.add_item(title=title)
    rendered_list_item = poly_list.render_item(id)
    poly_list.schedule_updating_emojies(id)
    return rendered_list_item, mk_list_item_input(hx_swap_oob='true')


async def populate_emojies(todo: ListItem):
    emojies = await get_emoji_for_todo(todo.title)
    todo.title = f"{todo.title} - {emojies}"
    return todo

@app.post("/list/{name}/toggle/{id}")
async def toggle_todo(name:str, id: int):
    poly_list = PolyList.get_by_name(name)
    poly_list.toggle_item(id)
    return poly_list.render_item(id)


@app.get("/list/{name}/edit/{id}")
async def edit_item(name:str, id:int):
    polylist = PolyList.get_by_name(name)
    list_item = polylist.get_item_by_id(id)

    group = Group(
        Input(id="title", name="title", value=list_item.title),
        Button("Save", type="Submit")
    ) 
    edit_form = Form(
        group,
        hx_put=f"/list/{name}/update/{id}", 
        hx_target="closest li",
        hx_swap="innerHTML",
    )

    return edit_form


@app.put("/list/{name}/update/{id}")
async def update_item(name: str, id: int, title: str):
    poly_list = PolyList.get_by_name(name)
    poly_list.update_item(id, title)
    return poly_list.render_item(id)


if __name__ == '__main__': serve(port=8080)