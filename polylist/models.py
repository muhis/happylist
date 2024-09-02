# models.py
from dataclasses import dataclass
from fasthtml.common import *

@dataclass
class TodoItem():
    title: str
    id: int = -1
    done: bool = False

    def __ft__(self):
        checkbox = Input(type="checkbox", 
                         hx_post=f'/toggle/{self.id}', 
                         hx_trigger="click", 
                         hx_target=f'#{tid(self.id)}',
                         checked=self.done)
        show = AX(self.title, f'/todos/{self.id}', id_curr)
        edit = AX('edit', f'/edit/{self.id}', id_curr)
        return Li(checkbox, ' ', show, ' | ', edit, id=tid(self.id))

TODO_LIST = [TodoItem(id=0, title="Start writing todo list", done=True),
             TodoItem(id=1, title="???", done=False),
             TodoItem(id=2, title="Profit", done=False),
             TodoItem(id=3, title="$$$", done=False)]

def tid(id): return f'todo-{id}'

id_curr = 'current-todo'
id_list = 'todo-list'
