# Run with: python app.py
from dataclasses import dataclass
from starlette.background import BackgroundTasks
from fasthtml.common import (AX, Button, Card, CheckboxX, Div, Footer, Form, Group,
                             Hidden, Input, Li, Titled, Ul, fast_app,
                             fill_dataclass, fill_form, serve)
from polylist.emoji_from_todo import get_emoji_for_todo
id_curr = 'current-todo'
id_list = 'todo-list'
def tid(id): return f'todo-{id}'

@dataclass
class TodoItem():
    title: str; id: int = -1; done: bool = False
    def __ft__(self):
        checkbox = CheckboxX(id=f'done-{self.id}', checked=self.done, 
                     hx_post=f'/toggle/{self.id}', 
                     hx_target=f'#{tid(self.id)}',
                     hx_swap='outerHTML')

        show = AX(self.title, f'/todos/{self.id}', id_curr)
        
        edit = AX('edit',     f'/edit/{self.id}' , id_curr)
        return Li(checkbox, show, ' | ', edit, id=tid(self.id))

TODO_LIST = [TodoItem(id=0, title="Start writing todo list", done=True),
             TodoItem(id=1, title="???", done=False),
             TodoItem(id=2, title="Profit", done=False)]

app, rt = fast_app()

def mk_input(**kw): return Input(id="new-title", name="title", placeholder="New Todo", **kw)

@app.get("/")
async def get_todos(req):
    add = Form(Group(mk_input(), Button("Add")),
               hx_post="/", target_id=id_list, hx_swap="beforeend")
    cards = Card(Ul(*TODO_LIST, id=id_list),
                header=add, footer=Div(id=id_curr))
    
    return Titled('Polylist!', cards)

@app.post("/")
async def add_item(todo:TodoItem):
    todo.id = len(TODO_LIST)+1
    await populate_emojies(todo)
    TODO_LIST.append(todo)
    return todo, mk_input(hx_swap_oob='true')


async def populate_emojies(todo: TodoItem):
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
    res = Form(Group(Input(id="title"), Button("Save")),
        Hidden(id="id"), CheckboxX(id="done", label='Done'),
        hx_put="/", target_id=tid(id), id="edit")
    fill_form(res, todo)
    return res

@app.put("/")
async def update(todo: TodoItem):
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


if __name__ == '__main__': serve()